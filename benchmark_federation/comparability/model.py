from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from benchmark_federation.benchmarks.contract import (
    ContractError,
    bounded,
    finite_number,
    identifier,
    stable_hash,
)
from benchmark_federation.translation.metric_bridge import UNIT_FACTORS, canonical_term

COMPARABLE = "comparable"
MISSING = "missing"
WAIVED = "waived"
INCOMPARABLE = "incomparable"
METRIC_STATUSES = (COMPARABLE, MISSING, WAIVED, INCOMPARABLE)
EXCLUDED_STATUSES = (MISSING, WAIVED, INCOMPARABLE)

DEFAULT_RANGES: dict[str, tuple[float, float]] = {
    "fraction": (0.0, 1.0),
    "percent": (0.0, 100.0),
    "seconds": (0.0, math.inf),
    "milliseconds": (0.0, math.inf),
}
DEFAULT_RANGE_BY_METRIC: dict[str, tuple[float, float]] = {
    "retest_pass_rate": (0.0, 1.0),
    "pass_threshold": (0.0, 1.0),
    "accuracy": (0.0, 1.0),
    "f1": (0.0, 1.0),
    "latency": (0.0, math.inf),
    "throughput": (0.0, math.inf),
}


def _number(value: Any, *, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    result = finite_number(value)
    if not math.isfinite(result):
        raise ContractError("numeric value must be finite")
    return result


def _text(value: Any, *, default: str = "") -> str:
    return str(value if value is not None else default).strip()


def alias_key(value: Any) -> str:
    """Normalize a source metric label the same way alias sources are keyed."""
    return canonical_term(value) or " ".join(str(value or "").split()).casefold()


def _alias_map(value: Mapping[str, Any]) -> dict[str, str]:
    """Normalize a language-pack alias table without collapsing distinct keys.

    ``canonical_term`` is ASCII-only, so a non-Latin source metric (e.g. a
    Chinese or Thai label) normalizes to an empty string.  Such a label is a
    legitimate source identifier: keep it verbatim (case-folded) instead of
    silently merging every non-Latin alias into one entry.  Two different
    source labels that normalize to the same key are a contract error rather
    than a last-writer-wins overwrite.
    """
    result: dict[str, str] = {}
    for raw_key, raw_target in dict(value or {}).items():
        key = alias_key(raw_key)
        if not key:
            raise ContractError("mapping alias source is empty")
        target = canonical_term(raw_target)
        if not target:
            raise ContractError("mapping alias target has no canonical metric code")
        if key in result and result[key] != target:
            raise ContractError(f"mapping alias {raw_key!r} resolves to conflicting targets")
        result[key] = target
    return result


@dataclass(frozen=True)
class MetricSpec:
    """A metric declared by the shared baseline (the comparison denominator)."""

    metric_code: str
    pass_threshold: float | None = None
    higher_is_better: bool = True
    weight: float = 1.0
    required: bool = True
    target_scale: str | None = None
    value_range: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "metric_code", identifier(self.metric_code))
        if not math.isfinite(finite_number(self.weight)) or finite_number(self.weight) <= 0:
            raise ContractError("metric weight must be positive")
        if self.pass_threshold is not None:
            object.__setattr__(self, "pass_threshold", finite_number(self.pass_threshold))
        if self.value_range is not None:
            lower, upper = finite_number(self.value_range[0]), finite_number(self.value_range[1])
            if lower > upper:
                raise ContractError("metric value range is inverted")
            object.__setattr__(self, "value_range", (lower, upper))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "MetricSpec":
        if not isinstance(value, Mapping):
            raise ContractError("metric spec must be an object")
        raw_range = value.get("value_range")
        value_range = None
        if isinstance(raw_range, (list, tuple)) and len(raw_range) == 2:
            value_range = (finite_number(raw_range[0]), finite_number(raw_range[1]))
        return cls(
            metric_code=str(value.get("metric_code") or value.get("code") or ""),
            pass_threshold=_number(value.get("pass_threshold")),
            higher_is_better=bool(value.get("higher_is_better", True)),
            weight=float(value.get("weight", 1.0)),
            required=bool(value.get("required", True)),
            target_scale=_text(value.get("target_scale")) or None,
            value_range=value_range,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric_code": self.metric_code,
            "pass_threshold": self.pass_threshold,
            "higher_is_better": self.higher_is_better,
            "weight": self.weight,
            "required": self.required,
            "target_scale": self.target_scale,
            "value_range": list(self.value_range) if self.value_range else None,
        }


