import { useAuthStore } from "../stores/useAuthStore";

/**
 * 운영자 판별.
 *
 * 그림 현황 같은 디버그 화면은 배포 사이트에서 운영자 계정으로 로그인했을 때만 보인다.
 * 이메일을 공개 코드에 그대로 적지 않으려고 SHA-256 해시로 비교한다.
 * 운영자를 더하려면 아래 명령의 결과를 목록에 넣는다.
 *
 *   printf '%s' '이메일(소문자)' | shasum -a 256
 *
 * 화면에서 감추는 것일 뿐 보안 장치는 아니다. 감춘 화면에 비밀 정보를 두지 않는다.
 */
const ADMIN_EMAIL_HASHES = new Set([
  "dc5464b8fa9c9e02e8f218891808e1eceef136fef4ca0d9471e2222e06f7daf7",
]);

async function sha256Hex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/** 이 이메일이 운영자인지. 해시를 못 구하는 환경이면 운영자로 보지 않는다 */
export async function isAdminEmail(email: string | null): Promise<boolean> {
  if (!email || typeof crypto === "undefined" || !crypto.subtle) return false;
  try {
    return ADMIN_EMAIL_HASHES.has(await sha256Hex(email.trim().toLowerCase()));
  } catch {
    return false;
  }
}

/**
 * 그림 현황(디버그 화면)을 보여 줄지.
 * 개발 서버에서는 늘 보이고, 배포본에서는 운영자로 로그인했을 때만 보인다.
 */
export function useImageStatusVisible(): boolean {
  const isAdmin = useAuthStore((s) => s.isAdmin);
  return __DEV__ || isAdmin;
}
