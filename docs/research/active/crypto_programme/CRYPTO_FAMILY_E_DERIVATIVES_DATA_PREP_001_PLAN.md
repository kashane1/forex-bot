# Crypto Family E — Derivatives / Funding / Open-Interest Data Prep 001 — Plan

**Sprint:** `crypto-family-e-derivatives-data-prep-001`
**Branch:** `main`
**Date:** 2026-06-02
**Type:** Data preparation + diagnostics infrastructure ONLY. No factor, no front gate, no campaign, no strategy, no approval.

---

## 1. Current crypto programme state (audited at sprint start)

| Item | State |
|------|-------|
| Universe | BTC/USD and ETH/USD only (no altcoins, no basket expansion) |
| Stage 1 — data design | Complete |
| Stage 2 — spot ingestion infra | Complete (Coinbase spot public REST, M1 + materialized M5/M15/H1/H4/D1) |
| Stage 3 — exploratory diagnostics | In progress |
| Family C — Trend Persistence | **STATISTICAL_ONLY_COST_DEFEATED** |
| Family B — Relative Value (BTC/ETH) | **STATISTICAL_ONLY_COST_DEFEATED** (gross H4 rel-momentum ~4.6 bps; paired all-in hurdle ~260 bps) |
| Spot cost model | FROZEN (`CRYPTO_COST_MODEL_001.md`) |
| Crypto campaign | None |
| Crypto strategy | None |
| `configs/approved_strategies.yaml` | Empty (`approved: []`) |
| Paper / demo / live | Blocked |
| FX programme | COMPLETE · ARCHIVED (`docs/research/FOREX_PROGRAMME_FINAL_STATE.md`) — not reopened |

Baseline validation at sprint start: pytest green, freeze PASS, archive PASS, secret scan PASS. Pre-existing ruff findings (60) live entirely in already-committed files from prior crypto / edge-discovery sprints and are unrelated to this sprint (documented in the summary).

## 2. Why Family E prep was chosen over Family D

Family C and Family B were both **spot-OHLCV-based** and both landed `STATISTICAL_ONLY_COST_DEFEATED`. Family D (non-time bars) would mostly **re-sample the same spot OHLCV** into alternative bars — useful later, but it adds no genuinely new information about the crypto market.

The higher-information next step is to add **crypto-native derivatives data** that does not exist in the repo at all:

- perpetual funding rates
- open interest
- spot/perp basis
- futures/perp OHLCV (where public/free)
- exchange provenance and symbol mapping
- conservative cost assumptions for derivatives diagnostics

This sprint **prepares** that data layer. It does not test it. Family D remains available as a later spot-resampling lane; it is explicitly deferred, not rejected.

## 3. Non-goals (this sprint does NOT do any of these)

- No factor / factor-validation run.
- No front gate.
- No campaign.
- No strategy.
- No approval; no edit to `configs/approved_strategies.yaml`.
- No paper / demo / live enablement.
- No Family E validation or diagnostics execution (designed only).
- No tuning or revival of Family C or Family B.
- No altcoins; no expansion beyond BTC and ETH.
- No funding-rate trading signal.
- No treating exploratory derivatives diagnostics as tradable edge.

## 4. Hard safety rules

- Public market-data APIs only. No private, authenticated, or account endpoints.
- No order / trading / leverage / margin endpoints.
- No exchange private API keys. No code path may require an API-key-shaped env var.
- No paid data.
- Dry-run is the default for every fetch script; real public fetch only behind an explicit `--execute-public-fetch` flag.
- BTC and ETH only — symbol guards refuse anything else.
- Do not commit `.env`, credentials, API keys, database files, bulky raw data, local cache files, or large exchange responses. Raw data is local-only and gitignored.
- Commit only compact manifests, schema docs, validation summaries, synthetic fixtures, and (optionally) intentionally tiny pilot fixtures.

## 5. Data-source plan (Phase 1)

