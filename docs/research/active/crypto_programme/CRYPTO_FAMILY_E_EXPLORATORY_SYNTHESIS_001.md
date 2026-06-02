# Crypto Family E — Exploratory Diagnostics 001 — Synthesis

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Date:** 2026-06-02
**Type:** Exploratory diagnostics synthesis. **No** strategy, campaign, front gate, or approval.

---

## 1. Executive summary

Family E (BTC/ETH perpetual funding / basis / OI) was tested with seven pre-registered
exploratory diagnostics on a 6.4-year USD-quoted Deribit-canonical dataset, against
matched nulls, all-in + 2× costs (incl. funding cashflow), and Holm multiple-comparisons
discipline. **No diagnostic reaches `candidate_for_front_gate`.** Diagnostics 1, 2, 3, 6, 7
are `rejected`; diagnostics 4, 5 are `blocked_low_power_oi`.

The single most notable exploratory signal in the entire crypto programme appeared in
regime conditioning: **funding mean reversion in a prior-7-day downtrend** is net-positive
after 2× stress in **both** BTC (+0.0027) and ETH (+0.0011). It nonetheless **fails the
frozen candidate bar** — it is a single regime slice conditioning a *rejected* base
diagnostic and is borderline/failing under full-family Holm. Per pre-registration, a tiny
regime slice must not override base failure, so it is recorded as a future-revisit thread,
not a candidate.

This is the third crypto factor family to fail to clear the bar (Family C and Family B both
closed `STATISTICAL_ONLY_COST_DEFEATED`). The honest prior held.

## 2. Data used

- Instruments: `BTC_PERP_USD`, `ETH_PERP_USD` (Deribit USD inverse perps, canonical).
- Funding: 56,186 hourly realized rows each (~99.86% cov), resampled to 6,953 complete 8h windows (sum of hourly).
- Perp OHLCV H1 (56,267), index H1 (56,186), basis_h1 (56,186), all 6.4y USD-quoted.
- OI: 180d aggregate daily (OKX rubik) — shallow, low-power.
- Frozen cost model: `CRYPTO_DERIVATIVES_COST_MODEL_001.md` (BTC 16 bps / ETH 18 bps all-in RT at H1/8h; 2× = 32/36 bps; funding cashflow long-pays-short).

## 3. Diagnostics run

1 funding mean reversion · 2 funding trend continuation · 3 basis compression/expansion ·
6 cross-asset confirmation · 7 regime conditioning (on 1–3). High-power on 6.4y data.

## 4. Diagnostics deferred / caveated

4 OI impulse · 5 funding/OI interaction — **low-power** (~180d aggregate daily OI only);
classified `blocked_low_power_oi`; not over-interpreted.

## 5. Result classification table

| Diagnostic | Label | Key result |
|-----------|-------|-----------|
| 1 Funding mean reversion | `rejected` | Pooled gross within null (shuffled p 0.26–0.83); BTC mildly +, ETH opposite (single-asset); all-in negative all horizons (8/24/72h). |
| 2 Funding trend continuation | `rejected` | No monotone gradient across k∈{3,6,9}; within null; all-in negative. Best cell k3/h24 all-in −0.0017. |
| 3 Basis compression/expansion | `rejected` | Best raw shuffled p≈0.013–0.017 (h4) → Holm-adj 0.22–0.27 (does NOT clear). Reversion AND expansion both raw-"significant" = forking-path artifact. |
| 4 OI impulse | `blocked_low_power_oi` | Only 180d aggregate daily OI; cannot power the test. |
| 5 Funding/OI interaction | `blocked_low_power_oi` | Same OI depth gap. |
| 6 Cross-asset confirmation | `rejected` | Agreement & disagreement (RV) within null; paired cost-defeated. |
| 7 Regime conditioning | `rejected` | One notable cell (downtrend funding reversion) net-positive after 2× in BTC+ETH but single-slice on rejected base; fails frozen bar. Basis-tercile cell is circular. |

## 6. Classification roll-up

- **rejected:** 1, 2, 3, 6, 7
- **statistical_only_cost_defeated:** none
- **cost_defeated:** none (effects did not even clear the null gross after MC, so they are rejected rather than cost-defeated)
- **blocked_data_quality:** none
- **blocked_low_power_oi:** 4, 5
- **candidate_for_front_gate:** **none**

## 7. Does any diagnostic clear the full bar?

| Gate | Best case (downtrend funding reversion regime cell) |
|------|------|
| Clears matched null after Holm | Partially — within-regime-family Holm yes (adj 0.032), full-family (incl. assets) borderline/failing |
| All-in net positive | Yes (pooled +0.0036) |
| 2× stress net positive | Yes (BTC +0.0027, ETH +0.0011) |
| BTC + ETH both supportive | Yes |
| Pooled supportive | Yes |
| Enough observations | Marginal (n=901 pooled; single regime slice) |
| Not dependent on one small regime slice | **No** — exists only in the downtrend tercile |
| Base diagnostic supportive | **No** — unconditioned diagnostic 1 was rejected |

→ **Fails the full candidate bar.** No diagnostic qualifies.

## 8. Single-asset vs robust

- Diagnostic 1 base: BTC mildly positive, ETH opposite-signed → single-asset, not robust.
- The notable regime cell: robust across BTC and ETH (both supportive, both 2×-positive) — its weakness is the single-regime-slice dependency and the rejected base, not single-asset.

## 9. Small-regime-slice dependency

Yes — the only net-positive-after-2× result depends entirely on one regime slice (prior-7d
downtrend) of a base diagnostic that is otherwise rejected. This is precisely the
forking-path risk the design pre-registered against. The basis|basis cell that also looked
"significant" is circular (the regime variable is the diagnostic's own signal).

## 10. Does OI need forward collection?

OI depth (180d aggregate daily) is the binding gap for diagnostics 4/5 only. The high-power
diagnostics (1/2/3/6) failed on deep funding/basis data, so OI is **not** the reason Family E
failed. Forward OI collection would only re-enable the two weakest diagnostics — it is not
the highest-value next step on its own.

## 11. Should Family E proceed / collect more data / move to Family D / pause?

- **Front-gate design:** not justified — no candidate cleared the bar.
- **OI forward collection:** low value alone (high-power diagnostics failed on non-OI data).
- **Family D (non-time bars):** low value — Family D mostly re-samples the same spot OHLCV that Families C and B already showed cost-defeated; it adds little new information (this is exactly why E was chosen over D).
- **Pause:** **recommended.** Three families (C cost-defeated, B cost-defeated, E rejected) now fail to clear the bar on this BTC/ETH corpus. The disciplined call is a programme-pause synthesis that decides whether to stop, carrying forward the one regime-conditional thread (downtrend funding reversion) and forward-OI collection as the only conditions that could ever reopen Family E — under fresh pre-registration with walk-forward, full-family multiple-comparisons, and BTC/ETH robustness, never a re-tune.

**Next sprint:** `NEXT_PROMPT_CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md` (a synthesis/decision sprint, not more diagnostics).

## 12. Safety statement

- No strategy created.
- No campaign created.
- No front gate created.
- No approval; `configs/approved_strategies.yaml` remains empty.
- Paper/demo/live remain blocked. BTC/ETH only. FX archive untouched. Cost model unchanged.
