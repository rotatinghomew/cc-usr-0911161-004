from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable

from benchmark_federation.benchmarks.contract import ContractError, bounded, finite_number, stable_hash
from benchmark_federation.comparability.model import (
    COMPARABLE,
    DEFAULT_RANGE_BY_METRIC,
    DEFAULT_RANGES,
    EXCLUDED_STATUSES,
    INCOMPARABLE,
    MISSING,
    WAIVED,
    MappingProfile,
    MetricObservation,
    MetricSpec,
    ReviewDefinition,
    alias_key,
)
from benchmark_federation.translation.metric_bridge import UNIT_FACTORS, canonical_term

RECOGNIZED = "recognized"
CONDITIONAL = "conditional"
NOT_RECOGNIZED = "not_recognized"
INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class MetricAttribution:
    metric_code: str
    status: str
    reason: str
    declared: bool
    required: bool
    weight: float
    threshold: float | None
    higher_is_better: bool
    raw_value: float | None
    normalized_value: float | None
    source_scale: str | None
    target_scale: str
    scale_factor: float | None
    passed: bool | None
    counted: bool
    evidence_ref: str | None
    evidence_digest: str | None
    waiver: dict[str, Any] | None = None
    sensitivity: dict[str, float] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric_code": self.metric_code,
            "status": self.status,
            "reason": self.reason,
            "declared": self.declared,
            "required": self.required,
            "weight": self.weight,
            "threshold": self.threshold,
            "higher_is_better": self.higher_is_better,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "source_scale": self.source_scale,
            "target_scale": self.target_scale,
            "scale_factor": self.scale_factor,
            "passed": self.passed,
            "counted": self.counted,
            "evidence_ref": self.evidence_ref,
            "evidence_digest": self.evidence_digest,
            "waiver": self.waiver,
            "sensitivity": self.sensitivity,
        }


@dataclass(frozen=True)
class ComparabilityAssessment:
    record_id: str
    baseline_family: str
    baseline_version: str
    baseline_digest: str
    mapping_id: str | None
    mapping_version: int | None
    mapping_digest: str | None
    mapping_language_pack: str | None
    mapping_resolved: bool
    mapping_reason: str | None
    policy: dict[str, Any]
    policy_digest: str
    metrics: tuple[MetricAttribution, ...]
    denominator: dict[str, Any]
    overall_pass_rate: float | None
    conclusion: str
    conclusion_reasons: tuple[str, ...]
    evidence_digests: tuple[str, ...] = ()
    measurement_digest: str = ""
    recorded_retest_pass_rate: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "baseline_family": self.baseline_family,
            "baseline_version": self.baseline_version,
            "baseline_digest": self.baseline_digest,
            "mapping_id": self.mapping_id,
            "mapping_version": self.mapping_version,
            "mapping_digest": self.mapping_digest,
            "mapping_language_pack": self.mapping_language_pack,
            "mapping_resolved": self.mapping_resolved,
            "mapping_reason": self.mapping_reason,
            "policy": self.policy,
            "policy_digest": self.policy_digest,
            "review_digest": self.review_digest,
            "metrics": [item.as_dict() for item in self.metrics],
            "denominator": self.denominator,
            "overall_pass_rate": self.overall_pass_rate,
            "conclusion": self.conclusion,
            "conclusion_reasons": list(self.conclusion_reasons),
            "evidence_digests": list(self.evidence_digests),
            "measurement_digest": self.measurement_digest,
            "recorded_retest_pass_rate": self.recorded_retest_pass_rate,
        }

    @property
    def digest(self) -> str:
        return stable_hash(self.as_dict())

    @property
    def review_digest(self) -> str:
        """Fingerprint of everything that is allowed to move a conclusion.

        Notably this excludes timestamps, so re-running the same review over
        the same evidence cannot produce a different review fingerprint.
        """
        return stable_hash({
            "baseline_digest": self.baseline_digest,
            "mapping_digest": self.mapping_digest,
            "policy_digest": self.policy_digest,
            "evidence_digest": stable_hash(list(self.evidence_digests)),
            "measurement_digest": self.measurement_digest,
        })

    def metric(self, metric_code: str) -> MetricAttribution | None:
        for item in self.metrics:
            if item.metric_code == metric_code:
                return item
        return None


