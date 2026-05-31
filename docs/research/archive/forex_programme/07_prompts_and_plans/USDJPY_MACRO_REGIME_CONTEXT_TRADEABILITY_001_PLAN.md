# USD_JPY Macro-Regime Context Tradeability 001 — Plan

**Sprint:** `usdjpy-macro-regime-context-tradeability-001`
**Branch:** `research-usdjpy-macro-regime-context-tradeability-001` (branched from the
framing-correction tip `4f04a50` — depends on the locked framing).
**Date:** 2026-05-28
**Status:** read-only research + lookahead-safe data infrastructure. **NOT** fast-news
trading, **NOT** an event-reaction strategy, **NOT** tick/latency trading, **NOT** a
strategy, **NOT** a campaign, **NOT** C024, **NOT** C023, **NOT** approval, **NOT**
paper/demo/live.

Framing is **locked** by `MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md`.

---

## 1. Purpose

Determine whether **slow, lookahead-safe** macro / rates / calendar **context** helps
classify USD/JPY **tradeability** over M15/H1/H4 horizons — above all *when not to trade*
— without any fast-news reaction and without touching TEST. Macro context is a
tradeability **conditioner / no-trade filter, never an entry signal**.

The question is *"is a future technical setup more/less likely to be tradeable in this
slow regime?"* — never *"what will the market do on the news?"*

---

## 2. Non-goals (explicit)

No fast-news trading; no immediate event-reaction; no tick-level rate-correlation; no
latency-dependent logic; no live headline reaction; no predicting USD/JPY from fast rate
ticks; no strategy/campaign/C024/C023/approval; no paper/demo/live; no verdict change; no
metric rewrite; no threshold-mining; `approved_strategies.yaml` stays `approved: []`;
**TEST 2025-07+ sealed**.

---

## 3. Safety rules

- Phased; commit after each meaningful phase.
- USD_JPY M15/H1/H4 read **read-only**; `.env` only for research-DB access; no credential
  printing.
- Macro/rates/risk features use **as-of / lagged** joins — only values published on or
  before the decision bar (default 1-day publication lag); daily/weekly cadence only.
- Event calendar = **public schedule dates only** (lookahead-safe); the event *outcome* is
  never traded.
- Compact summaries committed; bulky outputs gitignored.

---

## 4. Data inventory (verified this sprint)

**Present — FRED cache** (`data/external_features/.fred_cache/`, daily, 2019→2026,
gitignored local data):

| series | feature_id | use |
|---|---|---|
| DGS2 | us_2y_yield | rates regime (short end) |
| DGS10 | us_10y_yield | rates regime (long end), 2s10s slope |
| VIXCLS | vix | risk-off/on regime |
| SP500 | sp500 | risk regime (trend) |
| DTWEXBGS | broad_usd_index | broad USD strength regime |
| DCOILWTICO | oil_wti | (optional context) |
| NASDAQCOM | nasdaq_composite | (optional risk context) |

**Partial — rate differential:** US 2y/10y present; **JP rate leg absent** from the
cache. For 2021–2025 the BoJ held rates near zero/pinned (YCC), so US rates dominate the
US–JP differential; **US rates are used as the dominant differential proxy and the JP-leg
gap is documented as a limitation** (a verified JP rate series would be future infra).

**Reusable infra:** `research/cross_asset_features/` (fred.py, loader.py, alignment.py)
already does availability-aware (as-of) FRED alignment; the new module reuses that pattern.

**Event calendar — NOT in repo.** Build a small static fixture (dates only):
- **NFP** — computed deterministically (first Friday of month, 13:30 UTC / 08:30 ET).
  Exact, lookahead-safe.
- **FOMC** — best-effort public scheduled announcement dates 2021–2025 (caveated: verify
  vs the Fed calendar before any precommit).
- **CPI / BOJ** — **deferred** (need a verified source; not fabricated). Documented as a
  gap. Per the framing, categories 3–5 (rates/risk regime + no-trade filters) rely only on
  the FRED cache and proceed regardless.

