# Next Prompt — After Non-USD Cross Data Population

The first-wave non-USD crosses are now **populated, validated, materialized,
and cost-profiled** from real OANDA practice data (8 crosses, ~14.7M M1 rows
+ ~4.05M materialized bars, parity-verified, over 2021-05-26 → 2026-05-26).
No factor discovery, screen, campaign, or strategy has been created.

The next sprint is **factor-discovery PLANNING only** — it produces a design
document and stops. It is **not** a campaign, **not** a front-gate screen,
**not** a strategy, and runs **no** train/validation/test evidence.

---

## Recommended next sprint — cross factor-discovery PLANNING

> Branch: `research-nonusd-cross-factor-discovery-planning-001`
>
> **Planning only — pre-screen, pre-campaign, pre-strategy.** Produce a
> design document that scopes (does NOT execute) factor discovery on the
> now-populated non-USD crosses, using the generalized multi-market
> front-gate framework (`MULTI_MARKET_FRONT_GATE_FRAMEWORK.md`). Run no
> backtest, build no signal, fit no model.
>
> The plan must:
>
> 1. **Open from the measured cost reality, not assumptions.** Use the
>    Phase-5 cost baseline (`NONUSD_CROSS_COST_BASELINE.md`): crosses are
>    wider and fatter-tailed than the majors (cross median 1.4–3.1p, p99
>    8.4–19.9p, std 1.3–3.2p vs majors 1.3–1.9p / 4.9–11.8p / 0.65–1.5p).
>    The cost wall is *higher* here. EUR_GBP (~1.4p) is the only
>    near-major-cost cross; rank candidate venues by measured cost.
> 2. **Prioritize the two intended uses (and only these):**
>    - **Independent replication of C1** — the one genuine factor on this
>      programme (fade H4+H1+M15 bullish alignment → reverts down) —
>      re-screened on non-collinear cross data via a *fresh, pre-registered*
>      screen with frozen thresholds. This is replication to settle the
>      residual-USD question, **NOT** a re-tune of C1's cost-defeated
>      USD-major result.
>    - **Breadth families** that were data-blocked on USD-only majors:
>      cross-sectional momentum, carry (AUD_JPY/NZD_JPY/EUR_JPY now have
>      real carry legs), and relative-value/cointegration — each framed
>      cost-first.
> 3. **Carry a do-not-revive list.** Every REJECTED campaign/lane stays
>    closed and must not be re-tuned: C022 pullback, C025/026 Donchian
>    ladder, C027 z-score, C028 RV spread, C029 range bars, C031 vol-managed
>    TSMOM, H03/H16 non-time-bar, and the M1/HTF directional lane. A cross
>    re-screen of C1 is the *one* sanctioned reuse, and only as a fresh
>    independent replication.
> 4. **Specify the cost-realism gate up front.** Every candidate must clear
>    net-of-cost using `forex_bot.research.cost_models` (round-trip measured
>    spread + two-legged carry, `debit_r`) *before* it earns a single
>    front-gate screen — exactly the bar the majors faced.
> 5. **Define explicit stop criteria.** State what result closes the cross
>    lane (as the majors' lane closed on cost), so the eventual discovery
>    work cannot drift into open-ended mining.
>
> Deliverable: **one planning document.** Do not create a hypothesis, run a
> screen, build entry/exit logic, create a campaign, approve anything, or
> enable paper/demo/live. Freeze stays intact.

---

## Guardrails carried into the next sprint

- No CAMPAIGN_032 / no campaign of any kind.
- No trading logic, no entry/exit logic, no signal construction.
- No train/validation/test evidence; no front-gate screen executed
  (planning only).
- No strategy approved; paper/demo/live stay blocked.
- No rejected idea revived except a **fresh, independent, pre-registered**
  C1 replication on cross data.
- Read-only research patterns only; data is already populated, so no new
  ingestion is required for planning.
