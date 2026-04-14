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
claude -p --dangerously-skip-permissions --add-dir /private/tmp -- "Inspect only this workspace. Show a human-readable report with five short sections: Setup, pwd, file tree, first-setup-guide, final answer. In the Setup section, explain briefly that this workspace was prepared from a fresh git clone and then installed the client skill plus the first reusable shared insight. In the pwd section, show the current working directory. In the file tree section, list the files in this workspace. In first-setup-guide, write a very simple Chinese guide for a new non-technical user. In final answer, answer in very simple Chinese for a non-technical PM: 'Postgres 高并发下 lock timeout 怎么排查？' based only on files in this workspace."