---

## 5. Confirmation / diagnostic categories (all slow, lookahead-safe)

1. **Macro event-avoidance windows** (NFP primary, FOMC best-effort): pre/post-event
   spread, volatility, whipsaw — when to stand aside.
2. **Delayed post-event stabilization** at +4h/+8h/+24h/+48h vs normal periods.
3. **Rate-differential regime** (US 2y/10y level & trend, daily/weekly): does the slow
   regime correlate with USD/JPY drift/volatility **regimes**.
4. **Risk regime** (VIX level/trend, SP500 trend): does risk regime condition tradeability.
5. **No-trade filters**: regimes/windows where technical systems are structurally
   untradeable (cost/whipsaw) — highest-value, lowest-overfit output.
6. **Setup-conditioning**: macro context conditions whether a future technical setup is
   worth testing — never the entry.

USD/JPY tradeability is measured with the **existing** descriptive metrics (spread pips,
ATR/range, whipsaw rate, breakout-survival/false-breakout) conditioned on the slow context.

---

## 6. Lookahead & latency-safety requirements

- As-of join with a default **1-day** publication lag; Phase 3 re-runs with a larger lag
  to prove **latency-independence** (a real edge must survive hours/days of delay).
- Event calendar uses schedule dates known in advance; outcomes never used.
- Daily/weekly cadence only; nothing sub-minute.
- A unit test proves the as-of join uses no future values.
- TEST sealed throughout.

---

## 7. Expected artifacts

| phase | artifact |
|---|---|
| 0 | this plan |
| 1 | `src/forex_bot/research/macro_regime_context.py` + tests; `research/usdjpy_macro_regime_context/event_calendar.json` (dates-only fixture) |
| 2 | `scripts/build_usdjpy_macro_regime_context_dataset.py` + `scripts/analyze_usdjpy_macro_regime_context.py`; `research/usdjpy_macro_regime_context/{context_manifest.json,analysis_summary.json}`; `docs/research/USDJPY_MACRO_REGIME_CONTEXT_RESULT.md` |
| 3 | `docs/research/USDJPY_MACRO_REGIME_CONTEXT_ROBUSTNESS.md` |
| 4 | `docs/research/USDJPY_MACRO_REGIME_CONTEXT_READINESS_DECISION.md` |
| 5 | `docs/research/USDJPY_MACRO_REGIME_CONTEXT_TRADEABILITY_001_SUMMARY.md` |

Bulky per-bar outputs gitignored; only compact summaries committed.

---

## 8. Readiness bar (from the framing doc — a future precommit needs ALL)

slow-regime based · lookahead-safe · latency-independent · not news-reactive · not
speed-competitive · supported on **both** train and validation without TEST · expressed as
tradeability conditioning / no-trade filtering (not a macro entry) · structurally distinct
from C022/C023/microstructure/compression-expansion families.

---

## 9. Validation commands (Phase 0 baseline + Phase 5 final)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

**Phase 0 baseline (2026-05-28):** pytest **2006 passed, 3 skipped** (pre-existing
data-absence); ruff clean; freeze/archive/secret **PASS**. `approved: []`; C023 not
executed; C024 absent; paper/demo loops refuse. Splits: train 2021-06-01..2023-12-31,
validation 2024-01-01..2025-06-30, **TEST 2025-07+ sealed**.

---

## 10. Explicit no-fast-trading / no-C024 / no-approval statement

This sprint builds lookahead-safe slow overlays and runs a read-only **tradeability-
context** diagnostic. It does **no** fast-news/event-reaction/latency trading, treats macro
strictly as a **no-trade filter / conditioner (never an entry)**, creates **no** campaign,
**no** C024, executes **no** C023, implements **no** strategy, changes **no** verdict,
approves **no** strategy, touches **no** sealed TEST data, and leaves paper/demo/live
blocked with `approved: []`. It ends at a readiness decision; a null result → NOT_READY /
PAUSE. Any campaign design is deferred to a future, separately-precommitted sprint.
