#!/usr/bin/env bash
# Install the forex-bot paper/practice launchd job on macOS.
#
# DO NOT install until demo mode has been stable for 30 days per
# forex_bot_founders_pack/12_ACCEPTANCE_CRITERIA.md. The plist never
# starts live mode.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_TEMPLATE="${REPO_ROOT}/scripts/com.kashane.forexbot.plist.template"
PLIST_TARGET="${HOME}/Library/LaunchAgents/com.kashane.forexbot.plist"
CONFIG_PATH="${1:-${REPO_ROOT}/configs/paper.yaml}"
VENV_PY="${REPO_ROOT}/.venv/bin/python"

if [[ ! -f "${VENV_PY}" ]]; then
    echo "ERROR: ${VENV_PY} not found. Create .venv and pip install -e .[dev] first." >&2
    exit 1
fi

if [[ ! -f "${CONFIG_PATH}" ]]; then
    echo "ERROR: config not found at ${CONFIG_PATH}" >&2
    exit 1
fi

mkdir -p "${HOME}/Library/LaunchAgents"
mkdir -p "${REPO_ROOT}/logs"

sed \
    -e "s|@REPO_ROOT@|${REPO_ROOT}|g" \
    -e "s|@PYTHON@|${VENV_PY}|g" \
    -e "s|@CONFIG_PATH@|${CONFIG_PATH}|g" \
    "${PLIST_TEMPLATE}" >"${PLIST_TARGET}"

launchctl unload "${PLIST_TARGET}" 2>/dev/null || true
launchctl load "${PLIST_TARGET}"
echo "Installed ${PLIST_TARGET} pointing at ${CONFIG_PATH}"
echo "Tail logs with: tail -f ${REPO_ROOT}/logs/launchd.out ${REPO_ROOT}/logs/launchd.err"
