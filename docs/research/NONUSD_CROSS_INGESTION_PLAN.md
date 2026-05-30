# Non-USD Cross Ingestion Plan (Sprint 001, Phase 1)

**Sprint:** `research-nonusd-cross-data-population-001`
**Status:** planning. No data written yet at this phase.

## Available history (OANDA practice, daily-candle probe)

All eight crosses have OANDA practice history back to **2009-12-31**,
latest **2026-05-26** — i.e. availability is **not** the binding
constraint. To keep crosses comparable to the control universe we **match
the majors' M1 window**, not OANDA's full depth.

| Cross | OANDA earliest (D) | OANDA latest (D) | Availability |
|-------|--------------------|------------------|--------------|
| EUR_GBP | 2009-12-31 | 2026-05-26 | full |
| EUR_JPY | 2009-12-31 | 2026-05-26 | full |
| GBP_JPY | 2009-12-31 | 2026-05-26 | full |
| AUD_JPY | 2009-12-31 | 2026-05-26 | full |
| NZD_JPY | 2009-12-31 | 2026-05-26 | full |
| EUR_CHF | 2009-12-31 | 2026-05-26 | full (NB 2015-01-15 SNB break inside window? no — window starts 2021) |
| GBP_CHF | 2009-12-31 | 2026-05-26 | full |
| EUR_AUD | 2009-12-31 | 2026-05-26 | full |

## Target horizon (matched to majors)

- **M1 ingestion window:** `2021-05-26 → 2026-05-27` (the majors' M1 span;
  native broker H4 reaches 2020-01-01 but M1 — and everything derived from
  it — begins 2021-05-26).
- Note: the EUR_CHF 2015 SNB structural break is **outside** this window,
  so it does not affect the populated data (still flagged in the registry
  for any future longer-horizon study).

## Expected row counts

Majors average **~1,827,600 M1 rows** each over this window (range
1.79M–1.84M). Crosses trade the same 24×5 sessions, so expected M1 counts
are comparable; thinner crosses (NZD_JPY, GBP_CHF) may sit slightly lower.
Expected per cross: **≈1.75M–1.85M M1 rows**. Actuals will be read back
from the store and reported — no count is assumed.

## Storage requirements

- Current `market_data.candles`: **11 GB / 20.9M rows** (~555 bytes/row).
- Per cross, M1 only: ~1.8M rows ≈ **~1.0 GB**.
- Per cross, + materialized M5/M15/H1/H4M1 (~0.5M rows): **~2.3M rows ≈
  ~1.3 GB**.
- 4 required crosses fully populated+materialized: **~9.3M rows ≈ ~5 GB**.
- 8 crosses: **~18.6M rows ≈ ~10 GB** (total DB ≈ 21 GB).

Local Postgres has ample capacity; M3/M30 diagnostic timeframes are **not**
materialized this sprint (only M5/M15/H1/H4M1 per scope), keeping the
footprint lower than the majors'.

## Ingestion sequencing

Required crosses first, in cost-band / value order (`PRIMARY_CROSS_PAIRS`):

1. **EUR_GBP** (near-major, tightest)
2. **EUR_JPY** (near-major, JPY-funded)
3. **GBP_JPY** (wide, breadth)
4. **AUD_JPY** (moderate, classic carry)

Each ingested independently with its own `fetch_batch_id`; `data_hash`
auto-computed per row; source label `oanda-practice-m1`. Command:

```
python scripts/ingest_oanda_m1_candles.py --crosses \
  --start 2021-05-26 --end 2026-05-27 \
  --execute-readonly-ingestion --allow-large-range --quiet
```

(The `--crosses` flag expands to exactly the four required primary crosses.)

Optional crosses (NZD_JPY, EUR_CHF, GBP_CHF, EUR_AUD) are ingested via
`--all-crosses` **only if** the four required complete with time margin;
otherwise left `NOT_INGESTED` and documented honestly.

Materialization (Phase 4) then runs `--all-crosses` over the populated set,
producing M5/M15/H1/H4M1, followed by `verify_materialized_pair` parity
checks.

## Safeguards (unchanged)

- Practice host only; live host refused; endpoint regex limits to
  `/v3/instruments/XXX_XXX/candles`; mutation/account paths refused.
- `OANDA_ENVIRONMENT=practice` confirmed; live env refused.
- Research DB safety check passed (local, non-prod name).
- Only compact JSON manifests are committed; **no raw candle data** is
  committed (it lives in the local research Postgres, which is gitignored
  infra).
