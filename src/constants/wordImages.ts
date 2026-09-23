import { WORD_IMAGE_KEYS } from "./wordImageKeys";

/**
 * 단어별 연상 이미지.
 *
 * 그림 5,400여 장(원본 236MB)을 앱에 넣으면 APK 가 400MB 를 넘어 스토어에
 * 올릴 수 없다. 그래서 그림은 별도 저장소에 384px WebP 로 두고 CDN(jsDelivr)
 * 에서 받아 온다. 앱에는 "어떤 낱말에 그림이 있는지"만 들어간다.
 *
 * 열쇠는 낱말의 철자(= 뜻을 가리키는 conceptId)다. 그림은 철자 하나에 한 장이고,
 * 학년·코스는 철자 목록만 가지므로 같은 철자는 어느 과정에서든 같은 그림을 쓴다.
 *
 * 화면에서는 expo-image 로 그린다. 받아 온 그림을 디스크에 담아 두므로
 * 한 번 본 그림은 인터넷이 없어도 다시 뜬다.
 */

/**
 * 그림을 받아 올 주소의 앞부분.
 *
 * 깃허브 Pages 로 내보낸다. 처음에는 jsDelivr 를 쓰려 했으나, jsDelivr 는
 * 저장소 하나가 50MB 를 넘으면 받아 주지 않는다 (우리 그림은 67MB).
 * Pages 에는 그런 제한이 없고 Fastly CDN 을 거쳐 나가므로 속도도 충분하다.
 */
export const IMAGE_BASE_URL = "https://lebass98.github.io/word-images";

/** 그림이 있는 낱말. 있는지 확인할 일이 잦아 집합으로 만들어 둔다 */
const KEYS = new Set(WORD_IMAGE_KEYS);

/** 파일이 놓인 글자 폴더. a~z 가 아니면 "_" 에 둔다 */
function letterOf(key: string): string {
  const first = key.slice(0, 1).toLowerCase();
  return first >= "a" && first <= "z" ? first : "_";
}

/**
 * 낱말 하나의 그림 주소. 그림이 없으면 null.
 *
 * 파일 이름은 낱말을 그대로 쓰되 띄어쓰기만 붙임표로 바꿔 두었다
 * (living room → living-room). 대문자도 그대로다 (COO, Pacific).
 * 서버는 대소문자를 가리므로 여기서 소문자로 바꾸면 안 된다.
 */
export function wordImageUrl(key: string | undefined): string | null {
  if (!key || !KEYS.has(key)) return null;
  const slug = key.trim().replace(/\s+/g, "-");
  return `${IMAGE_BASE_URL}/${letterOf(slug)}/${encodeURIComponent(slug)}.webp`;
}

/**
 * 화면에 넘길 그림.
 *
 * 뜻(conceptId)으로 먼저 찾고 없으면 철자로 찾는다. 두 낱말이 같은 뜻을
 * 가리키면 그림 한 장을 함께 쓰기 때문이다.
 */
export function wordImageSource(
  word: { conceptId?: string; word: string } | undefined,
): { uri: string } | null {
  if (!word) return null;
  const url = wordImageUrl(word.conceptId) ?? wordImageUrl(word.word);
  return url ? { uri: url } : null;
}

/** 이 낱말에 그림이 있는지 */
export function hasWordImage(word: {
  conceptId?: string;
  word: string;
}): boolean {
  return KEYS.has(word.conceptId ?? "") || KEYS.has(word.word);
}

/** 등록된 그림 수 */
export function wordImageCount(): number {
  return KEYS.size;
}