@dataclass(frozen=True)
class Baseline:
    """The pinned benchmark version and its declared metric catalog."""

    benchmark_family: str
    benchmark_version: str
    metrics: tuple[MetricSpec, ...] = ()
    default_target_scale: str = "fraction"

    def __post_init__(self) -> None:
        if not _text(self.benchmark_family):
            raise ContractError("baseline benchmark_family is required")
        if not _text(self.benchmark_version):
            raise ContractError("baseline benchmark_version is required")
        codes = [spec.metric_code for spec in self.metrics]
        if len(codes) != len(set(codes)):
            raise ContractError("baseline contains duplicate metric codes")
        object.__setattr__(self, "default_target_scale", canonical_term(self.default_target_scale or "fraction"))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Baseline":
        if not isinstance(value, Mapping):
            raise ContractError("baseline must be an object")
        metrics = value.get("metrics") or []
        if not isinstance(metrics, list):
            raise ContractError("baseline metrics must be a list")
        return cls(
            benchmark_family=_text(value.get("benchmark_family") or value.get("family")),
            benchmark_version=_text(value.get("benchmark_version") or value.get("version")),
            metrics=tuple(MetricSpec.from_dict(item) for item in metrics),
            default_target_scale=_text(value.get("default_target_scale") or value.get("target_scale") or "fraction"),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "benchmark_family": self.benchmark_family,
            "benchmark_version": self.benchmark_version,
            "default_target_scale": self.default_target_scale,
            "metrics": [spec.as_dict() for spec in self.metrics],
        }

    @property
    def digest(self) -> str:
        return stable_hash(self.as_dict())

    def metric(self, metric_code: str) -> MetricSpec | None:
        for spec in self.metrics:
            if spec.metric_code == metric_code:
                return spec
        return None


@dataclass(frozen=True)
class MappingProfile:
    """The language-pack mapping pinned by a review/certificate.

    A mapping is more than an alias table: it also states which unit
    conversions are approved and the minimum semantic mapping confidence.
    ``language_pack`` scopes the mapping to a language pack; ``None`` makes it
    the review-wide default.
    """

    mapping_id: str
    mapping_version: int = 1
    language_pack: str | None = None
    aliases: Mapping[str, str] = field(default_factory=dict)
    confidence_floor: float = 0.75
    approved_conversions: tuple[tuple[str, str], ...] = field(
        default_factory=lambda: tuple(sorted(UNIT_FACTORS))
    )
    default_target_scale: str = "fraction"

    def __post_init__(self) -> None:
        if not _text(self.mapping_id):
            raise ContractError("mapping_id is required")
        if int(self.mapping_version) < 1:
            raise ContractError("mapping_version must be positive")
        object.__setattr__(self, "mapping_version", int(self.mapping_version))
        object.__setattr__(self, "confidence_floor", bounded(self.confidence_floor))
        object.__setattr__(self, "default_target_scale", canonical_term(self.default_target_scale or "fraction"))
        object.__setattr__(self, "language_pack", canonical_term(self.language_pack) if self.language_pack else None)
        normalized = _alias_map(self.aliases)
        object.__setattr__(self, "aliases", normalized)
        approved = set()
        for pair in self.approved_conversions or ():
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ContractError("approved conversion must be a pair")
            source, target = canonical_term(pair[0]), canonical_term(pair[1])
            if (source, target) in UNIT_FACTORS:
                approved.add((source, target))
        object.__setattr__(self, "approved_conversions", tuple(sorted(approved)))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "MappingProfile":
        if not isinstance(value, Mapping):
            raise ContractError("mapping must be an object")
        aliases = value.get("aliases") or {}
        if not isinstance(aliases, Mapping):
            raise ContractError("mapping aliases must be an object")
        conversions = value.get("approved_conversions")
        if conversions is None:
            approved = tuple(sorted(UNIT_FACTORS))
        else:
            if not isinstance(conversions, list):
                raise ContractError("approved_conversions must be a list")
            approved = tuple((item[0], item[1]) for item in conversions)
        return cls(
            mapping_id=_text(value.get("mapping_id") or value.get("id")),
            mapping_version=int(value.get("mapping_version", 1)),
            language_pack=_text(value.get("language_pack")) or None,
            aliases=dict(aliases),
            confidence_floor=float(value.get("confidence_floor", 0.75)),
            approved_conversions=approved,
            default_target_scale=_text(value.get("default_target_scale") or value.get("target_scale") or "fraction"),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "mapping_id": self.mapping_id,
            "mapping_version": self.mapping_version,
            "language_pack": self.language_pack,
            "aliases": dict(sorted(self.aliases.items())),
            "confidence_floor": self.confidence_floor,
            "approved_conversions": [list(pair) for pair in self.approved_conversions],
            "default_target_scale": self.default_target_scale,
        }

    @property
    def digest(self) -> str:
        return stable_hash(self.as_dict())

    def allows_conversion(self, source_scale: str, target_scale: str) -> bool:
        source, target = canonical_term(source_scale), canonical_term(target_scale)
        if source == target:
            return True
        return (source, target) in set(self.approved_conversions) and (source, target) in UNIT_FACTORS


