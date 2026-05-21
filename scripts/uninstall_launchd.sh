#!/usr/bin/env bash
set -euo pipefail
PLIST_TARGET="${HOME}/Library/LaunchAgents/com.kashane.forexbot.plist"
if [[ -f "${PLIST_TARGET}" ]]; then
    launchctl unload "${PLIST_TARGET}" 2>/dev/null || true
    rm -f "${PLIST_TARGET}"
    echo "Removed ${PLIST_TARGET}"
else
    echo "No plist found at ${PLIST_TARGET}; nothing to remove."
fi
