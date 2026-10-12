import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "firebase/auth";
import {
  doc,
  getDoc,
  onSnapshot,
  serverTimestamp,
  setDoc,
  type Unsubscribe,
} from "firebase/firestore";
import {
  useAppStore,
  type DailyStat,
  type LastStudied,
  type QuizRecord,
  type StudyEntry,
} from "../stores/useAppStore";
import { useAuthStore } from "../stores/useAuthStore";
import { isAdminEmail } from "./admin";
import { firebase } from "./firebase";
import { storage } from "./storage";

/**
 * 학습 기록 클라우드 동기화 (Firestore: users/{uid}).
 *
 * 규칙
 * - 학습 기록(외운 단어·단어장·퀴즈·일별 집계·이어하기·이름)만 올린다.
 *   소리 크기·자동 넘김 같은 기기 설정은 기기마다 따로 둔다.
 * - 로그인하면 한 번 맞춘다. 이 기기에서 같은 계정으로 이미 맞춘 적이 있고
 *   그 뒤로 기기에서 바뀐 게 없으면 클라우드 쪽을 그대로 받는다.
 *   처음 로그인했거나 로그아웃 중에 공부한 기록이 있으면 둘을 합친다.
 * - 그 뒤로는 바뀔 때마다 잠시 모아서 올리고, 다른 기기가 올린 것은 바로 받는다.
 *   동시에 고치면 나중에 올린 쪽이 이긴다.
 * - 기록은 JSON 문자열 하나로 담는다. 단어 수천 개를 맵으로 펼치면
 *   Firestore 문서당 색인 항목 한도에 걸릴 수 있다.
 */

/** 클라우드에 올리는 학습 기록 */
interface SyncedData {
  entries: Record<string, StudyEntry>;
  saved: Record<string, string>;
  lastStudied: LastStudied | null;
  dailyLog: Record<string, DailyStat>;
  nickname: string;
  quizRecords: Record<string, QuizRecord>;
}

const SYNCED_KEYS = [
  "entries",
  "saved",
  "lastStudied",
  "dailyLog",
  "nickname",
  "quizRecords",
] as const satisfies readonly (keyof SyncedData)[];

/** 기기에 남겨 두는 동기화 메모 */
interface SyncMeta {
  /** 마지막으로 맞춘 계정 */
  uid: string | null;
  /** 그 뒤로 기기에서 바뀌었지만 아직 못 올린 게 있는지 */
  dirty: boolean;
}

const META_KEY = "wordpic-cloud-meta";
const PUSH_DELAY_MS = 1500;
const DAILY_LOG_KEEP_DAYS = 60;

let meta: SyncMeta = { uid: null, dirty: false };
/** 지금 맞추고 있는 계정. 첫 맞춤이 끝나야 채워진다 */
let activeUid: string | null = null;
/** 마지막으로 올리거나 받은 내용. 같은 내용을 다시 올리거나 받지 않으려고 쓴다 */
let lastPayload = "";
/** 기기에서 바뀐 횟수. 올리는 사이에 또 바뀌었는지 가려낸다 */
let changeSeq = 0;
let applyingRemote = false;
let pushTimer: ReturnType<typeof setTimeout> | null = null;
let unsubDoc: Unsubscribe | null = null;

function pick(s: SyncedData): SyncedData {
  return {
    entries: s.entries,
    saved: s.saved,
    lastStudied: s.lastStudied,
    dailyLog: s.dailyLog,
    nickname: s.nickname,
    quizRecords: s.quizRecords,
  };
}

/** 클라우드에서 받은 값이 망가져 있어도 앱이 죽지 않게 빈 값으로 채운다 */
function parse(payload: unknown): SyncedData | null {
  if (typeof payload !== "string") return null;
  try {
    const d = JSON.parse(payload) as Partial<SyncedData>;
    return {
      entries: d.entries ?? {},
      saved: d.saved ?? {},
      lastStudied: d.lastStudied ?? null,
      dailyLog: d.dailyLog ?? {},
      nickname: d.nickname ?? "",
      quizRecords: d.quizRecords ?? {},
    };
  } catch {
    return null;
  }
}

