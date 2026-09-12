import { getLocales } from "expo-localization";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { StudyLangId } from "../constants/languages";
import { STUDY_LANGS } from "../constants/languages";
import { UI_LANGS, type UiLangId } from "../i18n/strings";
import { persistStorage } from "../lib/storage";

/** 기기 언어로 표시 언어를 정한다. 지원하지 않는 말이면 한국어로 시작한다 */
function deviceUiLang(): UiLangId {
  try {
    const code = getLocales()[0]?.languageCode ?? "";
    return (UI_LANGS as readonly string[]).includes(code)
      ? (code as UiLangId)
      : "ko";
  } catch {
    return "ko";
  }
}

/** 예전 기록의 단어 id 에는 학습 언어가 없었다 (m1-1). 영어로 보고 앞에 붙인다 */
function withLangPrefix(wordId: string): string {
  const head = wordId.split("-")[0];
  return (STUDY_LANGS as readonly string[]).includes(head)
    ? wordId
    : `en-${wordId}`;
}

/** 단어별 학습 상태: 미학습 / 헷갈림 / 외움 */
export type WordStatus = "unseen" | "unsure" | "known";

/** 숙련도 별(3개 중 채워진 수) */
export const STARS_BY_STATUS: Record<WordStatus, number> = {
  unseen: 0,
  unsure: 1,
  known: 3,
};

/** 단어 하나의 학습 기록 */
export interface StudyEntry {
  status: WordStatus;
  /** 마지막으로 판정한 시각 (ISO). 나중에 복습 주기를 계산할 때 쓴다 */
  updatedAt: string;
}

/** 이어하기 지점 */
export interface LastStudied {
  wordId: string;
  gradeId: string;
  updatedAt: string;
}

/** 하루치 집계 */
export interface DailyStat {
  /** 오늘 학습 화면에서 본 단어 수 */
  seen: number;
  /** 오늘 "외웠어요"로 판정한 단어 수 */
  known: number;
}

/** 일별 기록 보관 기간. 스트릭 계산에 필요한 만큼만 남긴다 */
const DAILY_LOG_KEEP_DAYS = 60;

/** 기기 로컬 자정 기준 날짜 키 (YYYY-MM-DD) */
export function dateKey(d: Date = new Date()): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** 오래된 일별 기록을 잘라낸다 */
function trimDailyLog(
  log: Record<string, DailyStat>,
): Record<string, DailyStat> {
  const keys = Object.keys(log).sort();
  if (keys.length <= DAILY_LOG_KEEP_DAYS) return log;
  const next: Record<string, DailyStat> = {};
  for (const k of keys.slice(-DAILY_LOG_KEEP_DAYS)) next[k] = log[k];
  return next;
}

interface AppState {
  /** 저장소에서 값을 다 읽어왔는지. 읽기 전에 빈 화면을 보여주지 않으려고 쓴다 */
  hydrated: boolean;

  /** 앱 화면에 쓰는 말 */
  uiLang: UiLangId;
  setUiLang: (id: UiLangId) => void;

  /** 지금 배우고 있는 말 */
  studyLang: StudyLangId;
  setStudyLang: (id: StudyLangId) => void;

  /** 현재 선택된 학년 ID */
  activeGradeId: string | null;
  setActiveGradeId: (id: string | null) => void;

  /** 자동 넘김 사용 여부 (학습 화면 전역 설정) */
  autoAdvance: boolean;
  setAutoAdvance: (on: boolean) => void;

  /** 발음 소리 크기 (0 = 음소거 … 1 = 최대). 학습 화면 스피커에 쓴다 */
  speechVolume: number;
  setSpeechVolume: (v: number) => void;

  /** 단어 id → 학습 기록 */
  entries: Record<string, StudyEntry>;
  /**
   * 단어장에 따로 담아 둔 단어. 단어 id → 담은 시각(ISO).
   * 외웠는지 헷갈리는지와는 별개다. 학습 화면에서 "저장"을 누르면 담기고,
   * 다시 누르면 빠진다.
   */
  saved: Record<string, string>;
  /** 마지막으로 본 단어 (이어하기 지점) */
  lastStudied: LastStudied | null;
  /** 날짜별 집계 */
  dailyLog: Record<string, DailyStat>;
  /** 사용자가 정한 이름 (설정 화면에서 변경) */
  nickname: string;

  /**
   * 학습 화면에 단어가 떴을 때 호출한다.
   * 이어하기 지점을 갱신하고 "오늘 본 단어"를 센다.
   * 판정 버튼이 아니라 화면 진입 시점이어야 자동 넘김으로 지나간 단어도 집계된다.
   */
  markSeen: (wordId: string, gradeId: string) => void;

  /** "외웠어요 / 헷갈려요" 판정. 기록과 일별 집계를 한 번에 갱신한다 */
  recordStudy: (wordId: string, status: WordStatus) => void;

