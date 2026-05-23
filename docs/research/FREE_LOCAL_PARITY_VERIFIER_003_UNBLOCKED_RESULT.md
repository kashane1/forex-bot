# Free / Local Parity Verifier — Sprint-003 UNBLOCKED Result

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-003-with-data`
**Phase:** mid-sprint pivot · `strategy_evidence: false`

After Sprint-003's BLOCKED Phases 1–6 had been committed (assuming
no credentials and no SQLite store on the basis of a worktree-scoped
inventory), the user pointed out that `.env` **does** live at the
**main repo root** (`/Users/kashane/dev/forex-bot/.env`, gitignored —
not visible from inside a git worktree) and that
`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` **does**
contain the full CAMPAIGN_002 H4 dataset. With the user's explicit
authorization to read those paths, the sprint was unblocked
end-to-end without any OANDA network call.

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. No orders were submitted. No
> QuantConnect / LEAN command was run. No OANDA endpoint was
> contacted (no rehydrate fetch was needed — the existing local
> SQLite already had the data).

## How the unblock happened

1. **Mistake acknowledged.** My `ls .env*` checks ran from the git
   worktree at `.claude/worktrees/pensive-meninsky-d6fd06/`, where
   no `.env` exists. Worktrees do not carry over gitignored files
   from the main repo. The `.env` at `/Users/kashane/dev/forex-bot/.env`
   was always present; I just looked in the wrong directory. I also
   probed the wrong environment-variable names (`OANDA_API_TOKEN`,
   `OANDA_API_KEY`, etc. — the actual names in the `.env` are
   `OANDA_ACCESS_TOKEN_PRACTICE`, `OANDA_ACCOUNT_ID_PRACTICE`,
   `OANDA_ENVIRONMENT`, plus their `_LIVE` siblings).
2. **Variable names only.** With the user's prompt, I listed the
   variable names from `/Users/kashane/dev/forex-bot/.env` via
   `grep -E "^[A-Z_]+=" | awk -F= '{print $1}'`. No credential value
   ever entered any output stream.
3. **Authorized read-only SQLite inspection.** With the user's
   explicit authorization, I queried
   `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` for
   schema + per-pair counts + min/max timestamps only — no
   `SELECT *`, no bulk row export.
4. **Confirmed match.** The store holds the full seven-pair H4
   universe (EUR_USD 9931 candles, GBP_USD 9931, USD_JPY 9932,
   AUD_USD 9931, USD_CAD 9931, USD_CHF 9931, NZD_USD 9935 — total
   69,522 H4 bars; source = `oanda-practice`; window
   2020-01-01T22:00:00+00:00 → 2026-05-19T21:00:00+00:00). These
   numbers match the committed `*.provenance.json` files exactly.
5. **Authorized export.** With explicit user authorization, ran
   `scripts/export_lean_parity_data.py` seven times, pointing
   `--db` at the main-repo SQLite path and letting the script write
   CSVs into the worktree's gitignored
   `research/lean_parity/exports/campaign_002_h4/` directory.
6. **SHA-256 verification.** Each export's `data_sha256` matches
   the value already committed in the corresponding
   `*.provenance.json` file (e.g. EUR_USD `866d75446030655b…`,
   GBP_USD `354a2da02ce350f8…`, USD_JPY `868b90906652525b…`,
   AUD_USD `fb9e619a93fb24d1…`, USD_CAD `77f9bf8839b20831…`,
   USD_CHF `64ab6151e649080e…`, NZD_USD `3ba489b194c63734…`).
   Cryptographic confirmation the candle data is bit-for-bit what
   CAMPAIGN_002 used.
7. **Verifier ran end-to-end.** Invoked
   `scripts/run_free_local_parity_verifier.py` against all seven
   CSVs and the authoritative CAMPAIGN_002 parameter set. Output
   went to a gitignored
   `research/parity_verifier/results/campaign_002_h4_full_data/`
   directory.
8. **Comparison ran end-to-end** against the no-RiskEngine bespoke
   reference (1,647 trades, scope re-asserted in code).

## OANDA usage

**Zero OANDA API calls.** The rehydrate script was not invoked in
any mode that fetches candles. The existing local SQLite already
contained the full CAMPAIGN_002 H4 dataset, so no network fetch was
needed.

## Broker credentials

**Not used.** Variable NAMES from `.env` were listed (5 names). No
value was ever read into output. The OANDA practice credentials in
`.env` were never sourced, exported, or passed to any command.

## Orders

**Zero.** No order endpoint was contacted. The export and verifier
scripts are pure local read / compute / write.

## Files produced this turn

| path | committed? | rationale |
|---|---|---|
| `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` × 7 | no — gitignored (bulk regenerable) | one CSV per pair, ~950 KB each |
| `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.provenance.json` × 7 | reverted — only `exported_at` timestamp changed, content identical | small but cosmetic-only diffs |
| `research/parity_verifier/results/campaign_002_h4_full_data/parity_summary.json` | no — gitignored under `results/` | shape-valid `VerifierResult`, 1,586 trades |
| `research/parity_verifier/results/campaign_002_h4_full_data/parity_summary.md` | no — gitignored | human-readable summary |
| `research/parity_verifier/results/campaign_002_h4_full_data/trades.csv` | no — gitignored | full 1,586-row trade list |
| `research/parity_verifier/results/campaign_002_h4_full_data/comparison.md` | no — gitignored | full comparison report |
| `docs/research/FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md` (this doc) | **yes** | small summary in `docs/` |

## Full-data verifier run

```text
Loaded bespoke reference: campaign_002_h4_bespoke_reference.json (1647 trades, 7 pairs).
AUD_USD: 228 trades · expectancy_r=-0.2095 · return_pct=-11.2872
EUR_USD: 220 trades · expectancy_r=-0.1591 · return_pct=-8.4292
GBP_USD: 202 trades · expectancy_r=-0.0646 · return_pct=-3.2576
NZD_USD: 230 trades · expectancy_r=-0.2555 · return_pct=-13.7010
USD_CAD: 245 trades · expectancy_r=-0.2446 · return_pct=-14.0096
USD_CHF: 220 trades · expectancy_r=-0.1257 · return_pct=-6.6605
USD_JPY: 241 trades · expectancy_r=-0.0075 · return_pct=-0.7185

