# Runbooks

## Local setup

1. Install Python 3.12+.
2. Install uv or chosen package manager.
3. Clone repo.
4. Copy `.env.example` to `.env` locally; never commit `.env`.
5. Create OANDA practice account and token.
6. Set practice env vars.
7. Run `bot doctor`.
8. Run `bot sync-instruments`.
9. Run `bot fetch-candles`.
10. Run `bot backtest`.
11. Run `bot paper-loop`.
12. Only then consider `bot demo-loop` with OANDA practice order submission.

## Daily operator checklist

- Confirm bot process is running only in intended mode.
- Check latest account snapshot.
- Check reconciliation status.
- Check open positions and protective stops.
- Check daily loss usage.
- Check spread/rejection anomalies.
- Check logs for auth, HTTP, or broker errors.

## Weekly operator checklist

- Generate weekly report.
- Review all closed trades.
- Review rejected trades.
- Compare paper signals vs practice orders.
- Review spread/slippage by pair and session.
- Review any reconciliation mismatches.
- Review all config changes.
- Archive report with config hash.

## Incident: kill switch

Trigger if:

- unexpected order appears
- unprotected position exists
- broker/local reconciliation mismatch persists
- token leak suspected
- repeated order rejects
- runaway loop or duplicate order attempt
- daily/weekly loss breached unexpectedly

Steps:

1. Create `KILL_SWITCH` file in repo root or set config `trading_enabled: false`.
2. Confirm bot logs show `trading_blocked`.
3. Manually inspect OANDA account in broker UI.
4. Cancel unexpected pending orders manually if needed.
5. Close positions manually if risk requires it.
6. Rotate token if a leak is possible.
7. Do not restart order submission until root cause is documented.

## Incident: unknown order status

Cause examples:

- timeout after submit
- broker returns partial response
- network disconnect
- process crash after submit before local write

Steps:

1. Block new orders.
2. Fetch account details.
3. Fetch open orders, trades, positions.
4. Fetch transactions since last known transaction ID.
5. Search by client order ID.
6. Update local ledger.
7. If still unknown, leave trading blocked and inspect broker UI.

## Incident: transaction stream disconnect

Steps:

1. Reconnect with backoff.
2. Poll `transactions/sinceid` using last stored transaction ID.
3. Store missing transactions.
4. Reconcile account, open orders, trades, positions.
5. Resume only if clean.

## Incident: data gap

Steps:

1. Stop trading on affected instruments.
2. Backfill missing candles.
3. Verify no incomplete candle was treated as complete.
4. Recompute indicators for affected windows.
5. Document affected signals.

## Incident: spread spike

Steps:

1. Confirm spread filter rejected new trades.
2. Check if any open trades were stopped during spike.
3. Record spread distribution in report.
4. Consider widening blackout windows only after validation, not reactively.

## Token rotation

1. Stop bot.
2. Activate kill switch.
3. Revoke old OANDA token in account portal.
4. Generate new token.
5. Update local environment variable.
6. Run `bot doctor`.
7. Run read-only account summary.
8. Remove kill switch only after confirming no secrets were committed.

## macOS launchd deployment

Do not set up launchd until demo mode is stable.

Required before launchd:

- absolute path to venv/uv command
- absolute path to config
- working directory set
- log directory exists
- env vars loaded securely
- kill switch path known
- restart policy conservative

The launchd job should start in paper or practice mode, never live by default.

## Rollback plan

Every deploy should have:

- git commit hash
- config hash
- migration version
- rollback command
- previous known-good config
- manual broker inspection checklist

Rollback steps:

1. Activate kill switch.
2. Stop process.
3. Inspect broker state.
4. Checkout previous git commit.
5. Restore previous config.
6. Run migrations only if reversible or compatible.
7. Start in read-only doctor/reconcile mode.
8. Resume paper/practice only after clean reconciliation.