  /** 단어장에 담거나 뺀다 */
  toggleSaved: (wordId: string) => void;

  setNickname: (name: string) => void;
  /** 학습 기록 전체 삭제 (설정 화면) */
  resetProgress: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      hydrated: false,

      uiLang: deviceUiLang(),
      setUiLang: (id) => set({ uiLang: id }),

      studyLang: "en",
      // 학습 언어를 바꾸면 보고 있던 코스도 비운다. 단계 id 가 언어마다 다르다
      setStudyLang: (id) => set({ studyLang: id, activeGradeId: null }),

      activeGradeId: null,
      setActiveGradeId: (id) => set({ activeGradeId: id }),

      autoAdvance: true,
      setAutoAdvance: (on) => set({ autoAdvance: on }),

      speechVolume: 1,
      // 0~1 을 벗어난 값이 들어와도 저장소가 망가지지 않게 잘라 둔다
      setSpeechVolume: (v) =>
        set({ speechVolume: Math.min(1, Math.max(0, v)) }),

      entries: {},
      saved: {},
      lastStudied: null,
      dailyLog: {},
      nickname: "",

      markSeen: (wordId, gradeId) =>
        set((s) => {
          const today = dateKey();
          // 같은 단어를 오늘 이미 봤다면 "오늘 본 단어"를 중복해서 세지 않는다
          const sameWordToday =
            s.lastStudied?.wordId === wordId &&
            s.lastStudied.updatedAt.slice(0, 10) === today;
          const prev = s.dailyLog[today] ?? { seen: 0, known: 0 };

          return {
            lastStudied: {
              wordId,
              gradeId,
              updatedAt: new Date().toISOString(),
            },
            dailyLog: sameWordToday
              ? s.dailyLog
              : trimDailyLog({
                  ...s.dailyLog,
                  [today]: { ...prev, seen: prev.seen + 1 },
                }),
          };
        }),

      recordStudy: (wordId, status) =>
        set((s) => {
          const today = dateKey();
          const prev = s.dailyLog[today] ?? { seen: 0, known: 0 };
          // 이미 외운 단어를 또 외웠다고 눌러도 오늘 개수는 한 번만 는다
          const wasKnown = s.entries[wordId]?.status === "known";
          const knownDelta = status === "known" && !wasKnown ? 1 : 0;

          return {
            entries: {
              ...s.entries,
              [wordId]: { status, updatedAt: new Date().toISOString() },
            },
            dailyLog: trimDailyLog({
              ...s.dailyLog,
              [today]: { ...prev, known: prev.known + knownDelta },
            }),
          };
        }),

      toggleSaved: (wordId) =>
        set((s) => {
          const next = { ...s.saved };
          if (next[wordId]) delete next[wordId];
          else next[wordId] = new Date().toISOString();
          return { saved: next };
        }),

      setNickname: (name) => set({ nickname: name }),

      resetProgress: () =>
        set({ entries: {}, saved: {}, lastStudied: null, dailyLog: {} }),
    }),
    {
      name: "wordpic-store",
      version: 2,
      // 네이티브는 디스크, 웹은 localStorage — 화면 이동·뒤로가기·앱 재시작에도 유지된다.
      // Node(SSR)에서는 빈 저장소로 떨어져 window 참조로 죽지 않는다
      storage: createJSONStorage(() => persistStorage),
      // hydrated는 저장하지 않는다. 매 실행마다 false에서 시작해야 한다
      partialize: (s) => ({
        uiLang: s.uiLang,
        studyLang: s.studyLang,
        autoAdvance: s.autoAdvance,
        speechVolume: s.speechVolume,
        activeGradeId: s.activeGradeId,
        entries: s.entries,
        saved: s.saved,
        lastStudied: s.lastStudied,
        dailyLog: s.dailyLog,
        nickname: s.nickname,
      }),
      // 다국어로 넘어오면서 단어 id 앞에 학습 언어가 붙었다 (m1-1 → en-m1-1).
      // 예전에 저장된 기록도 같은 규칙으로 바꿔 줘야 학습 내역이 살아남는다.
      migrate: (persisted, version) => {
        const state = persisted as Partial<AppState>;
        if (version >= 2) return state;

        if (state.entries) {
          const moved: Record<string, StudyEntry> = {};
          for (const [wordId, entry] of Object.entries(state.entries)) {
            moved[withLangPrefix(wordId)] = entry;
          }
          state.entries = moved;
        }
        if (state.lastStudied?.wordId) {
          state.lastStudied = {
            ...state.lastStudied,
            wordId: withLangPrefix(state.lastStudied.wordId),
          };
        }
        state.uiLang = state.uiLang ?? deviceUiLang();
        state.studyLang = state.studyLang ?? "en";
        return state;
      },
      onRehydrateStorage: () => () => {
        useAppStore.setState({ hydrated: true });
      },
    },
  ),
);
