#!/usr/bin/env bash
# 그림이 한 장 만들어질 때마다 제대로 올라갔는지 지켜보다가,
# 올라가지 못하고 로컬에 남은 커밋이 있으면 대신 올린다.
#
# 그림 작업 스크립트가 스스로 올리기까지 하지만, 원격이 바쁜 순간이나
# 리베이스가 멈춘 경우에는 커밋이 로컬에 남는다. 그때를 메운다.
#
#   ./scripts/push_watchdog.sh          # 기본 90초마다 확인
#   ./scripts/push_watchdog.sh 60 400   # 60초마다, 400회까지
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
EVERY="${1:-90}"
ROUNDS="${2:-400}"
export GIT_EDITOR=true

say() { echo "[$(date '+%H:%M:%S')] $*"; }

# 멈춘 리베이스를 정리한다. 빈 커밋은 건너뛰고, 그림이 겹치면 원격 쪽을 남긴다
settle() {
  for _ in $(seq 1 60); do
    [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] || return 0
    conf="$(git diff --name-only --diff-filter=U)"
    if [ -n "$conf" ]; then
      echo "$conf" | while read -r f; do
        git checkout --ours -- "$f" 2>/dev/null
        git add -- "$f"
      done
      git rebase --continue >/dev/null 2>&1 || git rebase --skip >/dev/null 2>&1
    else
      git rebase --skip >/dev/null 2>&1
    fi
  done
  [ -d .git/rebase-merge ] && { git rebase --abort >/dev/null 2>&1; return 1; }
  return 0
}

say "지킴이 시작 (${EVERY}초마다 확인)"
for _ in $(seq 1 "$ROUNDS"); do
  sleep "$EVERY"

  # 작업이 한창 git 을 쓰는 중이면 건드리지 않는다.
  # 리베이스 중이고 작업이 살아 있으면 작업이 스스로 끝내게 둔다
  if { [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; } &&
     pgrep -f "generate_h1_missing" >/dev/null 2>&1; then
    continue
  fi

  git fetch -q origin 2>/dev/null || continue
  ahead="$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)"
  [ "$ahead" = "0" ] && continue

  # 한 번 더 세어 본다. 작업이 지금 막 올리는 중일 수 있다
  sleep 20
  git fetch -q origin 2>/dev/null
  ahead="$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)"
  [ "$ahead" = "0" ] && continue

  say "안 올라간 커밋 ${ahead}개 발견 — 올린다"
  find . .. -name '._*' -type f -delete 2>/dev/null
  settle || { say "리베이스를 정리하지 못해 이번에는 넘어간다"; continue; }
  git pull --rebase origin main >/dev/null 2>&1
  settle || { say "받아 얹지 못해 이번에는 넘어간다"; continue; }
  if git push origin main >/dev/null 2>&1; then
    say "올림 완료 (${ahead}개)"
  else
    say "올리기 실패 — 다음 차례에 다시 해 본다"
  fi
done
say "지킴이 끝"
