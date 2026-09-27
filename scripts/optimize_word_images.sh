#!/usr/bin/env bash
# 단어 이미지(assets/words)를 512x512 로 맞추고 PNG 를 다시 압축한다.
#
#   1) 512 보다 큰 그림은 sips 로 512x512 로 줄인다
#   2) pngquant 로 팔레트(8비트)화한다. 선화라 색이 몇 가지 안 돼서 여기서 많이 준다
#   3) oxipng 로 무손실 재압축하고 필요 없는 메타데이터를 턴다
#
# 결과가 원본보다 크거나 깨졌으면 그 파일은 건드리지 않고 원본을 그대로 둔다.
# 원본은 git 에 남아 있으므로 되돌리려면 `git checkout -- assets/words` 하면 된다.
#
#   bash scripts/optimize_word_images.sh
set -uo pipefail

cd "$(dirname "$0")/.."
TARGET=${1:-assets/words}
JOBS=$(sysctl -n hw.ncpu 2>/dev/null || echo 4)

for tool in pngquant oxipng sips; do
  command -v "$tool" >/dev/null || { echo "$tool 가 없다. brew install pngquant oxipng"; exit 1; }
done

# 한 장을 처리한다. 하위 셸에서 병렬로 불린다
process() {
  f=$1
  before=$(stat -f %z "$f") || return

  # 가로 크기를 읽어 512 보다 크면 줄인다
  w=$(python3 -c "
import struct,sys
d=open(sys.argv[1],'rb').read(33)
print(struct.unpack('>II', d[16:24])[0])" "$f" 2>/dev/null) || return
  if [ "$w" -gt 512 ]; then
    sips -z 512 512 "$f" --out "$f" >/dev/null 2>&1 || return
  fi

  tmp="$f.opt"
  cp "$f" "$tmp" || return
  pngquant --quality=70-95 --speed 3 --skip-if-larger --force --output "$tmp" "$tmp" 2>/dev/null
  oxipng -o 3 --strip safe -q "$tmp" 2>/dev/null

  # 결과가 멀쩡한 PNG 이고 더 작을 때만 바꾼다
  after=$(stat -f %z "$tmp" 2>/dev/null || echo 0)
  ok=$(python3 -c "
import struct,sys
try:
    d=open(sys.argv[1],'rb').read(33)
    assert d[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II', d[16:24])
    print(1 if (w,h)==(512,512) else 0)
except Exception:
    print(0)" "$tmp" 2>/dev/null || echo 0)

  # 이미 팔레트로 줄여 둔 그림을 또 줄이면 색이 조금씩 깎인다.
  # 그래서 이미 팔레트인 그림은 10% 넘게 작아질 때만 바꾼다.
  palette=$(python3 -c "
import struct,sys
d=open(sys.argv[1],'rb').read(26)
print(1 if d[25]==3 else 0)" "$f" 2>/dev/null || echo 0)
  limit=$before
  if [ "$palette" = "1" ]; then
    limit=$(( before * 90 / 100 ))
  fi

  if [ "$ok" = "1" ] && [ "$after" -gt 0 ] && [ "$after" -lt "$limit" ]; then
    mv "$tmp" "$f"
  else
    rm -f "$tmp"
  fi
}
export -f process

echo "대상: $TARGET  (병렬 $JOBS)"
find "$TARGET" -name '*.png' -print0 \
  | xargs -0 -P "$JOBS" -I{} bash -c 'process "$@"' _ {}
echo "완료"
