"""Comparison harness — verifier output vs bespoke reference.

Reads two JSON-shaped summaries (verifier ``parity_summary.json`` and
the committed bespoke reference) and emits a structured comparison
report classified under the divergence taxonomy.

Tolerance ladder, inherited from
``docs/research/LEAN_PARITY_COMPARISON_METHOD.md``:

- trade count (per pair & total): OK ≤ 5%, WARN ≤ 15%, FAIL > 15%.
- expectancy R (per pair): OK ≤ 0.03 R, WARN ≤ 0.10 R, FAIL > 0.10 R.
- return % (per pair): OK ≤ 0.5 pp, WARN ≤ 2.0 pp, FAIL > 2.0 pp.

A pair's status is the worst of its metrics; the overall status is
the worst of all pairs and the total-trade comparison. Missing pairs
and malformed inputs are FAIL.
"""

from __future__ import annotations

from pathlib import Path

from research.parity_verifier.models import (
    ComparisonReport,
    ComparisonStatus,
    DivergenceClassification,
    PairComparison,
    VerifierResult,
)

TRADE_COUNT_OK_PCT = 5.0
TRADE_COUNT_WARN_PCT = 15.0
EXPECTANCY_OK = 0.03
EXPECTANCY_WARN = 0.10
RETURN_PCT_OK = 0.5
RETURN_PCT_WARN = 2.0


def _trade_count_status(delta_pct: float | None) -> ComparisonStatus:
    if delta_pct is None:
        return ComparisonStatus.FAIL
    mag = abs(delta_pct)
    if mag <= TRADE_COUNT_OK_PCT:
        return ComparisonStatus.OK
    if mag <= TRADE_COUNT_WARN_PCT:
        return ComparisonStatus.WARN
    return ComparisonStatus.FAIL


def _expectancy_status(delta: float | None) -> ComparisonStatus:
    if delta is None:
        return ComparisonStatus.OK  # neutral — not all results carry expectancy
    mag = abs(delta)
    if mag <= EXPECTANCY_OK:
        return ComparisonStatus.OK
    if mag <= EXPECTANCY_WARN:
        return ComparisonStatus.WARN
    return ComparisonStatus.FAIL


def _return_pct_status(delta: float | None) -> ComparisonStatus:
    if delta is None:
        return ComparisonStatus.OK
    mag = abs(delta)
    if mag <= RETURN_PCT_OK:
        return ComparisonStatus.OK
    if mag <= RETURN_PCT_WARN:
        return ComparisonStatus.WARN
    return ComparisonStatus.FAIL


def _worse(a: ComparisonStatus, b: ComparisonStatus) -> ComparisonStatus:
    order = {
        ComparisonStatus.OK: 0,
        ComparisonStatus.WARN: 1,
        ComparisonStatus.FAIL: 2,
        ComparisonStatus.BLOCKED: 3,
    }
    return a if order[a] >= order[b] else b


def _classify(status: ComparisonStatus) -> DivergenceClassification:
    """Default classification mapping. Phase 6 may refine to a more
    specific bucket once a divergence is localized; the comparison
    itself starts with the most general label."""

    if status is ComparisonStatus.OK:
        return DivergenceClassification.NONE
    if status is ComparisonStatus.BLOCKED:
        return DivergenceClassification.UNKNOWN
    return DivergenceClassification.UNKNOWN


