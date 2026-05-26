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

- CSV raw sha256 (full file): `634fbc89fae3d142…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `bd7aa28b26efb911…`
- Provenance data_sha256: `bd7aa28b26efb911…`
- CSV row count: 9933 vs provenance candle_count: 9933
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:40+00:00`

**GBP_USD**

- CSV raw sha256 (full file): `db7bfc0d4751f739…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `214532db74e5a023…`
- Provenance data_sha256: `214532db74e5a023…`
- CSV row count: 9933 vs provenance candle_count: 9933
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:41+00:00`

**USD_JPY**

- CSV raw sha256 (full file): `df37d3e79677e71a…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `fd57e2fe99f9d4a3…`
- Provenance data_sha256: `fd57e2fe99f9d4a3…`
- CSV row count: 9934 vs provenance candle_count: 9934
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:41+00:00`

**AUD_USD**

- CSV raw sha256 (full file): `ab339a4722ac8181…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `401f8634fb9001e1…`
- Provenance data_sha256: `401f8634fb9001e1…`
- CSV row count: 9933 vs provenance candle_count: 9933
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:42+00:00`

**USD_CAD**

- CSV raw sha256 (full file): `c041ab03c7793d86…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `c06ec608b257c8df…`
- Provenance data_sha256: `c06ec608b257c8df…`
- CSV row count: 9933 vs provenance candle_count: 9933
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:43+00:00`

**USD_CHF**

- CSV raw sha256 (full file): `696e66bfef902a1b…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `8d0e7bf4fa0852c1…`
- Provenance data_sha256: `8d0e7bf4fa0852c1…`
- CSV row count: 9933 vs provenance candle_count: 9933
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:44+00:00`

**NZD_USD**

- CSV raw sha256 (full file): `c7bf2d1e9fa99c14…`
- CSV row-sha256 (data_adapter.compute_csv_sha256): `0ccc07324b8a7a4e…`
- Provenance data_sha256: `0ccc07324b8a7a4e…`
- CSV row count: 9937 vs provenance candle_count: 9937
- CSV first_ts: `2020-01-01T22:00:00+00:00` vs provenance: `2020-01-01T22:00:00+00:00`
- CSV last_ts: `2026-05-20T05:00:00+00:00` vs provenance: `2026-05-20T05:00:00+00:00`
- provenance exported_at: `2026-05-26T01:51:44+00:00`

Read-only diagnostic. Does NOT modify any export, provenance, or registry artifact. Does NOT approve any strategy. configs/approved_strategies.yaml remains approved: [].
