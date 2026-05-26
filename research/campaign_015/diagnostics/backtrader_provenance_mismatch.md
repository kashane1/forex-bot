# Backtrader CAMPAIGN_002 H4 export — CSV/Provenance Mismatch Report

**Exports dir:** `research/lean_parity/exports/campaign_002_h4`

- all instruments BT-strict-preflight PASS: **False**
- all instruments BT-strict-preflight FAIL: **True**
- any CSV missing: False
- any provenance missing: False
- any provenance stale vs CSV mtime: False

## Per-instrument detail

| instrument | csv? | prov? | row-sha match | row-count match | first-ts match | last-ts match | BT strict pass | prov stale? |
|---|---|---|---|---|---|---|---|---|
| EUR_USD | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| GBP_USD | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| USD_JPY | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| AUD_USD | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| USD_CAD | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| USD_CHF | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| NZD_USD | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

### Detailed shas (per instrument)

**EUR_USD**

- CSV raw sha256 (full file): `87cd3a1301362d48…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `16ed0bc40d05b578…`
- Provenance data_sha256: `866d75446030655b…`
- CSV row count: 9949 vs provenance candle_count: 9931
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T20:38:19+00:00`

**GBP_USD**

- CSV raw sha256 (full file): `5a3c83e0a7d26c7a…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `97feb3ea57b9704f…`
- Provenance data_sha256: `354a2da02ce350f8…`
- CSV row count: 9949 vs provenance candle_count: 9931
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T20:38:20+00:00`

**USD_JPY**

- CSV raw sha256 (full file): `34a9454b5bb7fae3…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `1581cac49c4e5573…`
- Provenance data_sha256: `868b90906652525b…`
- CSV row count: 9950 vs provenance candle_count: 9932
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T20:38:21+00:00`

**AUD_USD**

- CSV raw sha256 (full file): `62938be3ac2d84da…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `513f5653064e0256…`
- Provenance data_sha256: `fb9e619a93fb24d1…`
- CSV row count: 9949 vs provenance candle_count: 9931
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T20:38:21+00:00`

**USD_CAD**

- CSV raw sha256 (full file): `04e9346293513d9e…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `5a1bd163cfa84a1f…`
- Provenance data_sha256: `77f9bf8839b20831…`
- CSV row count: 9949 vs provenance candle_count: 9931
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T20:38:22+00:00`

**USD_CHF**

- CSV raw sha256 (full file): `a3af10b39ba2ed5c…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `897bb5cea41b5084…`
- Provenance data_sha256: `64ab6151e649080e…`
- CSV row count: 9949 vs provenance candle_count: 9931
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T20:38:22+00:00`

**NZD_USD**

- CSV raw sha256 (full file): `21a07eb294a13733…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `4ef9523f41880c0a…`
- Provenance data_sha256: `3ba489b194c63734…`
- CSV row count: 9953 vs provenance candle_count: 9935
- CSV first_ts: `2020-01-01T14:00:00-08:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-24T14:00:00-07:00` vs provenance: `2026-05-19T21:00:00+00:00`
- provenance exported_at: `2026-05-22T21:02:41+00:00`

Read-only diagnostic. Does NOT modify any export, provenance, or registry artifact. Does NOT approve any strategy. configs/approved_strategies.yaml remains approved: [].
