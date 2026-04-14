#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/liush2yuxjtu/V2demo_insights_share.git"
SOURCE_DIR="/private/tmp/insights-share-verify-without-source"
WORKSPACE="/private/tmp/insights-share-verify-without"
FINAL_QUERY="请先检查当前 workspace 里是否有与这个问题直接相关、已经存在并可用的 insight。问题是：Postgres 高并发下 lock timeout 怎么排查？如果有，请只根据那条 insight 用非常简单的中文输出 3 行：问题现象、正确步骤、常见误区。不要补充额外背景。如果没有，请明确说没有，不要编造。无论有没有 insight，第一行都必须正好写 case-answer。"

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
claude -p --model haiku --dangerously-skip-permissions --add-dir /private/tmp -- "${FINAL_QUERY}"
