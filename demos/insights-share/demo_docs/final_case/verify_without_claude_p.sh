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
claude -p --dangerously-skip-permissions --add-dir /private/tmp -- "Inspect only this workspace. Show a human-readable report with four short sections: Setup, pwd, file tree, final answer. In the Setup section, explain briefly that this workspace was prepared from a fresh git clone but contains only prompt.md. In the pwd section, show the current working directory. In the file tree section, list the files in this workspace. In the final answer section, answer in very simple Chinese for a non-technical PM: 'Postgres 高并发下 lock timeout 怎么排查？' If this workspace does not contain a validated reusable insight, say that clearly and do not invent one."
