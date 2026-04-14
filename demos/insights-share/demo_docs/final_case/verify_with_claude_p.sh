#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/liush2yuxjtu/V2demo_insights_share.git"
SOURCE_DIR="/private/tmp/insights-share-verify-with-source"
WORKSPACE="/private/tmp/insights-share-verify-with"
FINAL_QUERY="请先检查当前 workspace 里是否有与这个问题直接相关、已经存在并可用的 insight。问题是：Postgres 高并发下 lock timeout 怎么排查？如果有，请只根据那条 insight 用非常简单的中文输出 3 行：问题现象、正确步骤、常见误区。不要补充额外背景。如果没有，请明确说没有，不要编造。无论有没有 insight，第一行都必须正好写 case-answer。"

rm -rf "${SOURCE_DIR}" "${WORKSPACE}"
git clone --depth 1 "${REPO_URL}" "${SOURCE_DIR}"
mkdir -p "${WORKSPACE}/skills/insights-wiki" "${WORKSPACE}/wiki/database"
cp "${SOURCE_DIR}/prompt.md" "${WORKSPACE}/prompt.md"
cp "${SOURCE_DIR}/skills/insights-wiki/SKILL.md" "${WORKSPACE}/skills/insights-wiki/SKILL.md"
cp "${SOURCE_DIR}/demos/insights-share/demo_codes/wiki/database/postgres-concurrency.md" "${WORKSPACE}/wiki/database/postgres-concurrency.md"

cd "${WORKSPACE}"
printf '## Setup\n'
printf -- '- fresh git clone: %s\n' "${REPO_URL}"
printf -- '- installed client skill from the cloned repo\n'
printf -- '- installed the first reusable shared insight from the cloned repo\n\n'

printf '## pwd\n'
pwd
printf '\n## file tree\n'
find . -maxdepth 5 -type f | sort
printf '\n## first-setup-guide\n'
claude -p --model haiku --dangerously-skip-permissions --add-dir /private/tmp -- "请用非常简单的中文写一个 first-setup-guide，告诉一个非技术新用户：这个临时 workspace 从零开始安装了 client skill 和第一条可复用 shared insight 以后，现在能做什么。最多 4 条。"
printf '\n## final answer\n'
claude -p --model haiku --dangerously-skip-permissions --add-dir /private/tmp -- "${FINAL_QUERY}"