@dataclass
class _Denominator:
    declared_weight: float = 0.0
    comparable_weight: float = 0.0
    passed_weight: float = 0.0
    waived_weight: float = 0.0
    missing_weight: float = 0.0
    incomparable_weight: float = 0.0
    comparable: list[str] = field(default_factory=list)
    waived: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    incomparable: list[str] = field(default_factory=list)

    def add(self, attribution: MetricAttribution) -> None:
        self.declared_weight += attribution.weight
        if attribution.status == COMPARABLE:
            self.comparable_weight += attribution.weight
            self.comparable.append(attribution.metric_code)
            if attribution.passed:
                self.passed_weight += attribution.weight
        elif attribution.status == WAIVED:
            self.waived_weight += attribution.weight
            self.waived.append(attribution.metric_code)
        elif attribution.status == MISSING:
            self.missing_weight += attribution.weight
            self.missing.append(attribution.metric_code)
        else:
            self.incomparable_weight += attribution.weight
            self.incomparable.append(attribution.metric_code)

    def as_dict(self) -> dict[str, Any]:
        share = self.comparable_weight / self.declared_weight if self.declared_weight else 0.0
        excluded_share = 1.0 - share
        waiver_share = self.waived_weight / self.declared_weight if self.declared_weight else 0.0
        return {
            "declared_metrics": len(self.comparable) + len(self.waived) + len(self.missing) + len(self.incomparable),
            "declared_weight": round(self.declared_weight, 6),
            "comparable_metrics": len(self.comparable),
            "comparable_weight": round(self.comparable_weight, 6),
            "passed_weight": round(self.passed_weight, 6),
            "excluded_weight": round(self.waived_weight + self.missing_weight + self.incomparable_weight, 6),
            "comparability_share": round(share, 6),
            "excluded_share": round(excluded_share, 6),
            "waiver_share_of_declared": round(waiver_share, 6),
            "comparable": list(self.comparable),
            "waived": list(self.waived),
            "missing": list(self.missing),
            "incomparable": list(self.incomparable),
        }


def normalize_metric_value(value: float, source_scale: str | None, target_scale: str | None,
                           mapping: MappingProfile, spec: MetricSpec | None) -> tuple[float, float]:
    source = canonical_term(source_scale or target_scale or mapping.default_target_scale or "fraction")
    target = canonical_term(target_scale or mapping.default_target_scale or "fraction")
    if source == target:
        factor = 1.0
    else:
        if not mapping.allows_conversion(source, target):
            raise ContractError(f"scale conversion {source}->{target} is not approved by mapping {mapping.mapping_id}")
        factor = UNIT_FACTORS[(source, target)]
    normalized = finite_number(value) * factor
    value_range = spec.value_range if spec and spec.value_range else None
    if value_range is None and spec is not None:
        value_range = DEFAULT_RANGE_BY_METRIC.get(spec.metric_code)
    if value_range is None:
        value_range = DEFAULT_RANGES.get(target)
    if value_range is not None:
        lower, upper = value_range
        epsilon = 1e-9
        if normalized < lower - epsilon or normalized > upper + epsilon:
            raise ContractError(
                f"metric {spec.metric_code if spec else '?'} normalized value {normalized!r} "
                f"falls outside {lower}..{upper}"
            )
    return normalized, factor


def _base_attribution(spec: MetricSpec, observation: MetricObservation | None,
                      target_scale: str) -> dict[str, Any]:
    return dict(
        metric_code=spec.metric_code,
        declared=True,
        required=spec.required,
        weight=spec.weight,
        threshold=spec.pass_threshold,
        higher_is_better=spec.higher_is_better,
        raw_value=observation.value if observation else None,
        normalized_value=None,
        source_scale=observation.source_scale if observation else None,
        target_scale=target_scale,
        scale_factor=None,
        passed=None,
        counted=False,
        evidence_ref=observation.evidence_ref if observation else None,
        evidence_digest=observation.evidence_digest if observation else None,
        sensitivity=None,
    )


def _excluded(spec: MetricSpec, observation: MetricObservation | None, status: str, reason: str,
              target_scale: str, waiver: dict[str, Any] | None = None) -> MetricAttribution:
    return MetricAttribution(status=status, reason=reason, waiver=waiver,
                             **_base_attribution(spec, observation, target_scale))


