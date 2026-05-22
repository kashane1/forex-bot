# Observed Financing Capture

**Date:** 2026-05-22 · **Branch:** `infra-execution-fidelity-001` · Phase 4

Infrastructure to **record actual financing events once trades exist** —
a schema, a repository, and a parser for OANDA `DAILY_FINANCING`
transactions. It is built now so that a *future*, human-authorized
paper/demo phase can collect real financing data from day one.

> **This sprint connects to nothing.** No OANDA call is made, no loop is
> enabled, no order is submitted. The `observed_financing_events` table
> ships **empty** and stays empty under the research freeze. This is
> a dormant seam, not an active pipeline.

## Why this does NOT solve historical financing

Accurate *historical* financing is still unavailable — nothing here
changes that (see `docs/research/FINANCING_MODEL_DESIGN.md` and
`src/forex_bot/financing.py`):

- OANDA's v20 REST API publishes **no historical financing-rate time
  series**. There is nothing to backtest against for 2020–2026.
- `DAILY_FINANCING` transactions exist **only for trades actually held
  on an account**. This research bot has submitted no orders, so there
  is **no** financing history to capture.
- A practice account's `financing` rates are 0 — practice accounts do
  not carry real carry costs.

So the backtest engine's PnL remains financing-`UNMODELED`, and
financing stays a **hard live blocker**. Observed-event capture is a
*forward-looking* data collector: it can only ever record financing for
trades that are placed *after* it starts running. It builds the dataset;
it does not retroactively create one.

## How it helps future paper/demo research

Once a strategy is (by a deliberate human decision, via the approval
process) allowed to paper- or demo-trade, every real trade it holds
overnight generates `DAILY_FINANCING` transactions. With this capture
layer already in place, that observation phase can:

- record each financing charge/credit per instrument and per trade, as
  it happens, with provenance;
- accumulate, over months, a **real, account-specific** financing
  dataset — the empirical input a real financing model needs;
- compare observed financing against the conservative stress overlay
  (`ConservativeStressFinancingModel`) to see whether the overlay is
  appropriately conservative or wildly off.

Building the seam now means the future observation phase loses **zero**
financing data to "we hadn't built the recorder yet."

## What was built

| component | location |
|---|---|
| `ObservedFinancingEvent` domain model | `src/forex_bot/domain/transactions.py` |
| `hash_account_id()` redaction helper | `src/forex_bot/domain/transactions.py` |
| `map_daily_financing()` / `observed_financing_events()` parsers | `src/forex_bot/broker/mapping.py` |
| `ObservedFinancingEventRepo` | `src/forex_bot/data/repositories.py` |
| `observed_financing_events` table (migration v3) | `src/forex_bot/data/migrations.py` |

### Event schema

| field | meaning |
|---|---|
| `transaction_id` | the broker transaction the event came from |
| `account_id_hash` | **SHA-256 of the account id — never the raw id** |
| `instrument` | the pair, when the transaction breaks financing down |
| `trade_id` | the trade, when a per-trade breakdown is available |
| `units` | position units, when the source transaction carries them |
| `financing` | signed amount — a credit is `> 0`, a debit is `< 0` |
| `currency` | the account home currency the financing settled in |
| `time` | the transaction timestamp |
| `source` | provenance, e.g. `oanda-practice` or `fixture` |

A `DAILY_FINANCING` transaction is broken down per instrument, and per
trade where `openTradeFinancings` is present; otherwise a single
account-level event is recorded. `event_key` (a deterministic hash of
transaction + instrument + trade) makes storage idempotent — re-reading
the same transactions never double-counts.

## Privacy / redaction requirements

These are **mandatory** and enforced in code:

1. **The raw account id is never stored.** `ObservedFinancingEvent`
   carries only `account_id_hash`, and a model validator **rejects** any
   value that is not a 64-character SHA-256 digest — a raw account id
   cannot be persisted even by mistake.
2. **Hash at the boundary.** The mappers call `hash_account_id()` while
   parsing the transaction; the raw id never reaches the domain model,
   the repository, or the database.
3. **No tokens, ever.** Financing transactions contain no credentials;
   nothing token-shaped is parsed or stored.
4. **The hash is stable**, so events from one account still group
   together (`account_id_hash` is indexed) without revealing which
   account.
5. A committed research database is covered by the credential scan in
   `scripts/validate_research_archive.py`; storing only hashes keeps it
   clean.

## How a future financing model could use observed events

The financing-model interface already exists
(`src/forex_bot/financing.py`): `FinancingModel`, the `MODELED /
ESTIMATED / UNMODELED` `FinancingTreatment` enum, and the
not-yet-implemented `FutureOandaObservedFinancingModel` placeholder.

`FutureOandaObservedFinancingModel` is the seam an observed-event-backed
model would fill. Once enough events are captured, it could:

- aggregate observed per-instrument financing into an empirical
  per-pair, per-direction carry rate;
- expose that rate through the `FinancingModel` interface so a campaign
  could fold real financing into engine PnL;
- legitimately advance a campaign's `financing_treatment` from
  `ESTIMATED` toward `MODELED`.

Until that model is implemented **and** validated against a sufficient
observed dataset, financing remains `UNMODELED` in engine PnL and a hard
blocker for any live promotion. Capturing events is the **first** step
of that path — not the last, and not on its own a basis for approving
anything.