Review free/public BTC/ETH derivatives sources (Binance USDⓈ-M futures public REST, Bybit v5 public, OKX public, Kraken Futures public, Deribit public; CCXT only if used as a public-only adapter). Evaluate each for: perp symbol mapping, funding-rate history, open interest, mark/index price, basis feasibility, OHLCV, timestamp conventions, rate limits, historical depth, public/free status, endpoint stability, redistribution/commit suitability, implementation complexity, caveats. Select an initial source or source hierarchy. Decide direct-HTTP vs adapter. Output: `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md`.

## 6. Schema plan (Phase 2)

Design the canonical derivatives storage model **before** ingestion code: canonical derivative instrument IDs (e.g. `BTC_PERP_USD`, `ETH_PERP_USD`) with exchange-native symbols stored separately; logical datasets for perp/futures OHLCV, funding rates, open interest, mark price, index price, basis, provenance, fetch manifests; UTC timestamp policy with explicit interval/funding/OI conventions; data-quality policy (dupes, monotonicity, missing-interval classification, outliers, symbol-map validation); cost/fee placeholders (maker/taker, funding cashflow direction, spread proxy) with no execution assumptions; git policy (raw local-only, manifests/fixtures committed). Output: `CRYPTO_DERIVATIVES_DATA_MODEL.md` plus minimal loader/registry interfaces consistent with existing crypto modules.

## 7. Implementation plan (Phase 3)

`research/crypto/derivatives_registry.py`, `research/crypto/derivatives_sources.py`, `research/crypto/derivatives_models.py`, and a dry-run-default `scripts/ingest_crypto_derivatives_public_data.py` with public-endpoint allowlist, BTC/ETH-only guards, and credential refusal. Synthetic fixtures for funding/OI/mark/index/perp-OHLCV. Tests for symbol mapping, allowlist, dry-run default, unknown-symbol refusal, BTC/ETH-only guard, no-credential requirement, funding-direction convention, timestamp parsing, duplicate detection.

## 8. Validation plan (Phase 4)

`scripts/validate_crypto_derivatives_store.py` plus `research/crypto/derivatives_validation.py` checking BTC/ETH-only, canonical symbols, per-class row counts, duplicate timestamps, monotonicity, missing intervals, funding-interval consistency, OI availability, mark/index alignment, OHLCV sanity, basis computability, provenance completeness. Manifest format for derivative fetches. Docs: `CRYPTO_DERIVATIVES_VALIDATION_POLICY.md`. Tests for validation helpers.

## 9. Expected deliverables

- `CRYPTO_FAMILY_E_DERIVATIVES_DATA_PREP_001_PLAN.md` (this file)
- `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md`
- `CRYPTO_DERIVATIVES_DATA_MODEL.md`
- derivatives registry / sources / models code + dry-run ingest script
- `scripts/validate_crypto_derivatives_store.py` + `CRYPTO_DERIVATIVES_VALIDATION_POLICY.md`
- synthetic fixtures + tests
- optional tiny public pilot result OR pilot-blocked doc
- `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md`
- `NEXT_PROMPT_CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001.md`
- `CRYPTO_FAMILY_E_DERIVATIVES_DATA_PREP_001_SUMMARY.md`

## 10. Blocked conditions

If no safe credential-free public source can be fetched, the pilot phase produces `CRYPTO_DERIVATIVES_PUBLIC_DATA_PILOT_BLOCKED.md` documenting the blocker, what was safely verified, and the operator action needed — with no fabricated data. All scaffolding, schema, validation, and design deliverables still complete; only live fetch is deferred.

## 11. No-strategy / no-campaign / no-approval statement

This sprint creates **no** strategy, **no** campaign, **no** front gate, and **no** approval. It does not enable paper, demo, or live trading. It does not call trading, order, account, or private APIs. `configs/approved_strategies.yaml` remains empty. BTC and ETH remain the only instruments. The deliverables are data-preparation and diagnostics infrastructure for a **future** Family E exploratory diagnostics sprint, which itself remains exploratory and non-tradable until separate pre-registered validation and explicit human approval.