def _classify(record_id: str, spec: MetricSpec, observation: MetricObservation | None,
              review: ReviewDefinition, mapping: MappingProfile, at: str | None) -> MetricAttribution:
    baseline, policy = review.baseline, review.policy
    target_scale = canonical_term(spec.target_scale or mapping.default_target_scale)
    base = _base_attribution(spec, observation, target_scale)
    # Waiver presence is never enough: it must be honour-able at the review
    # moment, in scope, and approved by a named authority.
    waiver = observation.waiver if observation else None
    if waiver is not None:
        waiver_error = waiver.validation_error(spec.metric_code, at)
        if waiver_error:
            return MetricAttribution(
                status=INCOMPARABLE, reason=waiver_error, waiver=waiver.as_dict(), **base
            )
        if spec.required and not policy.allow_waiver_for_required:
            return MetricAttribution(
                status=INCOMPARABLE, reason="waiver_not_allowed_for_required_metric",
                waiver=waiver.as_dict(), **base,
            )
        if not observation.evidence_ref or not observation.evidence_digest:
            return MetricAttribution(
                status=WAIVED, reason="approved_waiver_without_evidence_reference",
                waiver=waiver.as_dict(), **base,
            )
        return MetricAttribution(status=WAIVED, reason="approved_waiver", waiver=waiver.as_dict(), **base)

    def excluded(status: str, reason: str) -> MetricAttribution:
        return _excluded(spec, observation, status, reason, target_scale)

    if observation is None or not observation.present:
        return excluded(MISSING, "no_retest_observation")
    if observation.source_metric:
        resolved = canonical_term(mapping.aliases.get(alias_key(observation.source_metric), ""))
        if resolved != canonical_term(spec.metric_code):
            return excluded(INCOMPARABLE, "source_metric_not_mapped_to_baseline_metric")
    if observation.benchmark_version and canonical_term(observation.benchmark_version) != canonical_term(
            baseline.benchmark_version):
        return excluded(INCOMPARABLE, "benchmark_version_mismatch")
    if observation.mapping_confidence is not None and observation.mapping_confidence < mapping.confidence_floor:
        return excluded(INCOMPARABLE, "semantic_mapping_below_floor")
    if not observation.evidence_ref or not observation.evidence_digest:
        return excluded(MISSING, "evidence_reference_missing")
    if spec.pass_threshold is None:
        return excluded(INCOMPARABLE, "baseline_threshold_not_declared")

    try:
        normalized, factor = normalize_metric_value(observation.value, observation.source_scale,
                                                    target_scale, mapping, spec)
    except ContractError as exc:
        message = str(exc)
        reason = "unsupported_scale_conversion" if "not approved" in message else "normalized_value_out_of_range"
        return excluded(INCOMPARABLE, reason)

    passed = normalized >= spec.pass_threshold if spec.higher_is_better else normalized <= spec.pass_threshold
    base.update(normalized_value=normalized, scale_factor=factor, passed=passed, counted=True)
    return MetricAttribution(status=COMPARABLE, reason="comparable", **base)


def _sensitivity(spec: MetricSpec, passed_weight: float, comparable_weight: float) -> dict[str, float]:
    """Show how the *same excluded metric* would move the rate if wrongly imputed.

    This is descriptive only: excluded metrics never enter the reported
    denominator or conclusion.
    """
    if spec.weight <= 0:
        return {"if_counted_as_pass": 0.0, "if_counted_as_failure": 0.0}
    as_pass = (passed_weight + spec.weight) / (comparable_weight + spec.weight)
    as_fail = passed_weight / (comparable_weight + spec.weight)
    return {"if_counted_as_pass": round(as_pass, 6), "if_counted_as_failure": round(as_fail, 6)}


def _append_exclusion_reasons(reasons: list[str], denominator: "_Denominator",
                              skip_headline: bool = False) -> None:
    if denominator.waived:
        reasons.append("waived_metrics_excluded")
    if denominator.missing:
        reasons.append("missing_metrics_excluded")
    if denominator.incomparable:
        reasons.append("incomparable_metrics_excluded")
    if not skip_headline:
        reasons.append("excluded_metrics_not_counted")


