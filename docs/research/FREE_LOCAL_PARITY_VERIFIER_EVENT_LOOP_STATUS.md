# Free / Local Parity Verifier — Event-Loop Status

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Phase:** 4 · `strategy_evidence: false`

The verifier's minimal independent event loop is implemented and
exercised by fixture-level integration tests. A first full-data
seven-pair run is **BLOCKED** locally because the H4 candle export
CSVs are absent on this branch — the CSVs are gitignored regenerable
bulk data, and this is the expected branch state for a code-only
sprint.

## Implementation summary

- **Loop module:** [`research/parity_verifier/event_loop.py`](../../research/parity_verifier/event_loop.py).
- **Script entry point:** [`scripts/run_free_local_parity_verifier.py`](../../scripts/run_free_local_parity_verifier.py).
- **Shape:** one pair at a time, single open position per pair,
  bar-by-bar deterministic. Indicators compute once over the whole
  series; the loop walks bars in order, evaluating entry → fill →
  size on no-position bars, and trailing-update → exit-ladder on
  open-position bars.
- **No bespoke imports** — `import` lines under `research/parity_verifier/`
  reference only stdlib, pydantic, and other `research.parity_verifier.*`
  modules. A grep test in `tests/research/test_parity_verifier_models.py`
  enforces this.

## Inputs supported

| input | source | committed? |
|---|---|---|
| Authoritative CAMPAIGN_002 parameters | `research/lean_parity/lean_parity_config.json` | yes |
| Bespoke no-RiskEngine reference | `research/lean_parity/campaign_002_h4_bespoke_reference.json` | yes |
| H4 candle CSV per pair | `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` | **no — gitignored bulk** |

## Assumptions (re-derived from the mapping spec)

- Indicators consume mid prices, fills use bid/ask (mapping spec §2 /
  §7).
- Fill timing: `signal_bar_close` — entry at the signal bar's own
  close (mapping spec §2).
- One position per instrument at a time; no re-entry while a position
  is open (mapping spec §4).
- Exit precedence: trailing-stop update → adverse-stop → time-stop →
  end-of-data (mapping spec §5).
- Sizing: 0.25%-of-equity, USD-quoted pip value or
  ``pip_size / mid_price`` for USD-base pairs (mapping spec §6).
- PnL conversion: USD-quote → identity, USD-base → divide by exit
  price (mapping spec §6).
- NAV compounds at trade close.

## Unsupported items

- Financing — unmodeled, per CAMPAIGN_002 (mapping spec §7).
- RiskEngine gates — out of scope per mapping spec §0; the verifier
  targets the no-RiskEngine bespoke reference (1,647 trades), exactly
  as the LEAN algorithm did.
- Multi-asset / portfolio sizing — the loop runs one pair at a time.
- Currency pairs outside the CAMPAIGN_002 universe — `get_instrument`
  raises `KeyError` for anything not in the seven majors.

## Output format

For each run:

- `parity_summary.json` — `VerifierResult` shape (parity_target,
  fill_timing, window_start/end, config_hash, total_trades, per-pair
  trades / expectancy_r / return_pct / profit_factor / win_rate).
  Same shape as the bespoke reference and the LEAN
  `parity_summary.json`, so it feeds the comparison harness directly.
- `trades.csv` — one row per closed position (instrument, side,
  entry_time, entry_price, exit_time, exit_price, exit_reason, units,
  initial_stop_price, final_stop_price, bars_held, r_multiple,
  return_pct). **Gitignored.**
- `parity_summary.md` — human-readable summary rendered by
  `reporting.render_verifier_result_md`.

## Local data availability

Checked on this branch on 2026-05-22:

| pair | CSV present? |
|---|---|
| EUR_USD | NO — gitignored |
| GBP_USD | NO — gitignored |
| USD_JPY | NO — gitignored |
| AUD_USD | NO — gitignored |
| USD_CAD | NO — gitignored |
| USD_CHF | NO — gitignored |
| NZD_USD | NO — gitignored |

All seven `*.provenance.json` files are committed and locally
present; they pin the SHA-256 each CSV must match if it is
regenerated.

## First-run status — BLOCKED (full-data run)

A dry execution of the script with no CSVs present produces a
deterministic, clean BLOCKED state:

```text
$ python scripts/run_free_local_parity_verifier.py --output /tmp/verifier_test/
Loaded bespoke reference: …campaign_002_h4_bespoke_reference.json (1647 trades, 7 pairs).
BLOCKED — AUD_USD: CSV not found at …AUD_USD_H4_lean.csv. The Lean parity export CSVs are gitignored regenerable bulk data …
BLOCKED — EUR_USD: …
BLOCKED — GBP_USD: …
BLOCKED — NZD_USD: …
BLOCKED — USD_CAD: …
BLOCKED — USD_CHF: …
BLOCKED — USD_JPY: …
Verifier total trades: 0
Blocked pairs: ['AUD_USD', 'EUR_USD', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'USD_CHF', 'USD_JPY']
```

The script writes a valid `parity_summary.json` (zero pairs, zero
trades) and a markdown summary that lists the blocked pairs. The exit
code is `2` when every pair is blocked — communicating
non-availability to the caller without crashing or silently emitting
"zero trades, all good".

To unblock locally:

```bash
# 1. Rehydrate the OANDA H4 store (requires OANDA practice creds —
#    this sprint does NOT do this; it is documented as a separate
#    out-of-scope action a human can take):
#    python scripts/oanda_h4_data_rehydrate.py
#
# 2. Regenerate the seven candle CSVs from the local store:
python scripts/export_lean_parity_data.py --source oanda-practice \
    --window 2020-01-01:2026-05-20
#
# 3. Re-run the verifier:
python scripts/run_free_local_parity_verifier.py \
    --output research/parity_verifier/results/campaign_002_h4/
```

Step 1 is out of scope for this branch (this branch does not connect
to OANDA). Step 2 is committed infrastructure. Step 3 is the script
this sprint adds.

## Fixture-test status

[`tests/research/test_parity_verifier_event_loop.py`](../../tests/research/test_parity_verifier_event_loop.py)
— **8 cases pass:**

- empty series → zero trades, zero candles;
- flat series → zero trades;
- uptrend then drop → long entry + stop or trailing-stop exit (the
  exit price equals the final stop price exactly);
- persistent uptrend → time-stop / trailing-stop / EOD exit (at least
  one trade closed cleanly);
- pair summary has expectancy / win-rate fields when trades exist;
- **no-lookahead** — a giant spike on the final bar must not
  influence prior-bar entries (zero trades, as expected);
- the authoritative CAMPAIGN_002 50/200/20/14/2.0/2.0/240 config
  shape loads and runs without crashing on a short bar series;
- USD_JPY smoke test (divide-by-mid sizing path) does not crash.

Full repo suite with these tests: **462 passes** (454 prior + 8 new).

## What this proves

- The verifier's event loop is structurally sound: indicators, rule
  evaluation, and exit-ladder semantics from the mapping spec are
  wired together correctly and survive fixture-level integration
  testing.
- The verifier reports BLOCKED cleanly when its bulk inputs are not
  available, rather than silently producing zero-trade "success".

## What this does NOT prove

- It does not corroborate the bespoke engine on real candles — that
  requires the seven-pair CSVs, currently absent on this branch.
- It does not approve any strategy. ``configs/approved_strategies.yaml``
  remains ``approved: []``.
- It does not enable any paper / demo / live loop.
- It does not contact any broker, cloud, or external service.