@dataclass(frozen=True)
class ReviewPolicy:
    """Denominator and recognition policy shared by a review."""

    pass_threshold: float = 0.7
    minimum_comparability: float = 0.6
    hard_comparability_floor: float = 0.25
    max_waiver_share: float = 0.25
    allow_conditional: bool = True
    allow_waiver_for_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "pass_threshold", bounded(self.pass_threshold))
        object.__setattr__(self, "minimum_comparability", bounded(self.minimum_comparability))
        object.__setattr__(self, "hard_comparability_floor", bounded(self.hard_comparability_floor))
        object.__setattr__(self, "max_waiver_share", bounded(self.max_waiver_share))
        if self.minimum_comparability < self.hard_comparability_floor:
            raise ContractError("minimum_comparability cannot be below hard_comparability_floor")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any] | None) -> "ReviewPolicy":
        value = value or {}
        if not isinstance(value, Mapping):
            raise ContractError("policy must be an object")
        return cls(
            pass_threshold=float(value.get("pass_threshold", 0.7)),
            minimum_comparability=float(value.get("minimum_comparability", 0.6)),
            hard_comparability_floor=float(value.get("hard_comparability_floor", 0.25)),
            max_waiver_share=float(value.get("max_waiver_share", 0.25)),
            allow_conditional=bool(value.get("allow_conditional", True)),
            allow_waiver_for_required=bool(value.get("allow_waiver_for_required", True)),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "pass_threshold": self.pass_threshold,
            "minimum_comparability": self.minimum_comparability,
            "hard_comparability_floor": self.hard_comparability_floor,
            "max_waiver_share": self.max_waiver_share,
            "allow_conditional": self.allow_conditional,
            "allow_waiver_for_required": self.allow_waiver_for_required,
        }


