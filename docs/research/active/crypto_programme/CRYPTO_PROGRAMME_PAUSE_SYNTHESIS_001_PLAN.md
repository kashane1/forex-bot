# Crypto Programme Pause Synthesis 001 — Plan (Phase 0)

**Sprint:** `crypto-programme-pause-synthesis-001`
**Branch:** `main` (worked directly on main; no branch/worktree)
**Date:** 2026-06-02
**Type:** Programme-level synthesis + decision. **Docs-only** (ZERO new diagnostic code). **Not** a diagnostics, factor, campaign, strategy, front-gate, tuning, or paper/demo/live sprint.

---

## 1. Why this sprint

Three crypto factor families have now failed to clear the front-gate bar on the BTC/ETH corpus:

| Family | Verdict |
|--------|---------|
| C Trend Persistence | `STATISTICAL_ONLY_COST_DEFEATED` |
| B Relative Value | `STATISTICAL_ONLY_COST_DEFEATED` |
| E Derivatives (funding/basis/OI) | **NO CANDIDATE** (1/2/3/6/7 `rejected`, 4/5 `blocked_low_power_oi`) |

Per `NEXT_PROMPT_CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md`, the disciplined next step is a synthesis that decides whether to **pause** crypto research — not another exploratory drill (Family D is low-information; OI forward-collection is low-value alone).

## 2. Current repo state (truth audit)

| Check | Result |
|-------|--------|
| Branch / tree | `main`, clean, 0 behind `origin/main` |
| `configs/approved_strategies.yaml` | `approved: []` |
| Paper/demo/live | blocked |
| Crypto campaign / strategy / front gate / approval | none |
| Universe | BTC/USD + ETH/USD (perps BTC_PERP_USD/ETH_PERP_USD) only |
| FX programme | archived (untouched) |
| Frozen cost models | spot `CRYPTO_COST_MODEL_001.md`, perp `CRYPTO_DERIVATIVES_COST_MODEL_001.md` |

## 3. Tasks (from the next-prompt)

1. Classify every crypto effort (data design → ingestion → C → B → E prep/backfill → E diagnostics): what was tested, verdict, failure mode (idea-quality / cost / data-depth / efficiency).
2. Diagnose the dominant failure mode across C/B/E.
3. Evaluate the carried thread (downtrend-conditioned funding mean reversion) — future fresh-pre-registered re-test vs forking-path artifact. **Do not run it.**
4. Evaluate forward-OI collection strictly as an enabler of diagnostics 4/5.
5. Decide disposition: PAUSE (default) vs one narrow step; if PAUSE, write restart criteria mirroring the FX programme's `STRATEGY_RESEARCH_RESTART_CRITERIA.md`.

## 4. Deliverables

- `CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md` — classification, failure-mode diagnosis, thread + OI evaluation, decision.
- `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md` — standing governance doc (mirrors FX).
- Roadmap + README updates; mark the pause-synthesis next-prompt superseded.
- `CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001_SUMMARY.md` + validation.

## 5. Hard rules

No campaign / strategy / front gate / approval. Do not edit `approved_strategies.yaml` except to verify it stays empty. No paper/demo/live. No trading/private APIs; no keys. BTC/ETH only. Do not re-run/re-tune C/B/E. Do not invent new hypotheses. Do not change any frozen cost model. Docs-only. Do not commit raw/bulky data, `.env`, DB files.

## 6. Expected outcome

`PAUSE_CRYPTO_RESEARCH` with documented restart criteria; the downtrend-funding-reversion thread and forward-OI collection preserved as *conditional* reopen paths under fresh pre-registration only.
