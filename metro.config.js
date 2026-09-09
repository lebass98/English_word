const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

/**
 * macOS가 exFAT 외장하드에 자동 생성하는 AppleDouble(`._파일명`) 파일 차단.
 *
 * 차단하지 않으면 expo-router가 `app/**​/._화면.tsx`를 실제 라우트로 인식하고,
 * Babel이 그 바이너리를 TypeScript로 파싱하다 SyntaxError를 낸다.
 * 그 결과 파일을 저장할 때마다 재빌드가 실패해서
 * 자동 새로고침(Fast Refresh)이 동작하지 않는 것처럼 보인다.
 *
 * blockList는 Metro의 파일 맵 자체에서 제외되므로 라우트 스캔에도 잡히지 않는다.
 */
const APPLE_DOUBLE = /(^|[\\/])\._[^\\/]*$/;

config.resolver.blockList = [
  ...[].concat(config.resolver.blockList ?? []),
  APPLE_DOUBLE,
];

module.exports = withNativeWind(config, { input: "./global.css" });
