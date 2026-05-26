# Backtrader CAMPAIGN_002 H4 export — CSV/Provenance Mismatch Report

**Exports dir:** `research/lean_parity/exports/campaign_002_h4`

- all instruments BT-strict-preflight PASS: **True**
- all instruments BT-strict-preflight FAIL: **False**
- any CSV missing: False
- any provenance missing: False
- any provenance stale vs CSV mtime: False

## Per-instrument detail

| instrument | csv? | prov? | row-sha match | row-count match | first-ts match | last-ts match | BT strict pass | prov stale? |
|---|---|---|---|---|---|---|---|---|
| EUR_USD | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| GBP_USD | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| USD_JPY | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| AUD_USD | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| USD_CAD | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| USD_CHF | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| NZD_USD | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

### Detailed shas (per instrument)

**EUR_USD**

- CSV raw sha256 (full file): `94ffab64ddcc9d57…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `533cbf6571ce5f73…`
- Provenance data_sha256: `533cbf6571ce5f73…`
- CSV row count: 19864 vs provenance candle_count: 19864
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:46:58+00:00`

**GBP_USD**

- CSV raw sha256 (full file): `73bfa286b7c404cb…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `68d5160c40c14872…`
- Provenance data_sha256: `68d5160c40c14872…`
- CSV row count: 19864 vs provenance candle_count: 19864
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:46:59+00:00`

**USD_JPY**

- CSV raw sha256 (full file): `14dac4d8b324af20…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `acc23912c5c680fe…`
- Provenance data_sha256: `acc23912c5c680fe…`
- CSV row count: 19866 vs provenance candle_count: 19866
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:47:00+00:00`

**AUD_USD**

- CSV raw sha256 (full file): `f8a476d9f76a65ab…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `24e06add2c652cf7…`
- Provenance data_sha256: `24e06add2c652cf7…`
- CSV row count: 19864 vs provenance candle_count: 19864
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:47:01+00:00`

**USD_CAD**

- CSV raw sha256 (full file): `73c7c1b1aa26a535…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `a6a426d157e0c677…`
- Provenance data_sha256: `a6a426d157e0c677…`
- CSV row count: 19864 vs provenance candle_count: 19864
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:47:02+00:00`

**USD_CHF**

- CSV raw sha256 (full file): `b31c82da8c3e8d28…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `92477336c20056b1…`
- Provenance data_sha256: `92477336c20056b1…`
- CSV row count: 19864 vs provenance candle_count: 19864
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:47:02+00:00`

**NZD_USD**

- CSV raw sha256 (full file): `74481356e4d336d7…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `2bfeae6b64cbce74…`
- Provenance data_sha256: `2bfeae6b64cbce74…`
- CSV row count: 19872 vs provenance candle_count: 19872
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:47:03+00:00`

Read-only diagnostic. Does NOT modify any export, provenance, or registry artifact. Does NOT approve any strategy. configs/approved_strategies.yaml remains approved: [].
