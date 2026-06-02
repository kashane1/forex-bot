# Crypto Derivatives — Validation Policy (Family E Prep, Phase 4)

**Sprint:** `crypto-family-e-derivatives-data-prep-001` · Phase 4
**Date:** 2026-06-02
**Scope:** BTC and ETH perpetual derivatives data integrity. No factor, no campaign, no edge inference.

Mirrors the spot validation discipline (`research/crypto/validation.py`, `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`) for the derivatives layer. Status model: **PASS / WARN / FAIL**.

---

## 1. What is validated

| Check | Data class | Level on failure |
|-------|-----------|------------------|
| BTC/ETH-only (canonical perp authorized) | all | **FAIL** |
| Expected canonical symbols resolve | all | **FAIL** (at parse — unknown symbol refused) |
| Row counts per data class | all | reported |
| Duplicate timestamps | all | **FAIL** |
| Timestamp monotonicity (sorted ascending) | all | **FAIL** |
| Missing intervals (vs cadence) | funding, OI | **WARN** (logged, never interpolated) |
| Funding interval consistency (8h cadence; no mixed intervals) | funding | **WARN** |
| Funding outlier (\|rate\| > 0.3%/8h sanity) | funding | **WARN** (retained + flagged) |
| Open-interest availability | OI | **WARN** if absent (known free-data gap), **FAIL** if all-null |
| Mark/index presence | mark_index | **FAIL** if all-null |
| OHLCV sanity (high≥low, positive prices) | perp_ohlcv | **FAIL** |
| Basis computability (perp∩spot UTC overlap) | basis (derived) | reported as coverage ratio |
| Provenance completeness | manifests | reported |

## 2. Status semantics

- **PASS** — clean; safe for the future Family E diagnostics sprint.
- **WARN** — usable but caveated (gaps, outliers, OI-history shortfall). Diagnostics must declare gap tolerance.
- **FAIL** — integrity breach (dupes, non-monotonic, non-BTC/ETH, insane OHLCV, all-null mark/index). Blocks diagnostics until resolved.

Absence of open-interest history is **WARN, not FAIL**, because deep free OI history is a documented gap (source review §3). Diagnostics that require OI must check coverage explicitly.

## 3. Tooling

- `research/crypto/derivatives_validation.py` — pure helpers over the record dataclasses (storage-agnostic; no DB binding forced this sprint).
- `scripts/validate_crypto_derivatives_store.py` — default mode validates the committed **synthetic fixtures** through the real parsers + validators (a no-network self-check that the tooling is wired); `--manifests-dir` additionally summarizes committed fetch manifests.
- Exit code is non-zero only on a fixture-validation **FAIL** (catches tooling regressions in CI).

## 4. Manifest format (compact, committed)

Every real public fetch (Phase 5+) writes a compact manifest under `research/crypto/derivatives/manifests/` containing:

| Field | Notes |
|-------|-------|
| `batch_id` | UUID per fetch |
| `status` | PASS/WARN/FAIL |
| `source` | venue (e.g. `binance-usdm`) |
| `endpoint_category` | funding / open_interest / mark_index / perp_ohlcv |
| `instrument` / `canonical_symbol` | `BTC_PERP_USD` / `ETH_PERP_USD` |
| `native_symbol` | venue-native (e.g. `BTCUSDT`) |
| `quote_ccy` | USD / USDT |
| `start_utc` / `end_utc` | requested window |
| `rows_fetched` / `rows_inserted` / `skipped_duplicate` | counts |
| `fetched_at_utc` | UTC fetch time |
| `data_hash` | SHA-256 of normalized payload (where applicable) |
| `local_raw_path` | path string only — **the raw file itself is never committed** (gitignored) |

## 5. Git policy (enforced)

- Raw responses → `research/crypto/derivatives/raw/` (**gitignored**).
- Committed: compact manifests, synthetic fixtures, validation summaries.
- No `.env`, keys, DB files, or bulky raw data ever staged.

## 6. Out of scope

- No factor diagnostics, no edge inference, no PnL.
- No DB migration (dataclass + manifest contract only).
- No altcoins; BTC and ETH perps only.

---

## Related documents
- `CRYPTO_DERIVATIVES_DATA_MODEL.md`
- `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md`
- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` (spot)