def compare(
    *,
    verifier: VerifierResult,
    bespoke_reference: dict,
    verifier_result_path: str | Path | None = None,
    bespoke_reference_path: str | Path,
) -> ComparisonReport:
    """Compare a verifier result to the bespoke reference JSON.

    The bespoke reference is a dict (loaded via
    ``data_loader.load_bespoke_reference``) — passing the raw dict
    rather than a model lets the comparison evolve independently of
    minor schema additions on the bespoke side.
    """

    bespoke_pairs = {pair["instrument"]: pair for pair in bespoke_reference.get("pairs", [])}
    verifier_pairs = {pair.instrument: pair for pair in verifier.pairs}
    notes: list[str] = []
    rows: list[PairComparison] = []
    overall = ComparisonStatus.OK
    overall_class = DivergenceClassification.NONE

    for instrument in bespoke_pairs:
        ref = bespoke_pairs[instrument]
        result = verifier_pairs.get(instrument)
        bespoke_trades = int(ref.get("trades", 0))
        bespoke_exp = ref.get("expectancy_r")
        bespoke_ret = ref.get("return_pct")

        if result is None:
            rows.append(
                PairComparison(
                    instrument=instrument,
                    bespoke_trades=bespoke_trades,
                    verifier_trades=None,
                    trade_count_delta_pct=None,
                    bespoke_expectancy_r=bespoke_exp,
                    verifier_expectancy_r=None,
                    expectancy_r_delta=None,
                    bespoke_return_pct=bespoke_ret,
                    verifier_return_pct=None,
                    return_pct_delta=None,
                    status=ComparisonStatus.FAIL,
                    classification=DivergenceClassification.DATA_MISMATCH,
                )
            )
            notes.append(f"{instrument}: missing from verifier result")
            overall = _worse(overall, ComparisonStatus.FAIL)
            overall_class = DivergenceClassification.DATA_MISMATCH
            continue

        trade_delta_pct: float | None
        if bespoke_trades == 0:
            trade_delta_pct = None
        else:
            trade_delta_pct = (result.trades - bespoke_trades) / bespoke_trades * 100.0
        exp_delta = (
            None
            if (bespoke_exp is None or result.expectancy_r is None)
            else result.expectancy_r - bespoke_exp
        )
        ret_delta = (
            None
            if (bespoke_ret is None or result.return_pct is None)
            else result.return_pct - bespoke_ret
        )
        pair_status = _worse(
            _trade_count_status(trade_delta_pct),
            _worse(_expectancy_status(exp_delta), _return_pct_status(ret_delta)),
        )
        classification = _classify(pair_status)
        rows.append(
            PairComparison(
                instrument=instrument,
                bespoke_trades=bespoke_trades,
                verifier_trades=result.trades,
                trade_count_delta_pct=trade_delta_pct,
                bespoke_expectancy_r=bespoke_exp,
                verifier_expectancy_r=result.expectancy_r,
                expectancy_r_delta=exp_delta,
                bespoke_return_pct=bespoke_ret,
                verifier_return_pct=result.return_pct,
                return_pct_delta=ret_delta,
                status=pair_status,
                classification=classification,
            )
        )
        overall = _worse(overall, pair_status)
        if classification is not DivergenceClassification.NONE:
            overall_class = classification

    bespoke_total = int(bespoke_reference.get("total_trades", 0))
    if bespoke_total == 0:
        total_delta_pct: float | None = None
        total_status = ComparisonStatus.FAIL
    else:
        total_delta_pct = (verifier.total_trades - bespoke_total) / bespoke_total * 100.0
        total_status = _trade_count_status(total_delta_pct)
    overall = _worse(overall, total_status)
    if total_status is not ComparisonStatus.OK and overall_class is DivergenceClassification.NONE:
        overall_class = DivergenceClassification.UNKNOWN

    return ComparisonReport(
        bespoke_reference_path=str(bespoke_reference_path),
        verifier_result_path=str(verifier_result_path) if verifier_result_path else None,
        pairs=rows,
        bespoke_total_trades=bespoke_total,
        verifier_total_trades=verifier.total_trades,
        total_trade_count_delta_pct=total_delta_pct,
        overall_status=overall,
        overall_classification=overall_class,
        notes=notes,
        strategy_evidence=False,
    )


def blocked_report(
    *,
    bespoke_reference_path: str | Path,
    bespoke_reference: dict,
    reason: str,
) -> ComparisonReport:
    """Return a BLOCKED comparison report — used when the verifier
    could not produce a result (e.g. the gitignored CSVs are absent
    locally). The bespoke side is still recorded so the report is
    structurally identical to a successful one."""

    bespoke_pairs = bespoke_reference.get("pairs", [])
    rows = [
        PairComparison(
            instrument=pair["instrument"],
            bespoke_trades=int(pair.get("trades", 0)),
            verifier_trades=None,
            trade_count_delta_pct=None,
            bespoke_expectancy_r=pair.get("expectancy_r"),
            verifier_expectancy_r=None,
            expectancy_r_delta=None,
            bespoke_return_pct=pair.get("return_pct"),
            verifier_return_pct=None,
            return_pct_delta=None,
            status=ComparisonStatus.BLOCKED,
            classification=DivergenceClassification.UNKNOWN,
        )
        for pair in bespoke_pairs
    ]
    return ComparisonReport(
        bespoke_reference_path=str(bespoke_reference_path),
        verifier_result_path=None,
        pairs=rows,
        bespoke_total_trades=int(bespoke_reference.get("total_trades", 0)),
        verifier_total_trades=None,
        total_trade_count_delta_pct=None,
        overall_status=ComparisonStatus.BLOCKED,
        overall_classification=DivergenceClassification.UNKNOWN,
        notes=[reason],
        strategy_evidence=False,
    )