const newer = <T extends { updatedAt: string }>(a?: T | null, b?: T | null) =>
  !a ? b : !b ? a : a.updatedAt >= b.updatedAt ? a : b;

/** 두 기록을 합친다. 단어마다 나중에 판정한 쪽, 숫자는 큰 쪽을 남긴다 */
function merge(local: SyncedData, remote: SyncedData): SyncedData {
  const entries: Record<string, StudyEntry> = { ...remote.entries };
  for (const [id, e] of Object.entries(local.entries)) {
    entries[id] = newer(e, entries[id])!;
  }

  const saved: Record<string, string> = { ...remote.saved };
  for (const [id, at] of Object.entries(local.saved)) {
    if (!saved[id] || at > saved[id]) saved[id] = at;
  }

  const days: Record<string, DailyStat> = { ...remote.dailyLog };
  for (const [day, d] of Object.entries(local.dailyLog)) {
    const r = days[day];
    days[day] = r
      ? { seen: Math.max(d.seen, r.seen), known: Math.max(d.known, r.known) }
      : d;
  }
  const dailyLog: Record<string, DailyStat> = {};
  for (const k of Object.keys(days).sort().slice(-DAILY_LOG_KEEP_DAYS)) {
    dailyLog[k] = days[k];
  }

  const quizRecords: Record<string, QuizRecord> = { ...remote.quizRecords };
  for (const [id, q] of Object.entries(local.quizRecords)) {
    const r = quizRecords[id];
    quizRecords[id] = r
      ? {
          best: Math.max(q.best, r.best),
          bestCombo: Math.max(q.bestCombo, r.bestCombo),
          plays: Math.max(q.plays, r.plays),
          updatedAt: q.updatedAt > r.updatedAt ? q.updatedAt : r.updatedAt,
        }
      : q;
  }

  return {
    entries,
    saved,
    lastStudied: newer(local.lastStudied, remote.lastStudied) ?? null,
    dailyLog,
    nickname: local.nickname || remote.nickname,
    quizRecords,
  };
}

function saveMeta(next: SyncMeta) {
  meta = next;
  void storage.set(META_KEY, next);
}

/** 클라우드 값을 기기에 넣는다. 이때 생기는 변경은 다시 올리지 않는다 */
function applyLocal(data: SyncedData) {
  applyingRemote = true;
  try {
    useAppStore.setState(data);
  } finally {
    applyingRemote = false;
  }
}

async function push(uid: string, data: SyncedData) {
  const fb = firebase();
  if (!fb) return;
  const payload = JSON.stringify(data);
  if (payload === lastPayload && !meta.dirty) return;

  const seq = changeSeq;
  useAuthStore.setState({ sync: "syncing" });
  try {
    await setDoc(doc(fb.db, "users", uid), {
      payload,
      schema: 1,
      updatedAt: serverTimestamp(),
    });
    lastPayload = payload;
    // 올리는 사이에 또 바뀌었으면 아직 덜 올린 상태로 둔다
    saveMeta({ uid, dirty: seq !== changeSeq });
    useAuthStore.setState({ sync: "synced" });
  } catch (e) {
    console.warn("[cloudSync] 올리기 실패", e);
    useAuthStore.setState({ sync: "error" });
  }
}

function schedulePush() {
  if (!activeUid) return;
  if (pushTimer) clearTimeout(pushTimer);
  pushTimer = setTimeout(() => {
    pushTimer = null;
    if (activeUid) void push(activeUid, pick(useAppStore.getState()));
  }, PUSH_DELAY_MS);
}

/** 모아 둔 변경을 바로 올린다 (탭을 닫거나 로그아웃할 때) */
async function flush() {
  if (!pushTimer || !activeUid) return;
  clearTimeout(pushTimer);
  pushTimer = null;
  await push(activeUid, pick(useAppStore.getState()));
}

function waitHydrated(): Promise<void> {
  if (useAppStore.getState().hydrated) return Promise.resolve();
  return new Promise((resolve) => {
    const unsub = useAppStore.subscribe((s) => {
      if (s.hydrated) {
        unsub();
        resolve();
      }
    });
  });
}