@dataclass(frozen=True)
class Waiver:
    waiver_id: str
    reason: str
    approved_by: str
    scope: tuple[str, ...] = ()
    expires_at: str | None = None

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Waiver":
        if not isinstance(value, Mapping):
            raise ContractError("waiver must be an object")
        scope = value.get("scope") or []
        if isinstance(scope, str):
            scope = [scope]
        if not isinstance(scope, list):
            raise ContractError("waiver scope must be a list")
        return cls(
            waiver_id=_text(value.get("waiver_id") or value.get("id")),
            reason=_text(value.get("reason")),
            approved_by=_text(value.get("approved_by") or value.get("approver")),
            scope=tuple(_text(item) for item in scope if _text(item)),
            expires_at=_text(value.get("expires_at")) or None,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "waiver_id": self.waiver_id,
            "reason": self.reason,
            "approved_by": self.approved_by,
            "scope": list(self.scope),
            "expires_at": self.expires_at,
        }

    def validation_error(self, metric_code: str, at: str | None = None) -> str | None:
        if not self.waiver_id:
            return "waiver_id_missing"
        if not self.reason:
            return "waiver_reason_missing"
        if not self.approved_by:
            return "waiver_approver_missing"
        scope = {item.casefold() for item in self.scope}
        if "*" not in scope and metric_code.casefold() not in scope:
            return "waiver_scope_mismatch"
        if not self.expires_at:
            # An open-ended waiver cannot be audited against a review moment.
            return "waiver_expiry_missing"
        try:
            expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        except ValueError:
            return "waiver_expiry_invalid"
        if at is None:
            return "review_time_missing"
        try:
            reference = datetime.fromisoformat(at.replace("Z", "+00:00"))
        except ValueError:
            return "review_time_invalid"
        if expires.tzinfo is None or reference.tzinfo is None:
            return "waiver_expiry_timezone_missing"
        if expires < reference:
            return "waiver_expired"
        return None


@dataclass(frozen=True)
class MetricObservation:
    """Raw retest evidence for one metric, before scale conversion."""

    metric_code: str
    source_metric: str | None = None
    value: float | None = None
    source_scale: str | None = None
    present: bool = True
    mapping_confidence: float | None = None
    evidence_ref: str | None = None
    evidence_digest: str | None = None
    benchmark_version: str | None = None
    language_pack: str | None = None
    waiver: Waiver | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "metric_code", identifier(self.metric_code))
        if self.source_metric is not None:
            object.__setattr__(self, "source_metric", _text(self.source_metric))
        if self.source_scale is not None:
            object.__setattr__(self, "source_scale", canonical_term(self.source_scale))
        if self.value is not None:
            object.__setattr__(self, "value", finite_number(self.value))
        if self.mapping_confidence is not None:
            object.__setattr__(self, "mapping_confidence", bounded(self.mapping_confidence))
        if not self.present and self.value is not None:
            raise ContractError("a non-present observation cannot carry a value")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "MetricObservation":
        if not isinstance(value, Mapping):
            raise ContractError("observation must be an object")
        raw_waiver = value.get("waiver")
        waiver = Waiver.from_dict(raw_waiver) if isinstance(raw_waiver, Mapping) else None
        raw_value = value.get("value", value.get("observed_value"))
        present = bool(value.get("present", True))
        if raw_value is None and present:
            present = False
        return cls(
            metric_code=str(value.get("metric_code") or value.get("code") or ""),
            source_metric=_text(value.get("source_metric")) or None,
            value=None if raw_value is None else finite_number(raw_value),
            source_scale=_text(value.get("source_scale")) or None,
            present=present,
            mapping_confidence=_number(value.get("mapping_confidence")),
            evidence_ref=_text(value.get("evidence_ref") or value.get("evidence")) or None,
            evidence_digest=_text(value.get("evidence_digest")) or None,
            benchmark_version=_text(value.get("benchmark_version")) or None,
            language_pack=_text(value.get("language_pack")) or None,
            waiver=waiver,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric_code": self.metric_code,
            "source_metric": self.source_metric,
            "value": self.value,
            "source_scale": self.source_scale,
            "present": self.present,
            "mapping_confidence": self.mapping_confidence,
            "evidence_ref": self.evidence_ref,
            "evidence_digest": self.evidence_digest,
            "benchmark_version": self.benchmark_version,
            "language_pack": self.language_pack,
            "waiver": self.waiver.as_dict() if self.waiver else None,
        }


