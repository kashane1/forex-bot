# Observed Financing Capture Script Result

**Script:** `scripts/capture_oanda_observed_financing_readonly.py`

## Behavior

| Flag | Effect |
|------|--------|
| (default) | Dry-run — no network, no credentials required |
| `--dry-run` | Explicit dry-run |
| `--execute-readonly-capture` | Practice GET transactions only |
| `--start-date` / `--end-date` | Required for execute; optional for dry-run (defaults 14d) |
| `--fixture-out` | Sanitized fixture path (default under `research/observed_financing_capture_readonly/`) |
| `--output-dir` | Status JSON directory |
| `--max-transactions` | Cap list size (default 500) |

## Tests

`tests/unit/test_oanda_readonly_capture_002.py` — dry-run without network, execute credential gate, endpoint safety, sanitization.

## Phase 3 outcome

- Script implemented with mock/dry-run default
- **No OANDA calls in CI/agent environment** during sprint execution
- Prior repo capture (`capture_observed_financing_readonly.py`) remains; new script is sprint-002 canonical path with explicit execute flag

## No-approval statement

Script does not submit orders or approve strategies.