async function startAccount(uid: string) {
  const fb = firebase();
  if (!fb) return;
  const ref = doc(fb.db, "users", uid);

  const snap = await getDoc(ref);
  const local = pick(useAppStore.getState());
  const remote = snap.exists() ? parse(snap.get("payload")) : null;

  let next = local;
  if (remote) {
    const cleanSameAccount = meta.uid === uid && !meta.dirty;
    next = cleanSameAccount ? remote : merge(local, remote);
    lastPayload = JSON.stringify(remote);
  }
  applyLocal(next);
  activeUid = uid;
  // 합친 결과가 클라우드와 다르면 올린다 (같으면 push 가 알아서 건너뛴다)
  if (meta.uid !== uid) saveMeta({ uid, dirty: true });
  await push(uid, next);

  // 다른 기기가 올린 기록을 바로 받는다
  unsubDoc = onSnapshot(ref, (s) => {
    if (s.metadata.hasPendingWrites || !s.exists()) return;
    const payload = s.get("payload");
    if (payload === lastPayload) return;
    const data = parse(payload);
    if (!data) return;
    lastPayload = payload;
    if (pushTimer) {
      // 이 기기에도 아직 못 올린 변경이 있으면 합쳐서 다시 올린다
      applyLocal(merge(pick(useAppStore.getState()), data));
      schedulePush();
    } else {
      applyLocal(data);
    }
  });
}

function stopAccount() {
  if (pushTimer) clearTimeout(pushTimer);
  pushTimer = null;
  unsubDoc?.();
  unsubDoc = null;
  activeUid = null;
  lastPayload = "";
}

/**
 * 앱이 뜰 때 한 번 부른다. 로그인 상태를 지켜보다가 동기화를 켜고 끈다.
 * 클라우드를 쓸 수 없는 환경(네이티브, SSR)에서는 아무것도 하지 않는다.
 */
export function startCloudSync(): () => void {
  const fb = firebase();
  if (!fb) {
    useAuthStore.setState({ checking: false });
    return () => {};
  }

  let disposed = false;
  const metaReady = storage.get<SyncMeta>(META_KEY).then((m) => {
    if (m) meta = m;
  });

  // 로그인 여부와 상관없이 기기에서 바뀐 것은 표시해 둔다
  const unsubStore = useAppStore.subscribe((s, prev) => {
    if (applyingRemote || !s.hydrated || !prev.hydrated) return;
    if (!SYNCED_KEYS.some((k) => s[k] !== prev[k])) return;
    changeSeq += 1;
    if (!meta.dirty) saveMeta({ ...meta, dirty: true });
    schedulePush();
  });

  const unsubAuth = onAuthStateChanged(fb.auth, async (user) => {
    stopAccount();
    if (!user) {
      useAuthStore.setState({
        checking: false,
        user: null,
        isAdmin: false,
        adminChecking: false,
        sync: "off",
      });
      return;
    }
    useAuthStore.setState({
      checking: false,
      user: { uid: user.uid, email: user.email, name: user.displayName },
      isAdmin: false,
      adminChecking: true,
      sync: "syncing",
    });
    void isAdminEmail(user.email).then((isAdmin) => {
      if (fb.auth.currentUser?.uid === user.uid) {
        useAuthStore.setState({ isAdmin, adminChecking: false });
      }
    });
    try {
      await Promise.all([waitHydrated(), metaReady]);
      if (disposed || fb.auth.currentUser?.uid !== user.uid) return;
      await startAccount(user.uid);
    } catch (e) {
      console.warn("[cloudSync] 동기화 시작 실패", e);
      useAuthStore.setState({ sync: "error" });
    }
  });

  const onHide = () => {
    if (document.visibilityState === "hidden") void flush();
  };
  document.addEventListener("visibilitychange", onHide);

  return () => {
    disposed = true;
    unsubStore();
    unsubAuth();
    stopAccount();
    document.removeEventListener("visibilitychange", onHide);
  };
}

/** 구글 계정으로 로그인한다 (팝업) */
export async function signInWithGoogle() {
  const fb = firebase();
  if (!fb) return;
  await signInWithPopup(fb.auth, new GoogleAuthProvider());
}

/** 로그아웃한다. 기기의 기록은 그대로 둔다 */
export async function signOutCloud() {
  const fb = firebase();
  if (!fb) return;
  await flush();
  await signOut(fb.auth);
}
