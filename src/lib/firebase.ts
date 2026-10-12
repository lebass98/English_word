import { getApp, getApps, initializeApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";
import { getFirestore, type Firestore } from "firebase/firestore";
import { Platform } from "react-native";

/**
 * Firebase 연결 (프로젝트: wordpic-ceaa2).
 *
 * 설정값은 .env 의 EXPO_PUBLIC_FIREBASE_* 에서 온다. 브라우저에 실리는 공개용 값이고,
 * 다른 사람의 기록을 못 보게 막는 일은 Firestore 보안 규칙(firestore.rules)이 한다.
 *
 * 지금은 웹에서만 켠다. 네이티브 앱의 구글 로그인은 별도 모듈이 필요해 아직 붙이지 않았다.
 * 또 웹 화면을 Node 에서 미리 그릴 때(SSR)는 window 가 없으니 끈다.
 */
const config = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID,
};

/** 클라우드 기능을 쓸 수 있는 환경인지 */
export const cloudAvailable =
  Platform.OS === "web" &&
  typeof window !== "undefined" &&
  Boolean(config.apiKey && config.projectId);

let services: { app: FirebaseApp; auth: Auth; db: Firestore } | null = null;

/** 처음 부를 때 한 번만 연결한다. 쓸 수 없는 환경이면 null */
export function firebase() {
  if (!cloudAvailable) return null;
  if (!services) {
    const app = getApps().length ? getApp() : initializeApp(config);
    services = { app, auth: getAuth(app), db: getFirestore(app) };
  }
  return services;
}
