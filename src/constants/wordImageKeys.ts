/**
 * 연상 그림이 있는 낱말 목록.
 *
 * 그림 파일은 앱에 넣지 않고 CDN 에서 받아 온다. 그래서 여기에는 파일이 아니라
 * "이 낱말에는 그림이 있다"는 사실만 적는다. 실제 주소를 만드는 일은
 * wordImages.ts 가 한다.
 *
 * 이 파일은 scripts/sync_word_images.py 가 만든다. 손으로 고치지 않는다.
 */
export const WORD_IMAGE_KEYS: readonly string[] = [
  "beyond",
  "neither",
];
