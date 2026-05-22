# Runbooks

Operational playbooks. The authoritative spec is
[`forex_bot_founders_pack/10_RUNBOOKS.md`](../forex_bot_founders_pack/10_RUNBOOKS.md).

## Research status — loops are frozen

As of the research freeze (Research Marathon 001 = NO-GO), **no strategy
is approved for trading**. `bot paper-loop` and `bot demo-loop` refuse to
start: they check `configs/approved_strategies.yaml` (empty) and exit
non-zero. The loops will not run until a strategy is explicitly approved
by a human via the process in
`docs/research/STRATEGY_APPROVAL_PROCESS.md`. Backtesting and all
research commands are unaffected.

Audit the research archive at any time:

```bash
python scripts/validate_research_archive.py
```

D1 (daily) research uses H4→D1 aggregation (`scripts/aggregate_h4_to_d1.py`),
never native OANDA D1. Financing is modelled only as a conservative
*estimate* — a hard live blocker. See
`docs/research/FINAL_RESEARCH_DECISION_MEMO.md` and the
infra-foundation-001 sprint docs.

## Local setup (Mac, Python 3.12+)

1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -e ".[dev]"`
3. `cp .env.example .env` and fill in OANDA practice credentials.
4. `bot doctor --config configs/paper.yaml`
5. `bot sync-instruments --config configs/paper.yaml`
6. `bot fetch-candles --config configs/paper.yaml --instrument EUR_USD --granularity H4 --count 1000`
7. `bot backtest --config configs/paper.yaml`
8. `bot paper-loop --config configs/paper.yaml --once` — **refused
   while the research is frozen** (no approved strategy).
9. `bot demo-loop --config configs/practice.yaml --once` — likewise
   refused. Loops run only after a strategy is approved in
   `configs/approved_strategies.yaml`.

## Kill switch

Active in two ways:

- Config flag: `app.trading_enabled: false`.
- File: presence of the path given by `app.kill_switch_path` (default `./KILL_SWITCH`).

To engage at runtime:

```bash
touch KILL_SWITCH
```

To disengage:

```bash
rm KILL_SWITCH
```

When active, the risk engine rejects every signal with code
`KILL_SWITCH`, and the Executor's first call returns `trading_blocked`.

## Incident: unknown order status

Cause: timeout after submit, partial response, network drop, or
process crash between submit and write.

Steps:

1. Verify the Executor logged `unknown_status_after_submit`.
2. `bot reconcile --config <your config>` — fetches account, open
   orders/trades/positions, and `transactions/sinceid` from the last
   stored transaction id.
3. Inspect SQLite: `select * from system_events where kind='reconcile' order by id desc limit 10;`
4. If reconciliation is still unclean, do NOT lift the block. Open
   the OANDA broker UI and confirm manually.

## Incident: transaction stream disconnect

The Executor uses REST polling for v0; streaming is opt-in. If you do
use the stream, on disconnect:

1. Reconnect with exponential backoff (configured in `RetryPolicy`).
2. Call `bot reconcile` to backfill via `transactions/sinceid`.
3. Resume only after the report comes back clean.

## Incident: data gap

1. `touch KILL_SWITCH` for safety.
2. `bot fetch-candles` for the affected instrument and timeframe.
3. Confirm `complete=1` candles cover the gap. Incomplete candles are
   never used by default.
4. `bot reconcile` and inspect the ledger.

## Incident: spread spike

1. Confirm `risk_decisions` show `SPREAD_TOO_WIDE` rejections in the
   spike window.
2. Confirm any open trade either hit its protective stop or remained
   protected.
3. Capture the spread distribution into the next weekly report.

## Token rotation

1. `touch KILL_SWITCH`.
2. Stop the bot process.
3. Revoke the old token in the OANDA portal.
4. Generate a new token; update `.env`.
5. `bot doctor` to confirm.
6. Remove `KILL_SWITCH` once you have verified no leaks.

## macOS launchd

See `scripts/install_launchd.sh` and `scripts/uninstall_launchd.sh`.
Do NOT install the launchd job until demo mode has been stable for 30
days per `12_ACCEPTANCE_CRITERIA.md`. The plist starts paper or
practice mode only.

## Rollback

Each deploy should record:

- git commit hash (`git rev-parse --short HEAD`)
- config hash (`bot doctor` prints it)
- SQLite migration version (`select max(version) from schema_version`)

Rollback steps:

1. `touch KILL_SWITCH`.
2. Stop the bot process.
3. Inspect the OANDA broker UI for open trades / pending orders.
4. `git checkout <previous-good-commit>`.
5. Restore the previous config from version control.
6. `bot doctor` and `bot reconcile`.
7. Remove `KILL_SWITCH` only after clean reconciliation.
