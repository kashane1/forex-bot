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

## Comparison result — initially FAIL, after Phase 5 debug: **WARN**

**Final state after Phase 5 verifier-side debug fixes:**

- Verifier total: **1,655 trades** (vs bespoke 1,647 — Δ **+0.49 %**,
  within OK ±5 %).
- Per-pair: 3 OK (GBP_USD, USD_JPY, AUD_USD), 4 WARN (EUR_USD,
  USD_CAD, USD_CHF, NZD_USD), **0 FAIL**.
- **Overall status: WARN.** Down from FAIL on the initial pass.
- Two verifier-side bugs were identified and fixed (no bespoke-engine
  edits) — see
  [`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md).

The original pre-debug numbers (left below for the historical record)
showed FAIL driven by EUR_USD return delta +2.41 pp. After the two
debug fixes that delta is +0.76 pp (WARN, not FAIL).

### Post-debug per-pair table (final)

| pair | bespoke trades | verifier trades | Δ % | bespoke exp R | verifier exp R | Δ R | bespoke ret % | verifier ret % | Δ pp | status | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | 233 | 235 | +0.86 | −0.1961 | −0.1801 | +0.0160 | −10.8345 | −10.0701 | +0.7644 | WARN | unknown |
| GBP_USD | 215 | 215 | +0.00 | −0.0971 | −0.0966 | +0.0005 | −5.1182 | −5.1107 | +0.0075 | **OK** | none |
| USD_JPY | 247 | 251 | +1.62 | −0.0001 | −0.0126 | −0.0125 | −1.3735 | −1.0642 | +0.3093 | **OK** | none |
| AUD_USD | 237 | 238 | +0.42 | −0.2134 | −0.2167 | −0.0033 | −11.9013 | −12.1254 | −0.2241 | **OK** | none |
| USD_CAD | 251 | 251 | +0.00 | −0.1804 | −0.2409 | −0.0605 | −14.1096 | −14.1071 | +0.0025 | WARN | unknown |
| USD_CHF | 224 | 223 | −0.45 | −0.1430 | −0.1002 | +0.0428 | −7.0322 | −5.4018 | +1.6304 | WARN | unknown |
| NZD_USD | 240 | 242 | +0.83 | −0.2645 | −0.2722 | −0.0077 | −14.7032 | −15.2142 | −0.5110 | WARN | unknown |
| **total** | **1647** | **1655** | **+0.49 (OK)** | | | | | | | **WARN** | **unknown** |

(The AUD_USD `verifier exp R` and `verifier ret %` above are reported
to match the post-Bug #2 verifier run. They differ slightly from the
intermediate post-Bug #1 numbers because Bug #2 changed trade selection.)

### Original pre-debug per-pair detail (FAIL — historical)

This is the **initial** comparison before the Phase 5 fixes; preserved
as the "before" half of the bug investigation:

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

## Divergence pattern — pre-debug observations and resolution

**Pre-debug:** divergence was **systematic**, not random — verifier
consistently lower trade count and less negative on every pair.
This systematic direction pointed at a real implementation difference,
not random noise.

**Phase 5 debug found two verifier-side bugs (no bespoke change):**

- **Bug #1** — initial stop was anchored at the post-slippage
  `entry_price` instead of the bar's mid `close`. Fixed in
  `research/parity_verifier/rules.py` (`initial_stop_price` now takes
  `close_price` instead of `entry_price`).
- **Bug #2** — verifier's event loop blocked same-bar re-entry after
  an exit. Bespoke processes exits first then evaluates new entries on
  the same bar. Fixed by refactoring `research/parity_verifier/event_loop.py`
  to use the bespoke bar order (exit → entry).

After both fixes the total-trade delta dropped from −3.70 % to +0.49 %
(within OK), and the comparison verdict moved from FAIL to **WARN**.
The remaining WARN-band drift on 4 / 7 pairs is plausibly Decimal-vs-
float precision and the missing `instrument.round_price(...)` step on
the verifier side. See
[`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md)
for the full trace.

**Per sprint rules:** no tuning was done; the bespoke engine was not
modified; CAMPAIGN_002 rules were not changed.

## What this proves (post-debug)

- **The bespoke engine and an independent re-implementation agree
  on the directional verdict.** Both produce negative expectancy on
  every CAMPAIGN_002 H4 pair under the no-RiskEngine path. Both
  agree the strategy is a loser. CAMPAIGN_002 stays REJECT under
  either measurement.
- **The bespoke engine's overall magnitude is corroborated within
  1.6 % per pair on trade count and 1.6 pp per pair on return**
  (down from FAIL-on-EUR_USD to all-pairs OK or WARN after the two
  Phase 5 fixes).
- **Phase 5 found and fixed two verifier-side bugs.** No bespoke-
  engine bug was found; both bugs were on the verifier side and
  the bespoke engine continues to be the source of truth for the
  CAMPAIGN_002 H4 reference numbers.
- **The verifier's BLOCKED-state behavior in Sprint 002 / earlier
  Sprint 003 was the right thing to do.** No data was fabricated.
  When the data was made available (by user direction), the
  verifier ran clean.

## What this does NOT prove

- It does **not** prove the bespoke engine is *exactly* correct.
  Sub-WARN drift remains on 4 / 7 pairs, plausibly explained by
  Decimal-vs-float precision and the missing `round_price`
  rounding on the verifier side. Two independent implementations
  agreeing within 1.6 % is corroboration, not proof.
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
