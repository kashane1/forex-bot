# Crypto Family E Diagnostic 7 — Regime Conditioning Result

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Type:** Exploratory diagnostic only — highest forking-path risk.

**Frozen regimes:** volatility, trend, abs_funding, basis.

Applied to base diagnostics 1 (funding reversion h24), 2 (continuation k6 h24), 3 (basis reversion h24). Tercile 0=low, 1=mid, 2=high of the regime variable. Holm discipline applies; a tiny regime slice must not override base failure.

**Classification impact:** 1 non-circular regime cell(s) flagged notable; the strongest is downtrend-conditioned funding mean reversion (BTC+ETH supportive, both 2×-stress-positive). It FAILS the frozen candidate bar: it is a single regime slice conditioning a REJECTED base diagnostic and is borderline/failing under full-family Holm (incl. assets). Per pre-registration a tiny regime slice must not override base failure → no front-gate candidate this sprint, but it is the single thread worth a future fresh-pre-registered, walk-forward re-test.

## Notable regime cells (pre-Holm flags) — honest audit

Cells where pooled gross>0 AND all-in>0 AND shuffled p<0.05, recomputed per asset (BTC/ETH) with 2× stress. A cell is a `candidate_for_front_gate` ONLY if it is non-circular, BTC+ETH both supportive, both 2×-stress-positive, survives FULL-family Holm, AND is not merely a single regime slice on a rejected base.

### diag1_funding_reversion_h24 · regime=trend · tercile=0

- pooled: n=901, gross=0.004687, all-in=0.003611, 2×=0.001910, shuffled p=0.0000
- BTC_PERP_USD: n=445, gross=0.005389, all-in=0.004328, 2×=0.002728, shuffled p=0.0000
- ETH_PERP_USD: n=456, gross=0.004002, all-in=0.002912, 2×=0.001112, shuffled p=0.0460
- BTC+ETH both supportive: True; both 2×-stress-positive: True
- **Verdict:** Notable but DOES NOT meet the frozen candidate bar: single regime slice on a REJECTED base diagnostic; borderline/failing under full-family Holm (incl. assets).

### diag3_basis_reversion_h24 · regime=basis · tercile=0

- pooled: n=10854, gross=0.002469, all-in=0.000713, 2×=-0.000987, shuffled p=0.0000
- BTC_PERP_USD: n=5427, gross=0.001900, all-in=0.000210, 2×=-0.001390, shuffled p=0.0050
- ETH_PERP_USD: n=5427, gross=0.003038, all-in=0.001216, 2×=-0.000584, shuffled p=0.0000
- BTC+ETH both supportive: True; both 2×-stress-positive: False
- **Verdict:** CIRCULAR (regime variable = the diagnostic's own signal) — not an independent effect.

## diag1_funding_reversion_h24

| Regime | Tercile | n | gross | all-in | 2× stress | shuffled p |
|--------|--------:|--:|------:|-------:|----------:|-----------:|
| volatility | 0 | 468 | 0.000722 | -0.000373 | -0.002062 | 0.6420 |
| volatility | 1 | 815 | -0.002163 | -0.003174 | -0.004878 | 0.1020 |
| volatility | 2 | 1405 | 0.000422 | -0.000402 | -0.002104 | 0.6680 |
| trend | 0 | 901 | 0.004687 | 0.003611 | 0.001910 | 0.0000 |
| trend | 1 | 601 | -0.002174 | -0.003239 | -0.004932 | 0.1640 |
| trend | 2 | 1183 | -0.003218 | -0.003963 | -0.005666 | 0.0090 |
| abs_funding | 0 | 0 | 0.000000 | 0.000000 | 0.000000 | — |
| abs_funding | 1 | 509 | 0.003329 | 0.001780 | 0.000141 | 0.0770 |
| abs_funding | 2 | 2179 | -0.001159 | -0.001943 | -0.003657 | 0.1660 |
| basis | 0 | 999 | 0.000229 | -0.000746 | -0.002444 | 0.8500 |
| basis | 1 | 674 | -0.001351 | -0.002330 | -0.004028 | 0.3330 |
| basis | 2 | 1015 | -0.000147 | -0.000997 | -0.002699 | 0.9050 |

## diag2_continuation_k6_h24

| Regime | Tercile | n | gross | all-in | 2× stress | shuffled p |
|--------|--------:|--:|------:|-------:|----------:|-----------:|
| volatility | 0 | 2735 | 0.000743 | -0.001243 | -0.002941 | 0.4620 |
| volatility | 1 | 2708 | -0.000173 | -0.002235 | -0.003931 | 0.8600 |
| volatility | 2 | 2541 | -0.001224 | -0.003434 | -0.005129 | 0.1370 |
| trend | 0 | 2234 | -0.002735 | -0.004690 | -0.006392 | 0.0010 |
| trend | 1 | 2628 | -0.000500 | -0.002497 | -0.004191 | 0.5840 |
| trend | 2 | 3106 | 0.001783 | -0.000467 | -0.002161 | 0.0330 |
| abs_funding | 0 | 1582 | -0.003235 | -0.005002 | -0.006706 | 0.0000 |
| abs_funding | 1 | 2668 | -0.001141 | -0.003009 | -0.004703 | 0.1800 |
| abs_funding | 2 | 3734 | 0.001772 | -0.000598 | -0.002293 | 0.0340 |
| basis | 0 | 2625 | 0.000120 | -0.001936 | -0.003633 | 0.8930 |
| basis | 1 | 2656 | 0.000377 | -0.001654 | -0.003350 | 0.6900 |
| basis | 2 | 2703 | -0.001059 | -0.003219 | -0.004915 | 0.2340 |

## diag3_basis_reversion_h24

| Regime | Tercile | n | gross | all-in | 2× stress | shuffled p |
|--------|--------:|--:|------:|-------:|----------:|-----------:|
| volatility | 0 | 1855 | -0.000452 | -0.002063 | -0.003764 | 0.6020 |
| volatility | 1 | 6174 | -0.000725 | -0.002324 | -0.004023 | 0.1210 |
| volatility | 2 | 13677 | 0.000609 | -0.000964 | -0.002664 | 0.0590 |
| trend | 0 | 8933 | 0.001111 | -0.000524 | -0.002223 | 0.0080 |
| trend | 1 | 4816 | -0.000153 | -0.001755 | -0.003455 | 0.7470 |
| trend | 2 | 7900 | -0.000806 | -0.002320 | -0.004021 | 0.0740 |
| abs_funding | 0 | 6129 | 0.000033 | -0.001632 | -0.003329 | 0.9360 |
| abs_funding | 1 | 6577 | -0.000386 | -0.002028 | -0.003727 | 0.4090 |
| abs_funding | 2 | 8669 | 0.000349 | -0.001130 | -0.002833 | 0.3650 |
| basis | 0 | 10854 | 0.002469 | 0.000713 | -0.000987 | 0.0000 |
| basis | 1 | 0 | 0.000000 | 0.000000 | 0.000000 | — |
| basis | 2 | 10854 | -0.002195 | -0.003607 | -0.005307 | 0.0000 |

## Forking-path warning

Many regime cells × diagnostics × terciles → high multiple-comparisons risk. Any single favorable cell is treated as a forking-path artifact unless the base diagnostic also passed and the cell survives Holm.

