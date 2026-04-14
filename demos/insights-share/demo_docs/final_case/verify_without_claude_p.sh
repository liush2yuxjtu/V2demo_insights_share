#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/liush2yuxjtu/V2demo_insights_share.git"
SOURCE_DIR="/private/tmp/insights-share-verify-without-source"
WORKSPACE="/private/tmp/insights-share-verify-without"

rm -rf "${SOURCE_DIR}" "${WORKSPACE}"
git clone --depth 1 "${REPO_URL}" "${SOURCE_DIR}"
mkdir -p "${WORKSPACE}"
cp "${SOURCE_DIR}/prompt.md" "${WORKSPACE}/prompt.md"

cd "${WORKSPACE}"
printf '## Setup\n'
printf -- '- fresh git clone: %s\n' "${REPO_URL}"
printf -- '- kept only prompt.md in the temp workspace\n'
printf -- '- no client skill installed\n\n'

printf '## pwd\n'
pwd
printf '\n## file tree\n'
find . -maxdepth 4 -type f | sort
printf '\n## final answer\n'
claude -p --dangerously-skip-permissions --add-dir /private/tmp -- "这是 without-skill 版本。只根据当前 workspace 里的内容，用非常简单的中文回答给非技术 PM：Postgres 高并发下 lock timeout 怎么排查？如果这里没有经过验证的可复用 insight，请明确说没有，不要编造。"
