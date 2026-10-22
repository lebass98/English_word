import Constants from "expo-constants";
import { Linking, Platform } from "react-native";

/**
 * 안드로이드 앱 새 버전 확인 (GitHub 릴리즈).
 *
 * 앱은 스토어 없이 APK 로 나눠 주므로, GitHub 저장소의 최신 릴리즈를 보고
 * 지금 버전보다 새것이면 그 APK 를 브라우저로 내려받게 한다.
 * 릴리즈 태그는 `v1.2.0` 처럼 app.json 의 version 앞에 v 를 붙여 만든다.
 *
 * 웹은 main 에 올릴 때마다 Vercel 이 새로 배포하니 확인할 게 없다.
 */
const LATEST_RELEASE_URL =
  "https://api.github.com/repos/lebass98/English_word/releases/latest";

/** 이 기기에서 업데이트를 확인할 수 있는지 */
export const updateAvailable = Platform.OS === "android";

/** 지금 설치된 앱 버전 (app.json 의 version) */
export const currentVersion = Constants.expoConfig?.version ?? "0.0.0";

export interface LatestRelease {
  version: string;
  /** APK 를 바로 내려받는 주소. APK 가 없으면 릴리즈 페이지 */
  downloadUrl: string;
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
      html_url?: string;
      body?: string;
      assets?: { name: string; browser_download_url: string }[];
    };
    if (!data.tag_name || !data.html_url) return null;
    const apk = data.assets?.find((a) => a.name.endsWith(".apk"));
    return {
      version: data.tag_name.replace(/^v/i, ""),
      downloadUrl: apk?.browser_download_url ?? data.html_url,
      notes: data.body ?? "",
    };
  } catch {
    return null;
  }
}

/** 새 버전이 있으면 그 릴리즈를, 없으면 null 을 돌려준다 */
export async function checkForUpdate(): Promise<LatestRelease | null> {
  if (!updateAvailable) return null;
  const latest = await fetchLatestRelease();
  return latest && isNewer(latest.version, currentVersion) ? latest : null;
}

/** APK 를 브라우저로 내려받는다. 받은 뒤 설치는 안드로이드가 맡는다 */
export function openUpdate(release: LatestRelease) {
  return Linking.openURL(release.downloadUrl);
}
