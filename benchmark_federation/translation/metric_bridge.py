from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from benchmark_federation.benchmarks.contract import DomainRecord, bounded, finite_number, normalized_text


UNIT_FACTORS = {("fraction", "percent"): 100.0, ("percent", "fraction"): 0.01,
                ("milliseconds", "seconds"): 0.001, ("seconds", "milliseconds"): 1000.0}


@dataclass(frozen=True)
class MappingResult:
    source: str
    target: str
    value: Any
    confidence: float
    lossy: bool


def canonical_term(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalized_text(value)).strip("_")


def convert_unit(value: float, source: str, target: str) -> float:
    source, target = canonical_term(source), canonical_term(target)
    if source == target:
        return finite_number(value)
    if (source, target) not in UNIT_FACTORS:
        raise ValueError("unsupported unit conversion")
    return finite_number(value) * UNIT_FACTORS[(source, target)]


def map_field(source: str, target: str, value: Any, aliases: Mapping[str, str]) -> MappingResult:
    canonical_source = canonical_term(source)
    canonical_target = canonical_term(target)
    alias_target = canonical_term(aliases.get(canonical_source, canonical_source))
    exact = alias_target == canonical_target
    token_overlap = len(set(alias_target.split("_")) & set(canonical_target.split("_")))
    token_total = max(1, len(set(alias_target.split("_")) | set(canonical_target.split("_"))))
    confidence = 1.0 if exact else token_overlap / token_total
    return MappingResult(canonical_source, canonical_target, value, confidence, confidence < 0.75)


def conformance_profile(record: DomainRecord) -> dict[str, float]:
    unmapped = max(0.0, finite_number(record.payload.get("unmapped_metrics", 0.0)))
    evidence = max(0.0, finite_number(record.payload.get("evidence_items", 0.0)))
    waivers = max(0.0, finite_number(record.payload.get("waiver_count", 0.0)))
    pass_rate = bounded(finite_number(record.payload.get("retest_pass_rate", 0.0)))
    coverage = bounded(1.0 - unmapped / max(1.0, unmapped + evidence))
    semantic_loss = bounded(unmapped / max(1.0, evidence + 1.0))
    waiver_dependency = bounded(waivers / max(1.0, evidence))
    return {"mapping_coverage": coverage, "semantic_loss": semantic_loss, "waiver_dependency": waiver_dependency,
            "test_confidence": pass_rate * (1.0 - semantic_loss * 0.4)}


def reuse_matrix(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    markets = {canonical_term(row.payload.get("participant_code", "unknown")) for row in rows}
    standards = {canonical_term(row.payload.get("benchmark_family", "unknown")) for row in rows}
    benchmarks = [conformance_profile(row) for row in rows]
    return {"market_count": float(len(markets)), "standard_count": float(len(standards)),
            "mean_coverage": sum(item["mapping_coverage"] for item in benchmarks) / max(1, len(benchmarks)),
            "repeat_cost": bounded(len(standards) / max(1, len(markets) * 4.0))}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    profile = conformance_profile(record)
    reuse = reuse_matrix(repository.list_records() or [record])
    return {"mapping_coverage_weight": 0.6 + profile["mapping_coverage"] * 0.6,
            "semantic_loss_weight": 0.7 + profile["semantic_loss"] * 0.7,
            "test_confidence_weight": 0.6 + profile["test_confidence"] * 0.5,
            "waiver_dependency_weight": 0.8 + profile["waiver_dependency"] * 0.6,
            "market_reuse_weight": 0.7 + reuse["mean_coverage"] * 0.5}
