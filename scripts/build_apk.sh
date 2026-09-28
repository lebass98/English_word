#!/usr/bin/env bash
set -e

# ==============================================================================
# WordPic 안드로이드 릴리스 APK 자동 빌드 스크립트
#
# 1. 외장하드(한글 마운트 경로)의 최신 소스를 ASCII 경로 (~/build/English_word)로 동기화
# 2. Expo prebuild 로 최신 아이콘, 스플래시 화면, 패키지 설정 반영
# 3. Kotlin classpath 스냅샷 및 release 디버그 키 서명 설정 보장
# 4. Gradle assembleRelease 빌드 실행 및 ~/build/WordPic-YYYYMMDD.apk 출력
# ==============================================================================

SRC_DIR="/Volumes/외장하드/App/eng_word/English_word"
BUILD_DIR="$HOME/build/English_word"
OUT_DIR="$HOME/build"

export JAVA_HOME="$HOME/devtools/jdk-17.0.20.1+1/Contents/Home"
export ANDROID_HOME="$HOME/devtools/android-sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

echo "=================================================="
echo "  WordPic 안드로이드 APK 빌드 시작"
echo "  일시: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

# 1. 빌드 폴더 준비 및 소스 동기화
mkdir -p "$BUILD_DIR"
echo "==> [1/4] 최신 소스 동기화 중 ($SRC_DIR -> $BUILD_DIR)..."
rsync -av --delete \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='.expo' \
  --exclude='dist' \
  --exclude='output' \
  --exclude='android/build' \
  --exclude='android/app/build' \
  --exclude='android/.gradle' \
  "$SRC_DIR/" "$BUILD_DIR/"

# 2. 의존성 설치 및 Expo prebuild (아이콘/스플래시/설정 반영)
cd "$BUILD_DIR"
echo "==> [2/4] 의존성 패키지 확인 및 Expo prebuild 실행 중..."
npm install
npx expo prebuild --platform android --no-clean

# 3. 빌드 설정 보장 (Kotlin 증분 빌드 오류 방지 및 릴리스 서명)
echo "==> [3/4] Gradle 빌드 설정 검증 중..."

# kotlin.incremental.useClasspathSnapshot=false 설정 보장
if ! grep -q "kotlin.incremental.useClasspathSnapshot" "$BUILD_DIR/android/gradle.properties"; then
  echo "kotlin.incremental.useClasspathSnapshot=false" >> "$BUILD_DIR/android/gradle.properties"
fi

# release buildType 에 디버그 서명 키 설정 보장 (설치 가능한 APK 생성)
python3 -c "
path = '$BUILD_DIR/android/app/build.gradle'
with open(path, 'r') as f:
    content = f.read()
if 'signingConfig signingConfigs.debug' not in content:
    # release { 바로 아래에 추가
    content = content.replace('release {', 'release {\n            signingConfig signingConfigs.debug', 1)
    with open(path, 'w') as f:
        f.write(content)
    print('  - release buildType 에 디버그 서명 키 설정 완료')
else:
    print('  - release 서명 설정 이미 적용됨')
"

# 4. Gradle 빌드
cd "$BUILD_DIR/android"
echo "==> [4/4] Gradle assembleRelease 컴파일 및 패키징 중..."
./gradlew assembleRelease --no-daemon

# 5. 결과물 확인 및 복사
APK_SRC="$BUILD_DIR/android/app/build/outputs/apk/release/app-release.apk"
TODAY=$(date +%Y%m%d)
APK_DST="$OUT_DIR/WordPic-${TODAY}.apk"

if [ -f "$APK_SRC" ]; then
  cp "$APK_SRC" "$APK_DST"
  echo ""
  echo "=================================================="
  echo "  🎉 APK 빌드 성공!"
  echo "  위치: $APK_DST"
  echo "  용량: $(ls -lh "$APK_DST" | awk '{print $5}')"
  echo "=================================================="
else
  echo ""
  echo "❌ 빌드 실패: 생성된 APK 파일을 찾을 수 없습니다."
  exit 1
fi
