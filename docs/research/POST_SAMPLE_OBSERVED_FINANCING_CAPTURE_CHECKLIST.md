# Post-Sample Observed Financing Capture — Checklist

**Date:** 2026-05-27  
**Prerequisite:** Human completed [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md)  
**Type:** Infrastructure checklist — `strategy_evidence: false`

---

## 1. Pre-capture confirmations

- [ ] Positions were **manually** opened in OANDA **practice** UI (not by bot/Cursor)
- [ ] Positions were held across **at least one rollover** (UTC daily financing time)
- [ ] OANDA practice **Transaction History** shows at least one **`DAILY_FINANCING`** row
- [ ] Sample positions were **manually closed** (or you accept open positions may generate additional financing events)
- [ ] `OANDA_ACCESS_TOKEN_PRACTICE` and `OANDA_ACCOUNT_ID_PRACTICE` are set locally (never commit)
- [ ] `OANDA_ENVIRONMENT=practice` (or unset)

---

## 2. Run read-only capture

```bash
python scripts/capture_observed_financing_readonly.py --no-require-practice-tag
```

Optional dry-run first:

```bash
python scripts/capture_observed_financing_readonly.py --dry-run --no-require-practice-tag
```

Optional custom window (include sample dates):

```bash
python scripts/capture_observed_financing_readonly.py \
  --from-iso 2026-05-01T00:00:00Z \
  --to-iso 2026-05-31T23:59:59Z \
  --no-require-practice-tag
```

**Do not** modify the capture script to call mutation endpoints.

---

## 3. Expected outputs

| file | when |
|---|---|
| `research/financing/observed/observed_financing_capture_status.json` | always |
| `research/financing/observed/observed_financing_manifest.json` | always |
| `research/financing/observed/observed_daily_financing_sanitized.json` | if DAILY_FINANCING > 0 |
| `research/financing/observed/raw/*` | gitignored; optional local debug |

---

## 4. How to identify DAILY_FINANCING

In `observed_financing_capture_status.json`:

```json
"status": "OBSERVED_FINANCING_CAPTURED",
"daily_financing_count": <must be > 0>
```

In `observed_daily_financing_sanitized.json`:

- `"kind": "observed_financing_events"`
- `"synthetic": false`
- `"transactions"` array with parsed position/openTrade breakdowns
- `"events"` flat rows with `instrument`, `financing`, `time`

In OANDA UI: Transaction type column = **Daily Financing**.

---

## 5. Verify sanitized artifacts

- [ ] No raw account ID string in committed JSON (only `account_id_hash` SHA-256)
- [ ] No access token in any file
- [ ] Trade IDs appear as `trade_<hash>` redacted form
- [ ] Transaction IDs appear as `tx_<hash>` redacted form
- [ ] `strategy_evidence: false` on status/manifest
- [ ] Raw directory **not** staged for git commit

Run:

```bash
python scripts/scan_artifacts_for_secrets.py
git status --short   # must not show research/financing/observed/raw/
```

---

## 6. Validation commands (after committing sanitized outputs in future sprint)

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

---

## 7. Blocked outcomes

| outcome | action |
|---|---|
| **No DAILY_FINANCING** (`OBSERVED_FINANCING_EMPTY`) | Re-check hold spanned rollover; extend human hold; re-run capture — do not synthetic-fill |
| **Parser failure** | File issue with payload shape; fix `research/financing/observed.py` in a code sprint; do not commit raw dumps |
| **Missing conversion factors** | Document in reconciliation; may not block sparse sample — note in readiness memo |
| **Missing per-trade financing** | Position-level financing may still exist; note in manifest |
| **Credentials missing** | `BLOCKED_CREDENTIALS_MISSING` — set env vars locally only |
| **Live environment** | Stop — practice only |

---

## 8. Next sprint after successful capture

If `daily_financing_count > 0` and sanitized JSON validates:

→ **`infra-observed-financing-post-sample-capture-001`** (commit artifacts, reconciliation, readiness update)

Then if reconciliation passes:

→ **`infra-financing-observed-to-modeled-bridge-001`** (implement bridge per design doc)

---

## 9. Explicit non-goals

- No strategy approval
- No CAMPAIGN_019
- No bot order submission
- No change to C008/C009/C018 verdicts