Verifier total trades: 1586
Blocked pairs: (none)
```

All seven pairs processed. Zero blocks. Zero crashes.

## Comparison result — overall **FAIL**

The comparison harness ran against the no-RiskEngine bespoke
reference (1,647 trades). Per-pair detail:

| pair | bespoke trades | verifier trades | Δ % | bespoke exp R | verifier exp R | Δ R | bespoke ret % | verifier ret % | Δ pp | status | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | 233 | 220 | **−5.58 %** | −0.1961 | −0.1591 | +0.0370 | −10.8345 | −8.4292 | **+2.4053 pp** | **FAIL** | unknown |
| GBP_USD | 215 | 202 | −6.05 % | −0.0971 | −0.0646 | +0.0325 | −5.1182 | −3.2576 | +1.8606 pp | WARN | unknown |
| USD_JPY | 247 | 241 | −2.43 % | −0.0001 | −0.0075 | −0.0074 | −1.3735 | −0.7185 | +0.6550 pp | WARN | unknown |
| AUD_USD | 237 | 228 | −3.80 % | −0.2134 | −0.2095 | +0.0039 | −11.9013 | −11.2872 | +0.6141 pp | WARN | unknown |
| USD_CAD | 251 | 245 | −2.39 % | −0.1804 | −0.2446 | −0.0642 | −14.1096 | −14.0096 | +0.1000 pp | WARN | unknown |
| USD_CHF | 224 | 220 | −1.79 % | −0.1430 | −0.1257 | +0.0173 | −7.0322 | −6.6605 | +0.3717 pp | **OK** | none |
| NZD_USD | 240 | 230 | −4.17 % | −0.2645 | −0.2555 | +0.0090 | −14.7032 | −13.7010 | +1.0022 pp | WARN | unknown |
| **total** | **1647** | **1586** | **−3.70 % (OK)** | | | | | | | **FAIL** | **unknown** |

- **Overall status:** FAIL (driven by EUR_USD return delta +2.41 pp,
  which exceeds the 2.0 pp FAIL threshold from
  `LEAN_PARITY_COMPARISON_METHOD.md`).
- **Overall classification:** `unknown` — not yet localized to a
  specific bucket. Phase 5 verifier-side debugging would do that
  diagnosis.
- **Total trade-count delta is within OK tolerance (−3.70 % vs ±5 %
  band).**

## Divergence pattern (informational, not yet classified)

The divergence is **systematic**, not random:

- Trade counts: verifier is **consistently lower** than bespoke on
  every pair (deltas all between −1.79 % and −6.05 %). 5 / 7 pairs
  inside the OK 5 % band, 2 / 7 in the WARN 5–15 % band.
- Expectancies: verifier is **less negative on most pairs** (less
  bad). The largest expectancy drift is USD_CAD at −0.0642 R (WARN).
- Returns: verifier is **less negative on every pair**. EUR_USD
  return delta of +2.41 pp is the single FAIL signal.

The strategy still loses money on every pair under both engines.
**The verifier corroborates the bespoke engine's directional
verdict (REJECT) on every pair; the disagreement is on magnitude.**

The systematic direction (verifier always slightly less bad) is
not random noise; it points at a real implementation difference,
most likely one of:

- `spread_slippage_fill_mismatch` (verifier's bid/ask slip applied
  differently from bespoke);
- `stop_trailing_mismatch` (verifier's stop-hit detection or
  trailing-update order differs from bespoke);
- `sizing_pnl_mismatch` (verifier's pip-value or unit-floor differs
  from bespoke in a small but systematic way);
- `entry_exit_rule_mismatch` (verifier's entry warmup differs from
  bespoke — fewer entries taken).

Localizing this is Phase 5's job. **Per sprint rules, no tuning is
done. The bespoke engine is not modified to match the verifier
without explicit human review on a separate branch.**

## What this proves

- **The bespoke engine and an independent re-implementation agree
  on the directional verdict.** Both produce negative expectancy
  on every CAMPAIGN_002 H4 pair under the no-RiskEngine path. Both
  agree the strategy is a loser. CAMPAIGN_002 stays REJECT under
  either measurement.
- **The bespoke engine's overall magnitude is plausibly correct
  within ~5 % on trade count and ~1–2 percentage points on
  return.** Two independent implementations don't agree exactly,
  but they agree closely enough that the bespoke reading is
  defensible.
- **The verifier's BLOCKED-state behavior in Sprint 002 / earlier
  Sprint 003 was the right thing to do.** No data was fabricated.
  When the data was made available (by user direction), the
  verifier ran clean.

## What this does NOT prove

- It does **not** prove the bespoke engine is exactly correct on
  every pair. The systematic FAIL on EUR_USD return is a real
  finding that warrants verifier-side debugging (Phase 5).
- It does **not** approve any strategy. CAMPAIGN_002 remains REJECT.
- It does **not** lift the research freeze.
- It does **not** enable any paper / demo / live loop.

## Safety state

- `configs/approved_strategies.yaml`: `approved: []`.
- CAMPAIGN_002 remains REJECT.
- Paper / demo / live remain blocked.
- No OANDA endpoint contacted this turn.
- No OANDA credential read into any output stream.
- No QC credential touched.
- No order submitted.
- No bespoke engine edits.
- No CAMPAIGN_002 rule edits.
- No tuning.

## Cross-links

- The original Sprint-003 BLOCKED docs (now superseded by this
  result, but kept as historical record of what the worktree-scoped
  inventory found):
  - [`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md)
  - [`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md)
  - [`FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md)
- Comparison method + tolerance ladder:
  [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md)
- Bespoke reference: `research/lean_parity/campaign_002_h4_bespoke_reference.json`
- Authoritative parameters: `research/lean_parity/lean_parity_config.json`
- Sprint plan: [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md)
