# OANDA Practice Credential Check — `oanda-practice-readonly-001` Phase 1

**Date:** 2026-05-22 · **Branch:** `oanda-practice-readonly-001`
**Phase:** 1 — credential & environment gate

This is the Phase 1 credential & environment gate for the read-only
OANDA practice integration sprint. It confirms practice credentials are
present and unambiguously safe **without exposing any secret value**.
The probe is offline — it makes **no** OANDA network call (that is
Phase 2).

## Result summary

| Check | Result |
|---|---|
| Practice environment confirmed | **yes** (`OANDA_ENVIRONMENT=practice`) |
| Practice access token present | **yes** |
| Practice account id present | **yes** — redacted `101…001` |
| Live credentials used / selected | **no** |
| Live env vars present in `.env` | yes, but **placeholders** (`replace_me…`) |
| Practice account id == live account id | no |
| Practice token == live token | no |
| OANDA host (this sprint) | `https://api-fxpractice.oanda.com` |
| `practice-data` environment guard | **PASS** |

**Verdict: practice credentials are valid and safe — the credentialed
read-only sprint may proceed.**

## Detail

- **Practice environment confirmed: yes.** `OANDA_ENVIRONMENT` is set to
  `practice`. `configs/paper.yaml` declares `broker.environment:
  practice` and `app.mode: paper`, and resolves credentials from the
  `*_PRACTICE` env vars (`account_id_env: OANDA_ACCOUNT_ID_PRACTICE`,
  `token_env: OANDA_ACCESS_TOKEN_PRACTICE`).

- **Token present: yes.** `OANDA_ACCESS_TOKEN_PRACTICE` is set to a
  non-placeholder value. Its value was **not** printed, logged, or
  written anywhere.

- **Account id present: yes**, redacted as `101…001` (first 3 / last 3
  characters only). The full account id was never printed or written.

- **Live credentials used: no.** The `*_LIVE` env vars exist in the
  local `.env` but hold placeholder values (`replace_me_only_when_ready`,
  flagged `is placeholder: True`). No code path in this sprint reads the
  `*_LIVE` vars — every config used (`paper.yaml`) selects the
  `*_PRACTICE` vars. The practice account id and token differ from the
  live values, so there is no accidental credential reuse.

- **OANDA host:** all network access this sprint uses the practice REST
  host `https://api-fxpractice.oanda.com`. The live host
  `https://api-fxtrade.oanda.com` is never contacted.

- **`practice-data` environment guard:** `forex_bot.guards.
  assert_practice_data_environment(load_settings("configs/paper.yaml"))`
  returned **PASS** — the environment is unambiguously practice
  (`broker.environment == practice`, `OANDA_ENVIRONMENT == practice`,
  `*_PRACTICE` env var names, resolved non-placeholder credentials, and
  no practice/live credential collision).

## Credential handling

- Credentials live only in a local, **gitignored** `.env` in the main
  checkout (`/Users/kashane/dev/forex-bot/.env`). This sprint runs in a
  git worktree; the `.env` is sourced from the main checkout at run
  time and is **not** copied into the worktree.
- `.env` and `.env.*` are gitignored; only `.env.example`
  (placeholders) is tracked. `.env` is **not** staged or committed.
- The probe reports only booleans, env-var **names**, the declared
  environment string, a first-3/last-3 redacted account id, and public
  host URLs. **No token and no full account id was printed, logged, or
  committed.**

## Exact commands run

```bash
# From the worktree root, with the main checkout's gitignored .env
# sourced into the shell environment (repo convention — see
# scripts/fetch_campaign_002.sh).
set -a && source /Users/kashane/dev/forex-bot/.env && set +a

# Offline probe: env-var presence flags (no values), redacted account
# id, and the pure practice-data environment guard. No network call.
python3 /tmp/oanda_cred_probe.py   # temporary; removed after the run
```

The probe: read `OANDA_*` env vars and reported set/unset flags only;
redacted the account id to first-3/last-3; confirmed the practice and
live values differ; loaded `configs/paper.yaml`; and ran
`assert_practice_data_environment`, which passed. The temporary probe
script contained no secrets and was deleted after the run.

## Explicit safety statement

No OANDA credential value — neither the access token nor the full
account id — was printed to the terminal, written to any file, logged,
or committed. Only redacted / boolean / public-host information appears
in this document. `.env` was not staged. This Phase 1 gate made no
network call.
