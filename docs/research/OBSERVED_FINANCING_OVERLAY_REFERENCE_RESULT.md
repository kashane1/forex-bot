# Observed Financing Overlay — Reference Result

**Sprint:** `infra-observed-financing-capture-readonly-002`  
**Artifacts:** `research/observed_financing_capture_readonly/`

## Observed overlay ran?

**No** — `insufficiency_report.json` → `OBSERVED_FIXTURE_EMPTY_OR_SPARSE` (zero entries).

## Coverage

N/A — fixture empty.

## Adjusted deltas vs synthetic local-first

Not computed. Synthetic local-first deltas remain authoritative for **diagnostic** drag estimates only.

## Difference vs synthetic overlay

Synthetic overlay applied stress rate table; observed overlay requires non-empty `observed_practice_financing.json` entries mapped to rate source (future bridge). Current pipeline validates contract and fails closed.

## Limitations

- Need successful practice capture with overnight holds
- Need bridge from flat financing events → `financing_rates` table for calculator overlay
- Weekly/multi-day campaigns remain **overlay-required** before promotion review

## Future larger capture

Bounded 14–30 day windows per instrument with open positions; avoid full-account history dump.

## No-approval statement

No strategy approved; C019 verdict unchanged.
