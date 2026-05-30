# C1 Cross-Replication Screen 001 — Plan & Baseline Audit

**Branch:** `research-c1-cross-replication-screen-001`
**Type:** factor **replication screen only**. Not a strategy, not a campaign, not
a trading front-gate, not a train/validation/test exercise.
**Date:** 2026-05-30.
**Freeze status:** intact. `approved: []`; paper/demo/live blocked; no broker/
trading-API calls.

> **The one question this sprint answers:** does the C1 factor — the programme's
> only genuine effect, validated on USD majors — **replicate on the non-USD
> crosses**, or was its magnitude a residual-USD-regime artifact?
>
> **It does NOT evaluate tradability.** C1 is already known to be cost-defeated
> on the majors; that question is settled and out of scope. This sprint asks
> *only* whether the effect is present (sign + magnitude + null-separation) on
> independent, non-collinear instruments.

---

## PHASE 0 — Baseline audit

Six bodies of prior work were reviewed to lock the replication design.

### 0.1 C1 factor validation (`C1_CROSS_PAIR_STUDY` / `project_c1_factor_validation`)

C1 = fade simultaneous **H4-trend + H1-trend + M15-aligned** bullish confluence;
price reverts down over 30–60 min (signed forward return negative). On the 7 USD
majors:
- **Sign-universal:** C1_long 60-min signed return **negative on 7/7** majors
  (P(neg) 0.495–0.541). The single most important replication target.
- **Magnitude-concentrated:** significant (|matched-Z| ≥ 3) only on **EUR_USD**
  (mZ60 −4.21) and **USD_JPY** (−3.55) — the discovery pairs; marginal GBP_USD
  (mZ30 −2.46, fades by 60); within-null on NZD/AUD/CHF/CAD.
- **Pair-space sign does NOT track the USD leg** (USD-base and USD-quote pairs
  both revert *down in pair space*) → early evidence **against** a pure
  "USD-strength-mean-reverts" artifact.
- **Cost-defeated everywhere:** reversion ≈0.65–0.73× spread even on the
  strongest pair → a factor, not an edge.

### 0.2 C1 high-vol front gate (`project_c1_factor_validation`)

C1's high-vol-conditioned path beats a **vol-matched null** (genuine,
C1-specific) but is **net-of-cost negative on all 3 pairs** → `FAIL_FRONT_GATE`;
the M1/HTF time-bar confluence *directional trading lane* is CLOSED on the
majors. Reopen only with new data via a **fresh screen, never a re-tune**. **This
sprint is that fresh screen — for replication, not for tradability.**

### 0.3 Cross-universe planning sprint (`NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001`)

Mapped the 15-instrument universe; crosses pull **breadth only** (history,
microstructure, cost walls unchanged). Generated 24 cross-enabled families,
fenced the re-tunes, ranked and shortlisted 5.

### 0.4 Shortlist (`CROSS_UNIVERSE_FACTOR_SHORTLIST`)

S1–S5. **S1 = F24 = independent C1 replication** ranked #1 (4.31): cheapest,
zero-new-data, zero researcher degrees-of-freedom, and its result *gates* the
value of S2–S5.

### 0.5 Next-direction decision (`NEXT_FACTOR_DISCOVERY_DIRECTION`)

Chose **S1**. Pre-stated three outcome branches (carried into Phase 5 verdict):
`C1_ARTIFACT` / `C1_GENUINE_BUT_COST_DEFEATED` / `C1_GENUINE_AND_COST_SURVIVING`
— none of which creates a campaign. This sprint maps those onto the required
verdict labels: `REPLICATION_FAILED` / `PARTIAL_REPLICATION` /
`REPLICATION_SUCCESS` (tradability deliberately excluded from all three).

### 0.6 C1 original specification (source of truth — read from code, not memory)

The frozen definition is `forex_bot.research.c1_factor_validation.BASELINE`
(a `@dataclass(frozen=True) C1Spec`), driven by constants in
`forex_bot.research.m1_response_matrix`. Verbatim:

