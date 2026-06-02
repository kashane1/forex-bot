# Crypto Programme — Pause Synthesis 001

**Sprint:** `crypto-programme-pause-synthesis-001`
**Date:** 2026-06-02
**Type:** Programme-level synthesis + decision. Docs-only. **No** strategy, campaign, front gate, or approval.
**Standing decision:** `PAUSE_CRYPTO_RESEARCH` (see §6 and `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md`).

---

## 1. Executive summary

The crypto research programme set out to test whether BTC/ETH — a continuous, structurally
different market from FX — could yield a factor that survives realistic costs. Across **three
factor families** (C trend persistence, B relative value, E derivatives) on a clean
multi-year BTC/ETH corpus, **none produced a `candidate_for_front_gate`**. The pattern mirrors
the FX programme: small, sometimes statistically-real gross effects that do not survive
spread + fee (+ funding) hurdles, plus genuinely null mechanisms.

The single most notable exploratory result in the whole programme — downtrend-conditioned
funding mean reversion (the *first* result net-positive after 2× stress across both assets) —
was held below the bar by the pre-registered single-regime-slice and multiple-comparisons
discipline. It is preserved as a *conditional* future thread, not promoted.

**Decision: `PAUSE_CRYPTO_RESEARCH`.** Further exploratory drilling on this corpus has low
expected information value. Restart is gated by explicit criteria (§6). Infrastructure is
preserved and ready.

## 2. What was built and tested (full inventory)

| Stage / effort | What it produced | Verdict | Failure mode (if any) |
|----------------|------------------|---------|------------------------|
| Stage 1 — data design | Source eval, schema, validation reqs, futures hooks (Coinbase spot primary) | Complete | n/a (infra) |
| Stage 2 — spot ingestion | BTC/ETH M1 + materialized M5–D1 in Postgres; 7-day pilot; full 5y backfill; ~99.94% M1 cov | Complete | n/a (infra) |
| Family C — Trend Persistence | Autocorr / run-length / momentum-proxy, nulls, regime terciles, cost variants | `STATISTICAL_ONLY_COST_DEFEATED` | **cost** (gross hints e.g. ETH M15 AC1≈0.013; all-in Sharpe deeply negative under 120 bps spot RT) |
| Family B — Relative Value | BTC/ETH lead-lag, relative momentum, divergence/reversion, one-leg + paired cost | `STATISTICAL_ONLY_COST_DEFEATED` | **cost** (strongest gross ≈4.6 bps H4 rel-momentum vs ~260 bps paired hurdle) |
| Family E — derivatives data prep | Public-only registry/models/sources/validation; OKX pilot (Binance/Bybit geo-blocked) | Complete | n/a (infra) |
| Family E — derivatives backfill | Deribit USD-quoted 6.4y funding/OHLCV/index/basis_h1; 180d OKX OI; frozen perp cost model | Complete | OI depth gap (180d) |
| Family E — exploratory diagnostics | Diag 1/2/3/6/7 + 4/5; matched nulls, all-in+2× incl. funding, Holm | **NO CANDIDATE** | **idea-quality** (1/2/6 within null) + **forking-path control** (3 fails Holm) + **data-depth** (4/5) |

Deferred, not run: Family A (MTF confluence), Family D (non-time bars).

## 3. Family E diagnostic detail (this programme's newest evidence)

| Diagnostic | Label | One-line |
|-----------|-------|----------|
| 1 Funding mean reversion | `rejected` | pooled gross within null (shuffled p 0.26–0.83); BTC +/ETH − single-asset; all-in negative |
| 2 Funding trend continuation | `rejected` | no monotone k gradient; within null; all-in negative |
| 3 Basis compression/expansion | `rejected` | raw p≈0.013–0.017 (h4) → Holm 0.22–0.27; reversion+expansion both raw-sig = forking path |
| 4 OI impulse | `blocked_low_power_oi` | 180d aggregate daily OI only |
| 5 Funding/OI interaction | `blocked_low_power_oi` | same OI depth gap |
| 6 Cross-asset confirmation | `rejected` | agreement & disagreement within null; paired cost-defeated |
| 7 Regime conditioning | `rejected` | one notable sub-bar cell (see §5); basis-tercile cell circular |

## 4. Dominant failure-mode diagnosis

Across C / B / E the failures are **not a single cause**, but they rhyme:

1. **Cost is the dominant killer for C and B.** Both showed statistically detectable gross
   structure that vanished after spread + fees (spot Coinbase 120 bps RT; paired ~260 bps).
   This is the FX S4 pattern: *effect exists, tradable edge does not.*
