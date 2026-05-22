#!/usr/bin/env bash
# Fetch real OANDA practice candles for the CAMPAIGN_002 universe.
# Requires .env.local to be sourced and venv active.
set -euo pipefail

CONFIG=configs/campaign_002_real_oanda.yaml
PAIRS="EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD"
GRANS="H4 H1"
FROM=2020-01-01
TO=2026-05-20

for gran in $GRANS; do
    for pair in $PAIRS; do
        echo ">>> fetching $pair $gran"
        bot fetch-candles \
            --config "$CONFIG" \
            --instrument "$pair" \
            --granularity "$gran" \
            --from "$FROM" \
            --to "$TO" \
            --campaign CAMPAIGN_002
    done
done

echo "FETCH_DONE"
