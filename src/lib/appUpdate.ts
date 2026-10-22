import Constants from "expo-constants";
import { File, Paths } from "expo-file-system";
import { startActivityAsync } from "expo-intent-launcher";
import { Platform } from "react-native";
import { create } from "zustand";

/**
 * 안드로이드 앱 업데이트 (GitHub 릴리즈).
 *
 * 앱은 스토어 없이 APK 로 나눠 주므로, GitHub 저장소의 최신 릴리즈를 보고
 * 지금 버전보다 새것이면 앱 안에서 APK 를 내려받아 바로 설치 화면을 연다.
 * 브라우저를 거치지 않는다. 스토어 밖에서 받은 앱이라 마지막 "설치" 확인은
 * 안드로이드가 직접 묻고, 처음 한 번은 "이 앱에서 설치 허용"도 켜야 한다.
 *
 * 릴리즈 태그는 `v1.2.0` 처럼 app.json 의 version 앞에 v 를 붙여 만든다.
 * 웹은 main 에 올릴 때마다 Vercel 이 새로 배포하니 확인할 게 없다.
 */
const LATEST_RELEASE_URL =
  "https://api.github.com/repos/lebass98/English_word/releases/latest";

const APK_MIME = "application/vnd.android.package-archive";
/** 받은 파일을 설치 앱이 읽을 수 있게 하는 권한 (Intent.FLAG_GRANT_READ_URI_PERMISSION) */
const FLAG_GRANT_READ_URI_PERMISSION = 1;

/** 이 기기에서 업데이트를 확인할 수 있는지 */
export const updateAvailable = Platform.OS === "android";

/** 지금 설치된 앱 버전 (app.json 의 version) */
export const currentVersion = Constants.expoConfig?.version ?? "0.0.0";

export interface LatestRelease {
  version: string;
  /** 릴리즈에 붙은 APK 주소. 없으면 null */
  apkUrl: string | null;
  /** APK 크기 (바이트). 진행률 계산에 쓴다 */
  apkSize: number;
  notes: string;
}

/** "v1.10.0" 과 "1.9.2" 처럼 점으로 나뉜 버전을 숫자로 비교한다 */
export function isNewer(latest: string, current: string): boolean {
  const parse = (v: string) =>
    v
      .replace(/^v/i, "")
      .split(".")
      .map((n) => parseInt(n, 10) || 0);
  const a = parse(latest);
  const b = parse(current);
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const diff = (a[i] ?? 0) - (b[i] ?? 0);
    if (diff !== 0) return diff > 0;
  }
  return false;
}

/** 최신 릴리즈를 가져온다. 릴리즈가 없거나 인터넷이 안 되면 null */
export async function fetchLatestRelease(): Promise<LatestRelease | null> {
  try {
    const res = await fetch(LATEST_RELEASE_URL, {
      headers: { Accept: "application/vnd.github+json" },
    });
    if (!res.ok) return null;
    const data = (await res.json()) as {
      tag_name?: string;
      body?: string;
      assets?: { name: string; size: number; browser_download_url: string }[];
    };
    if (!data.tag_name) return null;
    const apk = data.assets?.find((a) => a.name.endsWith(".apk"));
    return {
      version: data.tag_name.replace(/^v/i, ""),
      apkUrl: apk?.browser_download_url ?? null,
      apkSize: apk?.size ?? 0,
      notes: data.body ?? "",
    };
  } catch {
    return null;
  }
}

/**
 * 업데이트 진행 단계.
 * - idle: 아직 확인 전
 * - checking: 확인 중
 * - latest: 최신 버전
 * - available: 새 버전이 있다
 * - downloading: 앱 안에서 내려받는 중 (progress 0~1)
 * - ready: 다 받아서 설치 화면을 열었다
 * - error: 확인·내려받기·설치 화면 열기 중 하나가 실패했다
 */
export type UpdatePhase =
  | "idle"
  | "checking"
  | "latest"
  | "available"
  | "downloading"
  | "ready"
  | "error";

interface UpdateState {
  phase: UpdatePhase;
  release: LatestRelease | null;
  progress: number;
  /** 업데이트 창을 띄울지. "나중에"를 누르면 닫히고 설정 칸에서 다시 열 수 있다 */
  open: boolean;
}

export const useUpdateStore = create<UpdateState>()(() => ({
  phase: "idle",
  release: null,
  progress: 0,
  open: false,
}));

const set = useUpdateStore.setState;
const get = useUpdateStore.getState;

/** 다 받은 APK. 설치 화면을 다시 열 때 또 받지 않으려고 둔다 */
let downloaded: File | null = null;

/**
 * 새 버전이 있는지 확인한다.
 * quiet 이면 (앱을 켤 때) 새 버전이 있을 때만 창을 띄우고, 실패는 조용히 넘어간다.
 */
export async function checkForUpdate({ quiet = false } = {}) {
  if (!updateAvailable) return;
  const { phase } = get();
  if (phase === "checking" || phase === "downloading") return;
  set({ phase: "checking" });
  const latest = await fetchLatestRelease();
  if (!latest) {
    set({ phase: quiet ? "idle" : "error", open: false });
    return;
  }
  if (!isNewer(latest.version, currentVersion) || !latest.apkUrl) {
    set({ phase: "latest", release: latest, open: false });
    return;
  }
  set({ phase: "available", release: latest, progress: 0, open: true });
}

/** 받은 APK 로 안드로이드 설치 화면을 연다 */
async function openInstaller(file: File) {
  await startActivityAsync("android.intent.action.VIEW", {
    data: file.contentUri,
    type: APK_MIME,
    flags: FLAG_GRANT_READ_URI_PERMISSION,
  });
}

/** 앱 안에서 APK 를 내려받고, 다 받으면 바로 설치 화면을 연다 */
export async function downloadAndInstall() {
  const { release, phase } = get();
  if (!release?.apkUrl || phase === "downloading") return;
  set({ phase: "downloading", progress: 0, open: true });
  try {
    const file = new File(Paths.cache, `WordPic-${release.version}.apk`);
    // 전에 받다 만 파일이 남아 있으면 지우고 새로 받는다
    if (file.exists) file.delete();
    const task = File.createDownloadTask(release.apkUrl, file, {
      onProgress: ({ bytesWritten, totalBytes }) => {
        const total = totalBytes > 0 ? totalBytes : release.apkSize;
        if (total > 0) set({ progress: Math.min(1, bytesWritten / total) });
      },
    });
    const result = await task.downloadAsync();
    if (!result) throw new Error("download cancelled");
    downloaded = result;
    set({ phase: "ready", progress: 1 });
    await openInstaller(result);
  } catch (e) {
    console.warn("[appUpdate]", e);
    set({ phase: "error" });
  }
}

/** 설치 화면을 닫아 버렸을 때 다시 연다. 받은 파일이 없으면 다시 받는다 */
export async function reopenInstaller() {
  if (!downloaded?.exists) return downloadAndInstall();
  try {
    await openInstaller(downloaded);
  } catch (e) {
    console.warn("[appUpdate]", e);
    set({ phase: "error" });
  }
}

/** 업데이트 창을 연다·닫는다. 받는 중에 닫아도 내려받기는 계속된다 */
export function setUpdateDialogOpen(open: boolean) {
  set({ open });
}
