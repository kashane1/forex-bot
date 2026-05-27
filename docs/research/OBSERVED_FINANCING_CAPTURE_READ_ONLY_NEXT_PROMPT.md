# Future Sprint Prompt — Observed Financing Capture (Read-Only)

Copy-paste for a **future** sprint. **Do not execute** during `infra-observed-cost-financing-overlay-local-first-001`.

---

## Prompt

You are executing a **read-only observed financing capture** sprint for the forex-bot repo.

**Branch:** `infra-observed-financing-capture-readonly-002` (suggested)

### Hard rules

1. **No** order/trade/position **mutation** OANDA APIs
2. **No** live credentials unless the human explicitly authorizes practice read-only access in that sprint
3. **No** strategy approval; `configs/approved_strategies.yaml` stays `approved: []`
4. **No** CAMPAIGN creation for strategy evidence
5. **No** `.env`, tokens, SQLite DBs, or raw bulky exports committed
6. Capture **transaction history / financing charges** only (read-only endpoints documented in prior `OBSERVED_FINANCING_CAPTURE_READONLY_*` docs)

### Goals

1. Export practice-account financing transactions for a bounded date window
2. Normalize to fixture schema reconcilable with `src/forex_bot/research/financing_overlay.py`
3. Run `manual_observed_fixture` overlay on C008/C016/C017/C019 reference ledgers
4. Compare synthetic vs observed drag; document gaps

### Deliverables

- `research/financing/fixtures/observed_<date>_financing.json` (small, redacted, no account ids if policy requires)
- `docs/research/OBSERVED_FINANCING_CAPTURE_READONLY_002_RESULT.md`
- Reconciliation report vs `FINANCING_OVERLAY_CONTRACT.md`

### Validation

```bash
pytest tests/ -q
python scripts/scan_artifacts_for_secrets.py
python scripts/check_research_freeze.py
```

### Local-only alternative (no broker access)

If capture is unauthorized: extend **manual CSV fixture** workflow from `FINANCING_OBSERVED_FIXTURE_SCHEMA.md` with human-pasted broker statements; label `source: manual_paste_observed`; never infer edge.

---

## No-approval statement

Capture sprint produces data infrastructure only.