def assess(record: Any, review: ReviewDefinition, *, at: str | None = None) -> ComparabilityAssessment:
    if not review.baseline.metrics:
        raise ContractError("baseline must declare at least one metric")
    specs = list(review.baseline.metrics)
    observations = {item.metric_code: item for item in review.for_record(record.record_id)}
    # Waivers are evaluated at the review moment, not at audit time: a waiver
    # that expired before this review cannot be silently honoured later.
    at = at or review.reviewed_at
    if at is None and any(item.waiver is not None for item in observations.values()):
        raise ContractError("a review containing waivers needs reviewed_at to evaluate waiver validity")
    mapping = review.mapping_for(record, strict=False)
    unmapped = mapping is None
    if mapping is None:
        payload = getattr(record, "payload", {}) or {}
        mapping = MappingProfile(
            mapping_id="unresolved",
            language_pack=str(payload.get("language_pack") or "") or None,
            aliases={},
            confidence_floor=1.0,
            approved_conversions=(),
            default_target_scale=review.mappings[0].default_target_scale,
        )
    unknown = sorted(set(observations) - {spec.metric_code for spec in specs})
    payload = getattr(record, "payload", {}) or {}
    record_family = canonical_term(payload.get("benchmark_family")) if payload.get("benchmark_family") else ""
    record_version = canonical_term(payload.get("benchmark_version")) if payload.get("benchmark_version") else ""
    if record_family and record_family != canonical_term(review.baseline.benchmark_family):
        record_level_problem = "baseline_family_mismatch"
    elif record_version and record_version != canonical_term(review.baseline.benchmark_version):
        record_level_problem = "baseline_version_mismatch"
    else:
        record_level_problem = None
    attributions: list[MetricAttribution] = []
    denominator = _Denominator()
    for spec in specs:
        if record_level_problem:
            attribution = _excluded(spec, observations.get(spec.metric_code), INCOMPARABLE,
                                    record_level_problem,
                                    canonical_term(spec.target_scale or mapping.default_target_scale))
        elif unmapped:
            attribution = _excluded(spec, observations.get(spec.metric_code), INCOMPARABLE,
                                    "language_pack_has_no_pinned_mapping",
                                    canonical_term(spec.target_scale or mapping.default_target_scale))
        else:
            attribution = _classify(record.record_id, spec, observations.get(spec.metric_code), review, mapping, at)
        attributions.append(attribution)
        denominator.add(attribution)

    # Unknown observations are surfaced, never silently added to the denominator.
    undeclared = [{
        "metric_code": code,
        "reason": "observed_metric_not_in_baseline_catalog",
        "evidence_ref": observations[code].evidence_ref,
        "evidence_digest": observations[code].evidence_digest,
    } for code in unknown]

    # Attach sensitivity after the comparable denominator is known.
    with_sensitivity = []
    for item in attributions:
        if item.status in EXCLUDED_STATUSES:
            spec = next(spec for spec in specs if spec.metric_code == item.metric_code)
            item = replace(
                item,
                sensitivity=_sensitivity(spec, denominator.passed_weight, denominator.comparable_weight),
            )
        with_sensitivity.append(item)
    attributions = tuple(with_sensitivity)

    overall = (denominator.passed_weight / denominator.comparable_weight
               if denominator.comparable_weight > 0 else None)
    comparability_share = (denominator.comparable_weight / denominator.declared_weight
                           if denominator.declared_weight else 0.0)
    waiver_share = (denominator.waived_weight / denominator.declared_weight
                    if denominator.declared_weight else 0.0)

    reasons: list[str] = []
    excluded_any = bool(denominator.waived or denominator.missing or denominator.incomparable)
    # Ordering matters.  The comparability floor gates whether *any* verdict is
    # admissible: excluded metrics are neither failures nor zeros, so a thin
    # comparable denominator must yield insufficient evidence rather than a
    # pass or a failure.  Once the denominator is admissible, the measured
    # pass rate is what decides recognition; excluded metrics can only keep it
    # from being unconditional.
    if overall is None:
        conclusion = INSUFFICIENT_EVIDENCE
        reasons.append("no_comparable_metrics")
    elif comparability_share < review.policy.hard_comparability_floor:
        conclusion = INSUFFICIENT_EVIDENCE
        reasons.append("comparability_below_hard_floor")
        _append_exclusion_reasons(reasons, denominator)
    elif comparability_share < review.policy.minimum_comparability:
        conclusion = INSUFFICIENT_EVIDENCE
        reasons.append("comparability_below_minimum")
        _append_exclusion_reasons(reasons, denominator)
    elif overall < review.policy.pass_threshold:
        conclusion = NOT_RECOGNIZED
        reasons.append("observed_pass_rate_below_threshold")
        _append_exclusion_reasons(reasons, denominator)
    elif waiver_share > review.policy.max_waiver_share:
        # Too much of the declared denominator is waived for an unconditional
        # verdict, but a waiver is not a measured failure.  The record leaves
        # the aggregate with insufficient evidence rather than being rejected.
        conclusion = INSUFFICIENT_EVIDENCE
        reasons.append("waiver_share_above_limit")
        _append_exclusion_reasons(reasons, denominator)
    elif excluded_any:
        conclusion = CONDITIONAL if review.policy.allow_conditional else NOT_RECOGNIZED
        reasons.append("non_comparable_metrics_excluded")
        _append_exclusion_reasons(reasons, denominator, skip_headline=True)
    else:
        conclusion = RECOGNIZED
        reasons.append("all_declared_metrics_comparable")

    denominator_payload = denominator.as_dict()
    denominator_payload["undeclared_observations"] = undeclared
    denominator_payload["effective_overall_pass_rate"] = None if overall is None else round(overall, 6)

    evidence_digests = tuple(sorted({
        item.evidence_digest for item in observations.values() if item.evidence_digest
    }))
    recorded_rate = _recorded_rate(record)
    measurement_digest = stable_hash({
        "record_id": record.record_id,
        "baseline_digest": review.baseline.digest,
        "mapping_digest": mapping.digest if not unmapped else None,
        "policy_digest": stable_hash(review.policy.as_dict()),
        "recorded_retest_pass_rate": recorded_rate,
        "observations": {
            code: {
                "value": item.value,
                "source_scale": item.source_scale,
                "source_metric": item.source_metric,
                "mapping_confidence": item.mapping_confidence,
                "benchmark_version": item.benchmark_version,
                "evidence_ref": item.evidence_ref,
                "evidence_digest": item.evidence_digest,
                "waiver": item.waiver.as_dict() if item.waiver else None,
            }
            for code, item in sorted(observations.items())
        },
    })

    return ComparabilityAssessment(
        record_id=record.record_id,
        baseline_family=review.baseline.benchmark_family,
        baseline_version=review.baseline.benchmark_version,
        baseline_digest=review.baseline.digest,
        mapping_id=mapping.mapping_id if not unmapped else None,
        mapping_version=mapping.mapping_version if not unmapped else None,
        mapping_digest=mapping.digest if not unmapped else None,
        mapping_language_pack=mapping.language_pack,
        mapping_resolved=not unmapped,
        mapping_reason=None if not unmapped else "language_pack_has_no_pinned_mapping",
        policy=review.policy.as_dict(),
        policy_digest=stable_hash(review.policy.as_dict()),
        metrics=attributions,
        denominator=denominator_payload,
        overall_pass_rate=None if overall is None else round(overall, 6),
        conclusion=conclusion,
        conclusion_reasons=tuple(reasons),
        evidence_digests=evidence_digests,
        measurement_digest=measurement_digest,
        recorded_retest_pass_rate=recorded_rate,
    )