2. **Family E shifts the diagnosis toward idea-quality, not just cost.** Perps are *cheaper*
   than spot (16–18 bps all-in RT), which is exactly why E was worth testing. Yet funding
   mean-reversion, funding continuation, and cross-asset confirmation are **within their
   matched nulls** — i.e. there is little predictive structure to begin with, before cost
   even applies. The one apparent basis signal failed multiple-comparisons (forking-path),
   not cost. So on the cheapest available venue the binding constraint became **absence of a
   robust predictive effect**, not the cost wall.
3. **Data depth is a real but secondary limit** — only for the OI diagnostics (4/5), which
   are not where any signal appeared.
4. **Market efficiency / crowding** is the through-line: BTC/ETH funding and basis are
   liquid, heavily-arbitraged, well-known signals; the corpus shows them behaving close to
   efficiently at the horizons tested.

**Conclusion:** the programme has now hit *both* walls in sequence — cost (C/B) and
idea-quality/efficiency (E) — on the same two-asset corpus. That combination is what makes
"keep drilling" low-value.

## 5. Evaluation of the carried thread — downtrend-conditioned funding mean reversion

**What it is.** In Family E diagnostic 7, conditioning funding mean reversion (h24) on a
prior-7-day **downtrend** regime produced the only net-positive-after-2× result in the entire
programme: pooled n=901, all-in +0.0036, 2× +0.0019; BTC 2× +0.0027, ETH 2× +0.0011 — BTC and
ETH both supportive and both 2×-stress-positive; within-regime-family Holm-adjusted p≈0.032.

**Why it is NOT a candidate (pre-registered discipline).**
- It is a **single regime slice** conditioning a base diagnostic (diag 1) that was *rejected*
  unconditioned. The frozen gate explicitly forbids a tiny regime slice overriding base failure.
- Under **full-family Holm** (including the per-asset and base tests, not just the 34-cell
  regime family) it is **borderline/failing**.
- It is one favorable cell among many regime × tercile × base combinations — exactly the
  forking-path risk pre-registered against.

**Is it a real mechanism or an artifact?** It is *economically plausible* (in a downtrend,
extreme positive funding marks crowded longs whose forced unwind reverts price). That
plausibility plus BTC/ETH robustness is why it is **preserved, not discarded** — but
plausibility is not evidence of a tradable edge, and the statistical support does not survive
honest multiple-comparisons. **Verdict: a NOTABLE-BUT-UNPROVEN thread.** It may only ever be
revisited as a *fresh, independently pre-registered* hypothesis with walk-forward and
full-family MC — never as a re-tune of this sprint's output.

## 6. Decision and disposition

**`PAUSE_CRYPTO_RESEARCH`.**

Rationale weighed against the four pre-committed options:

| Option | Assessment |
|--------|------------|
| Front-gate design | **Rejected** — no diagnostic cleared the candidate bar. |
| OI forward collection | **Not now (low value alone)** — high-power diagnostics (1/2/3/6) failed on deep, non-OI data; OI only re-enables the two weakest diagnostics. A reopen path, not a next step. |
| Family D (non-time bars) | **Rejected as next step** — D mostly re-samples the same spot OHLCV that C and B already showed cost-defeated; it adds little new information (the explicit reason E was chosen over D). |
| **Pause synthesis** | **Chosen** — three families missed the bar across both cost and idea-quality walls; disciplined stop with restart criteria. |

A pause is a legitimate, disciplined outcome — not a failure to be papered over with another
low-information drill. The full restart bar is in `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md`.

## 7. What is preserved (ready for a valid restart)

- All ingestion / materialization / validation infra (spot + derivatives), registry guards (BTC/ETH-only).
- The Family E diagnostic harness (`research/crypto/family_e/`, runner, 21 tests) — reusable for any fresh, pre-registered re-test.
- Frozen cost models (spot + perp) — unchanged.
- The two conditional reopen threads: (a) downtrend-conditioned funding reversion (fresh pre-registration + walk-forward); (b) deeper/forward-collected per-instrument OI (to power diagnostics 4/5).

## 8. Safety statement

No strategy, campaign, front gate, or approval created. `configs/approved_strategies.yaml`
remains `approved: []`. Paper/demo/live remain blocked. BTC/ETH only; no altcoins. FX archive
untouched. No frozen cost model changed. No trading/private API; no keys.

## Related documents

- `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md` (governance — restart bar)
- `CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md`
- `CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001_SYNTHESIS.md`
- `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SYNTHESIS.md`
- `../../CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`
