import { useEffect, useState } from "react";
import {
  REPLACED_IMAGES,
  keyOfImageSlug,
  type ReplacedImage,
} from "../constants/wordImages";
import replacedData from "../data/images/replaced.json";
import { storage } from "./storage";

/**
 * 그림 저장소(GitHub)에서 교체 기록을 바로 읽어 온다. 현황 화면 전용.
 *
 * 앱에 든 교체 기록(replaced.json)은 scripts/image_replacements.py 를 돌려야
 * 바뀐다. 그림을 교체하고 이 스크립트를 깜빡하면 현황 화면에 "교체됨"이
 * 붙지 않으므로, 화면을 열 때마다 저장소의 커밋 기록을 직접 훑는다.
 *
 * GitHub API 는 로그인 없이 시간당 60번까지만 받아 준다. 커밋 내용은 한 번
 * 올라가면 바뀌지 않으므로 커밋마다 읽은 결과를 저장해 두고, 새 커밋만 읽는다.
 * 그래서 화면을 열 때 보통 목록 한 번만 부른다.
 */

const API = "https://api.github.com/repos/lebass98/word-images";
const CACHE_PREFIX = "imageStatus.commit.";
const LAST_KEY = "imageStatus.liveReplaced";

/** 커밋 하나에서 그림 파일만 추린 것 */
interface CommitFiles {
  /** 커밋한 날 (기기 시간대 기준 YYYY-MM-DD) */
  date: string;
  /** 내용을 바꾼(교체한) 그림 파일 */
  modified: string[];
}

export interface LiveReplaced {
  /** 앱에 든 기록과 저장소에서 읽은 기록을 합친 것 */
  map: Record<string, ReplacedImage>;
  /** loading: 확인 중 · live: 저장소에서 확인함 · saved: 확인 못 해 이전 결과를 씀 */
  status: "loading" | "live" | "saved";
  /** 마지막으로 확인한 시각 (YYYY-MM-DD HH:MM) */
  checkedAt: string;
}

function stamp(d: Date, withTime = false) {
  const p = (n: number) => String(n).padStart(2, "0");
  const day = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  return withTime ? `${day} ${p(d.getHours())}:${p(d.getMinutes())}` : day;
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, {
    headers: { Accept: "application/vnd.github+json" },
  });
  if (!res.ok) throw new Error(`GitHub ${res.status}`);
  return (await res.json()) as T;
}

async function commitFiles(sha: string): Promise<CommitFiles> {
  const cached = await storage.get<CommitFiles>(CACHE_PREFIX + sha);
  if (cached) return cached;
  const detail = await getJson<{
    commit: { author: { date: string } };
    files?: { filename: string; status: string }[];
  }>(`${API}/commits/${sha}`);
  const files: CommitFiles = {
    date: stamp(new Date(detail.commit.author.date)),
    modified: (detail.files ?? [])
      .filter((f) => f.status === "modified" && f.filename.endsWith(".webp"))
      .map((f) => f.filename),
  };
  await storage.set(CACHE_PREFIX + sha, files);
  return files;
}

/** 저장소의 커밋을 옛날부터 훑어 교체한 그림을 센다 */
async function fetchReplaced(): Promise<Record<string, ReplacedImage>> {
  const list = await getJson<{ sha: string; parents: unknown[] }[]>(
    `${API}/commits?per_page=100`,
  );
  const out: Record<string, ReplacedImage> = {};
  // 최근 것이 앞에 오므로 뒤집는다. 처음 올린 커밋(부모 없음)은 그림을 더하기만 했다
  for (const c of [...list].reverse()) {
    if (c.parents.length === 0) continue;
    const files = await commitFiles(c.sha);
    for (const path of files.modified) {
      const slug = path
        .split("/")
        .pop()!
        .replace(/\.webp$/, "");
      // macOS 가 외장하드에 만드는 ._ 메타데이터 파일은 그림이 아니다
      if (slug.startsWith("._")) continue;
      const key = keyOfImageSlug(slug) ?? slug;
      out[key] = {
        date: files.date,
        rev: c.sha.slice(0, 7),
        count: (out[key]?.count ?? 0) + 1,
      };
    }
  }
  return out;
}

/** 현황 화면이 쓰는 교체 기록. 화면을 열 때마다 저장소에서 다시 확인한다 */
export function useLiveReplaced(): LiveReplaced {
  const [state, setState] = useState<LiveReplaced>({
    map: REPLACED_IMAGES,
    status: "loading",
    checkedAt: replacedData.generatedAt,
  });

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const live = await fetchReplaced();
        const next: LiveReplaced = {
          map: { ...REPLACED_IMAGES, ...live },
          status: "live",
          checkedAt: stamp(new Date(), true),
        };
        storage.set(LAST_KEY, next).catch(() => {});
        if (alive) setState(next);
      } catch {
        // 인터넷이 없거나 한도를 넘으면 지난번에 확인한 결과를 쓴다
        const last = await storage
          .get<LiveReplaced>(LAST_KEY)
          .catch(() => null);
        if (!alive) return;
        setState((s) => ({
          map: { ...REPLACED_IMAGES, ...(last?.map ?? {}) },
          status: "saved",
          checkedAt: last?.checkedAt ?? s.checkedAt,
        }));
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return state;
}
