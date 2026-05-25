# CAMPAIGN_011 no-RiskEngine bespoke reference — Phase 3 result

**Date:** 2026-05-25
**Branch:** `infra-bespoke-campaign-011-norisk-reference-001`
**Phase:** 3 of `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`
**`strategy_evidence: false`**

> The no-RiskEngine bespoke reference for CAMPAIGN_011 /
> `random_entry_anchor 0.1.0-c011` has been generated, hash-pinned,
> and reproducibly verified. **CAMPAIGN_011 remains REJECT / null
> diagnostic anchor by design.** `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked. No
> OANDA API call was made.

## 1. Exact command

```bash
python scripts/export_campaign_011_norisk_reference.py \
    --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3
```

(All other paths default to those documented in
`CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md` §1.)

## 2. Data source + safety

| field | value |
|---|---|
| SQLite store | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (main-repo path; reached from worktree because git worktrees do not isolate the host filesystem above `.git/worktrees/...`) |
| Data source label per pair | `oanda-practice` (verified by `DataSourceRepo.latest_for(...)` for all 7 pairs) |
| OANDA / network access | **none** — local SQLite only |
| Credentials touched | **none** |
| Files written outside committed paths | none (the determinism-check files were written to `/tmp/` and are not part of this artefact set) |

## 3. Seed behaviour

| field | value |
|---|---|
| `master_seed` | `20260523` (frozen pre-commit, verified at run start) |
| Seed sweep performed? | **no** — frozen by `_assert_frozen(...)` |
| Random source | SHA-256 in `_derive_random_pair(...)` only — no `random.random`, no `numpy.random`, no built-in `hash()` |
| Determinism check (Phase 3 §6) | **PASS** — two consecutive `--full-window-only` runs produced bit-identical JSON outputs |

## 4. Full-window status

| field | value |
|---|---|
| window | `2020-01-01` → `2026-05-20` |
| risk_engine_used | **`false`** (the whole point of this reference) |
| fill_timing | `signal_bar_close` |
| pairs | 7 (canonical order: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| total full-window trades | **2 800** |
| reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference.json` (2.4 KB) |
| sha256 of full-window JSON | `fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78` |
| config_hash | `69ab4e6f08dca374` |

### 4.1 Per-pair full-window summary

| instrument | candles | trades | expectancy R | return % | profit factor | win % | max DD % |
|---|---|---|---|---|---|---|---|
| EUR_USD | 9 931 | 394 | -0.0496 | -4.83 | 0.85 | 47.2 | -6.09 |
| GBP_USD | 9 931 | 400 | -0.0073 | -0.80 | 0.98 | 47.5 | -3.98 |
| USD_JPY | 9 932 | 418 | +0.0004 | +5.90 | 1.18 | 49.5 | -3.82 |
| AUD_USD | 9 931 | 385 | -0.0646 | -6.08 | 0.80 | 47.5 | -6.52 |
| USD_CAD | 9 931 | 394 | -0.0161 | -2.02 | 0.93 | 47.2 | -4.77 |
| USD_CHF | 9 931 | 409 | +0.0503 | +4.77 | 1.15 | 50.6 | -1.90 |
| NZD_USD | 9 935 | 400 | -0.0265 | -2.67 | 0.92 | 47.5 | -5.94 |