def _recorded_rate(record: Any) -> float | None:
    payload = getattr(record, "payload", {}) or {}
    value = payload.get("retest_pass_rate")
    if value is None or value == "":
        return None
    try:
        number = finite_number(value)
    except ContractError:
        return None
    if number > 1.0:
        number /= 100.0
    return bounded(number)


def assess_many(records: Iterable[Any], review: ReviewDefinition) -> list[ComparabilityAssessment]:
    return [assess(record, review) for record in records]


def summarize(assessments: Iterable[ComparabilityAssessment]) -> dict[str, Any]:
    rows = list(assessments)
    conclusions: dict[str, int] = {}
    statuses: dict[str, int] = {COMPARABLE: 0, MISSING: 0, WAIVED: 0, INCOMPARABLE: 0}
    reasons: dict[str, int] = {}
    for row in rows:
        conclusions[row.conclusion] = conclusions.get(row.conclusion, 0) + 1
        for reason in row.conclusion_reasons:
            reasons[reason] = reasons.get(reason, 0) + 1
        for item in row.metrics:
            statuses[item.status] = statuses.get(item.status, 0) + 1
    # A record only enters the aggregate when its own denominator is
    # admissible.  Records that failed the comparability floor are reported
    # but never contribute a pass rate (and never a zero).
    included = [
        row.overall_pass_rate for row in rows
        if row.overall_pass_rate is not None and row.conclusion != INSUFFICIENT_EVIDENCE
    ]
    recorded = [row.recorded_retest_pass_rate for row in rows
                if row.recorded_retest_pass_rate is not None]
    return {
        "records": len(rows),
        "conclusions": conclusions,
        "conclusion_reasons": reasons,
        "metric_statuses": statuses,
        "records_with_comparable_denominator": sum(
            1 for row in rows if row.overall_pass_rate is not None
        ),
        "records_in_aggregate": len(included),
        "records_excluded_from_aggregate": len(rows) - len(included),
        "mean_effective_pass_rate": round(sum(included) / len(included), 6) if included else None,
        "mean_recorded_pass_rate": round(sum(recorded) / len(recorded), 6) if recorded else None,
        "excluded_records": sorted(
            row.record_id for row in rows if row.conclusion == INSUFFICIENT_EVIDENCE
        ),
    }
