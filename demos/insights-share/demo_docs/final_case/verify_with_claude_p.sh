#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/liush2yuxjtu/V2demo_insights_share.git"
SOURCE_DIR="/private/tmp/insights-share-verify-with-source"
WORKSPACE="/private/tmp/insights-share-verify-with"

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
claude -p --dangerously-skip-permissions --add-dir /private/tmp -- "请用非常简单的中文写一个 first-setup-guide，告诉一个非技术新用户：这个临时 workspace 从零开始安装了 client skill 和第一条可复用 shared insight 以后，现在能做什么。最多 4 条。"
printf '\n## final answer\n'
claude -p --dangerously-skip-permissions --add-dir /private/tmp -- "这是 with-skill 版本。请基于当前 workspace 里的内容以及已经安装好的 client skill，用非常简单的中文回答给非技术 PM：Postgres 高并发下 lock timeout 怎么排查？"
