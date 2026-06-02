# Next Prompt — Crypto Family E Exploratory Diagnostics 001

> **STATUS: SUPERSEDED / COMPLETED (2026-06-02).** Executed as sprint
> `crypto-family-e-exploratory-diagnostics-001`. Outcome: **NO `candidate_for_front_gate`**
> — diagnostics 1/2/3/6/7 `rejected`, 4/5 `blocked_low_power_oi`. See
> `CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md` and
> `CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001_SUMMARY.md`. Next →
> `NEXT_PROMPT_CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md`.


**Precondition status (updated 2026-06-02):** The readiness gate is **MET for diagnostics 1–3, 6, 7** via `crypto-derivatives-backfill-001`:
- BTC+ETH USD-quoted funding backfilled 2020→2026 (56,186 hourly rows each, 99.86% coverage) — `CRYPTO_DERIVATIVES_BACKFILL_001_RESULT.md`;
- perp OHLCV (H1 + D1), hourly index, and basis_h1 (USD, ~6.4y) available;
- derivatives cost model **frozen** — `CRYPTO_DERIVATIVES_COST_MODEL_001.md`.

Diagnostics **4 and 5 (OI-dependent) remain low-power** — only ~180d aggregate daily OI is free; run them only with documented coverage caveats or after forward-collecting OI. Data lives as gitignored CSVs under `research/crypto/derivatives/backfill/<inst>/` (regenerate via `scripts/backfill_crypto_derivatives.py --execute-public-fetch`).

---

We are starting the Crypto Family E exploratory diagnostics sprint.

Work directly on `main`. Commit after each meaningful phase.

## Hard rules

- **Do not create a campaign.**
- **Do not create a strategy.**
- **Do not create a front gate.**
- **Do not approve anything**; do not edit `configs/approved_strategies.yaml`.
- **Do not enable paper/demo/live.**
- **Do not call trading/order/account/private APIs; no API keys.**
- **Run exploratory diagnostics only.**
- **Use BTC and ETH only.** No altcoins, no universe expansion.
- Do not treat any result as tradable edge. A statistically-real effect is not an edge.
- Do not tune or revive Family C or Family B.

## What to do

1. Confirm the data-readiness gate (funding/OHLCV/basis/OI coverage) and the frozen derivatives cost model exist; if not, stop and run backfill instead.
2. Use the **pre-registered hypotheses** in `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md` — do not invent new ones post-hoc. Pre-register thresholds and regime definitions before reading results.
3. For each diagnostic run:
   - compare against **matched nulls** (matched-random, shuffled-timestamp, randomized sign/rank — and wrong-pairing null for basis/cross-asset);
   - include **conservative costs and funding cashflows** (gross, spread-only, all-in, 2× stress; funding sign: long pays short when funding_rate > 0);
   - report **BTC-only, ETH-only, and pooled** — flag single-asset artifacts;
   - apply multiple-comparisons discipline (Holm / forking-path) across horizons and regime cells.
4. Classify each diagnostic with the pre-committed labels: **rejected**, **statistical_only_cost_defeated**, **cost_defeated**, or **candidate_for_front_gate**.
5. Write per-diagnostic result docs + a synthesis, and a next-prompt stub.

## Order of attack

Diagnostics 1–2 (funding-only) are closest to runnable; 3–7 require additional backfill (basis, OI history) and may be deferred or run low-power with documented coverage limits.

## Expected outcome

Given Family C and Family B both closed `STATISTICAL_ONLY_COST_DEFEATED`, the honest prior is that most Family E diagnostics land **rejected** or **statistical_only_cost_defeated**. A `candidate_for_front_gate` requires a real effect that is **net-positive after 2× stress and robust across BTC and ETH** — and even then it earns only a future pre-registered front-gate screen, never a campaign or approval from exploratory results.

## Scaffolding available

- `research/crypto/derivatives_registry.py`, `derivatives_models.py` (incl. `funding_cashflow`, `compute_basis`), `derivatives_sources.py` (public parsers), `derivatives_validation.py`.
- `scripts/ingest_crypto_derivatives_public_data.py` (dry-run default; OKX funding/OI wired; extend for perp OHLCV / mark-index / USD reference before use).
- `scripts/validate_crypto_derivatives_store.py`.
- Source hierarchy + geo constraints: `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md` (Binance/Bybit geo-blocked here; OKX/Deribit reachable).

Paper/demo/live remain blocked. `configs/approved_strategies.yaml` remains empty.
