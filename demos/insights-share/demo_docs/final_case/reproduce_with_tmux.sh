#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="https://github.com/liush2yuxjtu/V2demo_insights_share.git"
SOURCE_CLONE="/private/tmp/insights-share-source-with"
WORKSPACE="/private/tmp/insights-share-case-with-client"
SESSION="insights_case_with_repro"
EXPORT_FILE="${SCRIPT_DIR}/claude_with_client_skill_export.md"
FINAL_QUERY="请先检查当前 workspace 里是否有与这个问题直接相关、已经存在并可用的 insight。问题是：Postgres 高并发下 lock timeout 怎么排查？如果有，请只根据那条 insight 用非常简单的中文输出 3 行：问题现象、正确步骤、常见误区。不要补充额外背景。如果没有，请明确说没有，不要编造。无论有没有 insight，第一行都必须正好写 case-answer。"

capture_pane() {
  tmux capture-pane -pt "${SESSION}:0" -S -500
}

wait_for_any() {
  local timeout="$1"
  shift
  local end=$((SECONDS + timeout))
  while (( SECONDS < end )); do
    local pane
    pane="$(capture_pane)"
    if [[ "${pane}" == *"Do you want to proceed?"* ]]; then
      tmux send-keys -t "${SESSION}:0" Enter
      sleep 1
      pane="$(capture_pane)"
    fi
    for pattern in "$@"; do
      if [[ "${pane}" == *"${pattern}"* ]]; then
        printf '%s\n' "${pattern}"
        return 0
      fi
    done
    sleep 1
  done
  echo "Timed out waiting for: $*" >&2
  capture_pane >&2
  return 1
}

send_literal() {
  local text="$1"
  tmux send-keys -t "${SESSION}:0" -l "${text}"
  tmux send-keys -t "${SESSION}:0" Enter
}

rm -rf "${SOURCE_CLONE}" "${WORKSPACE}"
git clone --depth 1 "${REPO_URL}" "${SOURCE_CLONE}"
mkdir -p "${WORKSPACE}/skills/insights-wiki" "${WORKSPACE}/wiki/database"
cp "${SOURCE_CLONE}/prompt.md" "${WORKSPACE}/prompt.md"
cp "${SOURCE_CLONE}/skills/insights-wiki/SKILL.md" "${WORKSPACE}/skills/insights-wiki/SKILL.md"
cp "${SOURCE_CLONE}/demos/insights-share/demo_codes/wiki/database/postgres-concurrency.md" "${WORKSPACE}/wiki/database/postgres-concurrency.md"

tmux kill-session -t "${SESSION}" 2>/dev/null || true
tmux new-session -d -s "${SESSION}" -c "${WORKSPACE}" "claude --model haiku"

first_screen="$(wait_for_any 45 "Yes, I trust this folder" "❯")"
if [[ "${first_screen}" == "Yes, I trust this folder" ]]; then
  tmux send-keys -t "${SESSION}:0" Enter
  wait_for_any 45 "❯" >/dev/null
fi
sleep 2

send_literal "! pwd && find . -maxdepth 4 -type f | sort"
wait_for_any 30 "./skills/insights-wiki/SKILL.md" "./wiki/database/postgres-concurrency.md" >/dev/null

send_literal "${FINAL_QUERY}"
wait_for_any 120 "⏺ case-answer" >/dev/null

send_literal "/export ${EXPORT_FILE}"
wait_for_any 60 "Conversation exported to:" >/dev/null

tmux kill-session -t "${SESSION}"
rm -rf "${SOURCE_CLONE}" "${WORKSPACE}"