`USD_JPY` and `USD_CHF` show **positive** expectancy on the
full-window run. This is a fully expected null-model fluctuation
under 7 pairs × 6.5 years × random 5%-per-bar entry — it is **not**
evidence of an edge. CAMPAIGN_011 is a null model by construction;
even the original CAMPAIGN_011 with-RiskEngine walk-forward showed
positive aggregate expectancy on individual folds (e.g. fold 5/6).
Per `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §12, any
unexpected-looking number triggers pipeline investigation, never
promotion.

### 4.2 Per-pair `data_request_hash` (provenance)

| instrument | data_request_hash |
|---|---|
| EUR_USD | `ed353315b8ffd5a9` |
| GBP_USD | `ca2a95816825492e` |
| USD_JPY | `e1a6a5025f0cdc19` |
| AUD_USD | `c36cbd0228ebffc4` |
| USD_CAD | `40d80a3a240626a4` |
| USD_CHF | `d907a301cc57e010` |
| NZD_USD | `b62683f67f9fc916` |

## 5. Per-fold rollup status (informational sanity check)

| field | value |
|---|---|
| plan source | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` (the frozen rolling plan) |
| folds | 8 |
| total per-fold trades | **1 661** |
| per-fold reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` (13.8 KB) |

### 5.1 Per-fold aggregates (this sprint, no-RiskEngine)

| fold | test window | trades | expectancy R | return % | profit factor |
|---|---|---|---|---|---|
| 0 | 2021-12-21..2022-06-18 | 214 | -0.0398 | -1.93 | 0.84 |
| 1 | 2022-06-19..2022-12-15 | 230 | -0.0037 | +1.36 | 1.09 |
| 2 | 2022-12-16..2023-06-13 | 206 | -0.0072 | +1.84 | 1.16 |
| 3 | 2023-06-14..2023-12-10 | 192 | +0.0010 | -0.34 | 0.97 |
| 4 | 2023-12-11..2024-06-07 | 216 | -0.0153 | -0.72 | 0.94 |
| 5 | 2024-06-08..2024-12-04 | 211 | +0.0219 | +1.02 | 1.10 |
| 6 | 2024-12-05..2025-06-02 | 188 | +0.0389 | +0.79 | 1.07 |
| 7 | 2025-06-03..2025-11-29 | 204 | +0.0066 | +0.35 | 1.05 |

### 5.2 Sanity diff against the published with-RiskEngine walk-forward

| fold | with-RiskEngine trades (committed) | no-RiskEngine trades (this sprint) | Δ |
|---|---|---|---|
| 0 | 143 | 214 | +71 |
| 1 | 150 | 230 | +80 |
| 2 | 153 | 206 | +53 |
| 3 | 150 | 192 | +42 |
| 4 | 162 | 216 | +54 |
| 5 | 153 | 211 | +58 |
| 6 | 128 | 188 | +60 |
| 7 | 138 | 204 | +66 |
| **total** | **1 177** | **1 661** | **+484 (~41 % more)** |

The diff is the spread / session / loss-limit gates being silenced
under the no-RiskEngine path. This matches the CAMPAIGN_002
pattern (1 032 with-RiskEngine vs 1 647 no-RiskEngine, ~60 % more
trades on a directional strategy). Random entries are less
gate-sensitive than trend signals, which is why the percentage
delta here is smaller than CAMPAIGN_002's. **This is the expected
diff** and is itself part of what makes the no-RiskEngine reference
the right comparison target for the future BT-lane sprint.

### 5.3 Why per-fold total (1 661) < full-window total (2 800)

The 8 fold test-windows together cover roughly
`2021-12-21 → 2025-11-29` — about 3.9 years of the 6.4-year
full-window range. The remainder (2020-01-01 → 2021-12-20 and
2025-11-30 → 2026-05-20) is in the full-window run but not in any
fold. The Δ of `2 800 − 1 661 = 1 139` lines up with the missing
~2.5 years of training-window data that the walk-forward plan
deliberately holds out of the test windows (it is the
training / validation portion of the plan, not test).

The per-fold rollup is **informational**: the canonical
comparison target for the future Backtrader sprint is the
**full-window** reference. Per-fold reconciliation is intentionally
non-exact (R2 re-entry blocking at fold boundaries makes a small
strict-equality requirement misleading).

## 6. Determinism check (Phase 3 §6)

```
$ python scripts/export_campaign_011_norisk_reference.py \
      --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 \
      --out /tmp/c011_a.json --diagnostics-md /tmp/c011_a.md \
      --full-window-only
$ python scripts/export_campaign_011_norisk_reference.py \
      --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 \
      --out /tmp/c011_b.json --diagnostics-md /tmp/c011_b.md \
      --full-window-only
$ shasum -a 256 /tmp/c011_a.json /tmp/c011_b.json \
      research/lean_parity/campaign_011_h4_bespoke_reference.json

fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78  /tmp/c011_a.json
fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78  /tmp/c011_b.json
fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78  research/lean_parity/campaign_011_h4_bespoke_reference.json
```

**All three hashes identical.** Determinism verified.

## 7. Provenance summary

| field | value |
|---|---|
| Source code | `scripts/export_campaign_011_norisk_reference.py` (this sprint, Phase 2 commit) |
| Strategy module | `src/forex_bot/strategies/random_entry_anchor.py` (unchanged) |
| Strategy config | `configs/campaign_011_random_entry_anchor.yaml` (unchanged) |
| Walk-forward plan | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` (unchanged) |
| Bespoke engine | `src/forex_bot/backtesting/engine.py` (unchanged) |
| R formula source | `src/forex_bot/backtesting/engine.py:411-415` (`r = pnl_home / ((entry − stop) × units)`, no quote→home conversion — matches sprint-003 BT-lane post-fix) |
| Approximation flags carried by reference | **none** (the reference *is* the bespoke output) |

## 8. Output paths (artefacts committed by this phase)

| path | size | role |
|---|---|---|
| `research/lean_parity/campaign_011_h4_bespoke_reference.json` | 2.4 KB | canonical full-window comparison target |
| `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | 13.8 KB | informational per-fold rollup |
| `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | 2.3 KB | human-readable parity-style summary |
| `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` (this doc) | ~14 KB | Phase 3 result documentation |

## 9. Required disclosure (verbatim)

CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
This sprint produced the missing no-RiskEngine bespoke reference;
it did **not** approve any strategy, did **not** tune any parameter,
did **not** change the CAMPAIGN_011 rules, and did **not** mutate
any existing committed artefact under
`backtests/CAMPAIGN_011_random_entry_anchor/`.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. The reference cannot be used as
evidence of a strategy edge. `strategy_evidence: false`.