@dataclass(frozen=True)
class ReviewDefinition:
    baseline: Baseline
    mappings: tuple[MappingProfile, ...]
    policy: ReviewPolicy = field(default_factory=ReviewPolicy)
    observations: Mapping[str, tuple[MetricObservation, ...]] = field(default_factory=dict)
    default_mapping_id: str | None = None
    reviewed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.mappings:
            raise ContractError("comparability review needs at least one mapping")
        ids = [item.mapping_id for item in self.mappings]
        if len(ids) != len(set(ids)):
            raise ContractError("comparability review contains duplicate mapping ids")
        if self.default_mapping_id is not None and self.default_mapping_id not in ids:
            raise ContractError("default mapping is not part of the review")
        if self.reviewed_at:
            try:
                moment = datetime.fromisoformat(self.reviewed_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContractError("reviewed_at must be an ISO timestamp") from exc
            if moment.tzinfo is None:
                raise ContractError("reviewed_at must include a timezone")
            object.__setattr__(self, "reviewed_at", moment.isoformat())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ReviewDefinition":
        if not isinstance(value, Mapping):
            raise ContractError("comparability review must be an object")
        baseline = Baseline.from_dict(value.get("baseline") or {})
        raw_mappings = value.get("mappings")
        if raw_mappings is None:
            raw_mappings = [value.get("mapping") or {}]
        if not isinstance(raw_mappings, list) or not raw_mappings:
            raise ContractError("mappings must be a non-empty list")
        mappings = tuple(MappingProfile.from_dict(item) for item in raw_mappings)
        policy = ReviewPolicy.from_dict(value.get("policy"))
        raw = value.get("observations") or {}
        grouped: dict[str, list[MetricObservation]] = {}
        if isinstance(raw, Mapping):
            for record_id, items in raw.items():
                if not isinstance(items, list):
                    raise ContractError("observations for a record must be a list")
                grouped[_text(record_id)] = [MetricObservation.from_dict(item) for item in items]
        elif isinstance(raw, list):
            for item in raw:
                if not isinstance(item, Mapping):
                    raise ContractError("observation entry must be an object")
                record_id = _text(item.get("record_id"))
                if not record_id:
                    raise ContractError("observation entry needs record_id")
                grouped.setdefault(record_id, []).append(MetricObservation.from_dict(item))
        else:
            raise ContractError("observations must be an object or list")
        normalized: dict[str, tuple[MetricObservation, ...]] = {}
        for record_id, items in grouped.items():
            codes = [item.metric_code for item in items]
            if len(codes) != len(set(codes)):
                raise ContractError(f"duplicate observations for {record_id}")
            normalized[record_id] = tuple(items)
        return cls(baseline=baseline, mappings=mappings, policy=policy, observations=normalized,
                   default_mapping_id=_text(value.get("default_mapping_id")) or None,
                   reviewed_at=_text(value.get("reviewed_at")) or None)

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline": self.baseline.as_dict(),
            "mappings": [item.as_dict() for item in self.mappings],
            "default_mapping_id": self.default_mapping_id,
            "reviewed_at": self.reviewed_at,
            "policy": self.policy.as_dict(),
            "observations": {
                record_id: [item.as_dict() for item in items]
                for record_id, items in sorted(self.observations.items())
            },
        }

    @property
    def digest(self) -> str:
        return stable_hash(self.as_dict())

    def for_record(self, record_id: str) -> tuple[MetricObservation, ...]:
        return self.observations.get(record_id, ())

    def mapping_for(self, record: Any, *, strict: bool = True) -> MappingProfile | None:
        """Select the pinned mapping for a record's language pack.

        A language-pack-specific mapping always wins.  Otherwise the review's
        explicit default mapping is used; a review with several mappings and
        no default cannot be resolved implicitly.  With ``strict=False`` an
        unresolved language pack returns ``None`` so the review can record the
        metrics as incomparable instead of aborting the whole run.
        """
        payload = getattr(record, "payload", {}) or {}
        language_pack = canonical_term(payload.get("language_pack")) if payload.get("language_pack") else None
        if language_pack:
            for mapping in self.mappings:
                if mapping.language_pack == language_pack:
                    return mapping
        if self.default_mapping_id is not None:
            for mapping in self.mappings:
                if mapping.mapping_id == self.default_mapping_id:
                    return mapping
        fallback = [mapping for mapping in self.mappings if mapping.language_pack is None]
        if len(fallback) == 1:
            return fallback[0]
        if len(self.mappings) == 1:
            return self.mappings[0]
        if strict:
            raise ContractError(
                f"no pinned mapping for language pack {language_pack or '<unspecified>'!r}; "
                "a language pack change is not comparable under an implicit mapping"
            )
        return None