| Element | Frozen value | Source |
|---|---|---|
| EMA fast | **20** | `mrm.EMA_FAST` |
| EMA slow | **50** | `mrm.EMA_SLOW` |
| EMA50 slope lookback | **3** completed bars | `mrm.SLOPE_LOOKBACK` |
| Trend leg rule | close vs EMA50 **AND** slope sign (`trend`) | `C1Spec.legs` |
| Aligned leg rule | close vs EMA50 only (`aligned`) | `C1Spec.legs` |
| Confluence legs (slowest→fastest) | **H4=trend, H1=trend, M15=aligned** | `C1Spec.legs` |
| Trigger | rising-edge of confluence | `m1_response_matrix` |
| Cooldown | **60 min** between events | `mrm.COOLDOWN_MIN` |
| Response horizons | **5, 10, 15, 30, 60 min** (primary 30/60) | `mrm.HORIZONS_MIN` |
| Response | **signed** forward mid return in pips (negative = reverts against confluence) | `c1v.build_c1_panel` |
| M1 source | `oanda-practice-m1` | runner |
| HTF source | `m1_materialized` (H4 via **H4M1**) | runner |
| Null seeds | 60 (random + session-matched), reproduces 200-seed mZ to rounding | original meta |

This definition is **frozen as of this commit** and may not change after any
cross result is observed (hard rule). Phase 1 re-states it as a pre-registration.

---

## Replication objective

Apply the **byte-for-byte identical** C1 analysis (same `BASELINE` spec, same
horizons, same cooldown, same null methodology, same sources) to the 8 populated
non-USD crosses, and read out — directly from committed CSVs — the same
quantities measured on the majors: event counts, signed response at 30/60 min,
t-stat, P(neg), and **session-matched null Z**. Compare the cross result to the
majors result to decide replication.

This is **replication, not re-tuning**: no threshold, EMA, slope, leg, horizon,
cooldown, or pair-filter is adjusted to improve any cross number. The only thing
that changes versus the original run is the **instrument list**.

## Success criteria (REPLICATION_SUCCESS — Phase 5 detail)

C1 replicates on the crosses if **all** hold:
1. **Sign stability** — C1_long 60-min signed return is **negative on a clear
   majority** of the 4 required crosses (and broadly across the optional 4),
   matching the 7/7 majors sign-universality.
2. **Null separation** — the effect **exceeds the session-matched null** (|mZ| ≥
   2 at 30 or 60 min) on **multiple** crosses, not a single best-of-8.
3. **Broadly consistent behavior** — magnitude is in a comparable band to the
   majors (not an order of magnitude different) and not driven by one outlier
   pair or a sign that flips between base/quote-JPY groups.

## Failure criteria (REPLICATION_FAILED — Phase 5 detail)

C1 fails to replicate if **any** dominant pattern holds:
1. **Inconsistent sign** — C1_long 60-min sign is mixed/positive across the
   required crosses (no majority negative).
2. **Indistinguishable from null** — no cross clears |mZ| ≥ 2; observed effects
   sit inside the matched-null band.
3. **Inconsistent behavior** — effect appears only on a single pair (best-of-8
   selection), or sign tracks the shared leg in a way that reveals a regime
   artifact rather than a confluence effect.

**PARTIAL_REPLICATION** is the middle: sign mostly stable but null-separation on
only some pairs, or magnitude materially weaker — mixed evidence.

> **Tradability is excluded from every branch.** Even REPLICATION_SUCCESS makes
> no trading claim; cross spreads are wider and C1 is already cost-defeated on
> the cheaper majors. A positive net-of-cost result is **not expected** and is
> not what is being measured.

---

## Hard boundaries (restated)

- No CAMPAIGN_032 / no campaign of any number.
- No strategy, no entry/exit rules, no trading system.
- No train/validation/test evidence; this is a descriptive replication screen.
- No strategy approved; paper/demo/live stay blocked.
- No trading-API calls.
- **The C1 definition is frozen and will not be altered after results are
  observed.**

## Data-access note (surfaced honestly)

The C1 analysis reads the populated cross M1 + materialized HTF bars from the
**local research database**, whose URL (with password) lives in `.env`. The
original C1 majors validation ran under the same local-DB read and explicitly
scoped its boundary as *"NO credentials beyond the local research DB URL."* This
sprint's hard rule "do not use credentials" is stricter. Pre-registration
(Phases 0–1) requires **no** data and is completed first; the actual replication
run (Phase 2) requires reading the local research DB. The handling of that
access is documented in the Phase-2 result doc and was confirmed with the user
before any data was read — pre-registration is locked *before* any data review,
exactly as a replication screen requires.
