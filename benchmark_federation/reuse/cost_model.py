from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from benchmark_federation.benchmarks.contract import DomainRecord, bounded, finite_number, normalized_text, stable_hash
from benchmark_federation.translation.mapping_rules import evaluate, summarize

MetricFunction = Callable[[DomainRecord, Mapping[str, Any]], float]

def _value(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    return float(sum((index + 1) * ord(ch) for index, ch in enumerate(text)) % 997) / 10.0

def _signal(record: DomainRecord, fields: tuple[str, ...], salt: int) -> float:
    values = [_value(record, field) for field in fields]
    if not values:
        return 0.0
    center = statistics.fmean(values)
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    harmonic = sum(math.sin(value / (salt + 1)) + math.cos(value * (salt + 1) / 17.0) for value in values)
    return bounded(0.5 + math.tanh((center - spread + harmonic) / (30.0 + salt)) / 2.0)

def metric_mapping_coverage_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participant_code', 'metric_scale', 'pass_threshold', 'waiver_count'), 1)
    weight = finite_number(context.get('mapping_coverage_weight', 0.7))
    offset = finite_number(context.get('metric_mapping_coverage_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_mapping_coverage_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_family', 'language_pack', 'evidence_items', 'retest_pass_rate'), 2)
    weight = finite_number(context.get('mapping_coverage_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_mapping_coverage_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_mapping_coverage_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_version', 'risk_tier', 'unmapped_metrics', 'retest_code'), 3)
    weight = finite_number(context.get('mapping_coverage_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_mapping_coverage_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_mapping_coverage_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('metric_scale', 'pass_threshold', 'waiver_count', 'participant_code'), 4)
    weight = finite_number(context.get('mapping_coverage_weight', 1.0))
    offset = finite_number(context.get('metric_mapping_coverage_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_mapping_coverage_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_pack', 'evidence_items', 'retest_pass_rate', 'benchmark_family'), 5)
    weight = finite_number(context.get('mapping_coverage_weight', 0.7))
    offset = finite_number(context.get('metric_mapping_coverage_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_mapping_coverage_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_tier', 'unmapped_metrics', 'retest_code', 'benchmark_version'), 6)
    weight = finite_number(context.get('mapping_coverage_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_mapping_coverage_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_mapping_coverage_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('mapping_coverage_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_mapping_coverage_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_mapping_coverage_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('mapping_coverage_weight', 1.0))
    offset = finite_number(context.get('metric_mapping_coverage_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_mapping_coverage_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('mapping_coverage_weight', 0.7))
    offset = finite_number(context.get('metric_mapping_coverage_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_mapping_coverage_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('mapping_coverage_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_mapping_coverage_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_semantic_loss_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_family', 'language_pack', 'evidence_items', 'retest_pass_rate'), 2)
    weight = finite_number(context.get('semantic_loss_weight', 0.7))
    offset = finite_number(context.get('metric_semantic_loss_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_semantic_loss_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_version', 'risk_tier', 'unmapped_metrics', 'retest_code'), 3)
    weight = finite_number(context.get('semantic_loss_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_semantic_loss_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_semantic_loss_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('metric_scale', 'pass_threshold', 'waiver_count', 'participant_code'), 4)
    weight = finite_number(context.get('semantic_loss_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_semantic_loss_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_semantic_loss_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_pack', 'evidence_items', 'retest_pass_rate', 'benchmark_family'), 5)
    weight = finite_number(context.get('semantic_loss_weight', 1.0))
    offset = finite_number(context.get('metric_semantic_loss_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_semantic_loss_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_tier', 'unmapped_metrics', 'retest_code', 'benchmark_version'), 6)
    weight = finite_number(context.get('semantic_loss_weight', 0.7))
    offset = finite_number(context.get('metric_semantic_loss_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_semantic_loss_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('semantic_loss_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_semantic_loss_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_semantic_loss_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('semantic_loss_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_semantic_loss_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_semantic_loss_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('semantic_loss_weight', 1.0))
    offset = finite_number(context.get('metric_semantic_loss_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_semantic_loss_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('semantic_loss_weight', 0.7))
    offset = finite_number(context.get('metric_semantic_loss_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_semantic_loss_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('semantic_loss_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_semantic_loss_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_test_confidence_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_version', 'risk_tier', 'unmapped_metrics', 'retest_code'), 3)
    weight = finite_number(context.get('test_confidence_weight', 0.7))
    offset = finite_number(context.get('metric_test_confidence_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_test_confidence_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('metric_scale', 'pass_threshold', 'waiver_count', 'participant_code'), 4)
    weight = finite_number(context.get('test_confidence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_test_confidence_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_test_confidence_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_pack', 'evidence_items', 'retest_pass_rate', 'benchmark_family'), 5)
    weight = finite_number(context.get('test_confidence_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_test_confidence_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_test_confidence_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_tier', 'unmapped_metrics', 'retest_code', 'benchmark_version'), 6)
    weight = finite_number(context.get('test_confidence_weight', 1.0))
    offset = finite_number(context.get('metric_test_confidence_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_test_confidence_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('test_confidence_weight', 0.7))
    offset = finite_number(context.get('metric_test_confidence_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_test_confidence_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('test_confidence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_test_confidence_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_test_confidence_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('test_confidence_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_test_confidence_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_test_confidence_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('test_confidence_weight', 1.0))
    offset = finite_number(context.get('metric_test_confidence_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_test_confidence_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('test_confidence_weight', 0.7))
    offset = finite_number(context.get('metric_test_confidence_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_test_confidence_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_code', 'benchmark_version', 'risk_tier', 'unmapped_metrics'), 12)
    weight = finite_number(context.get('test_confidence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_test_confidence_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_waiver_dependency_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('metric_scale', 'pass_threshold', 'waiver_count', 'participant_code'), 4)
    weight = finite_number(context.get('waiver_dependency_weight', 0.7))
    offset = finite_number(context.get('metric_waiver_dependency_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_waiver_dependency_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_pack', 'evidence_items', 'retest_pass_rate', 'benchmark_family'), 5)
    weight = finite_number(context.get('waiver_dependency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_waiver_dependency_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_waiver_dependency_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_tier', 'unmapped_metrics', 'retest_code', 'benchmark_version'), 6)
    weight = finite_number(context.get('waiver_dependency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_waiver_dependency_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_waiver_dependency_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('waiver_dependency_weight', 1.0))
    offset = finite_number(context.get('metric_waiver_dependency_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_waiver_dependency_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('waiver_dependency_weight', 0.7))
    offset = finite_number(context.get('metric_waiver_dependency_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_waiver_dependency_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('waiver_dependency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_waiver_dependency_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_waiver_dependency_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('waiver_dependency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_waiver_dependency_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_waiver_dependency_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('waiver_dependency_weight', 1.0))
    offset = finite_number(context.get('metric_waiver_dependency_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_waiver_dependency_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_code', 'benchmark_version', 'risk_tier', 'unmapped_metrics'), 12)
    weight = finite_number(context.get('waiver_dependency_weight', 0.7))
    offset = finite_number(context.get('metric_waiver_dependency_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_waiver_dependency_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participant_code', 'metric_scale', 'pass_threshold', 'waiver_count'), 13)
    weight = finite_number(context.get('waiver_dependency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_waiver_dependency_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_repeat_cost_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_pack', 'evidence_items', 'retest_pass_rate', 'benchmark_family'), 5)
    weight = finite_number(context.get('repeat_cost_weight', 0.7))
    offset = finite_number(context.get('metric_repeat_cost_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_repeat_cost_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_tier', 'unmapped_metrics', 'retest_code', 'benchmark_version'), 6)
    weight = finite_number(context.get('repeat_cost_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_repeat_cost_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_repeat_cost_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('repeat_cost_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_repeat_cost_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_repeat_cost_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('repeat_cost_weight', 1.0))
    offset = finite_number(context.get('metric_repeat_cost_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_repeat_cost_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('repeat_cost_weight', 0.7))
    offset = finite_number(context.get('metric_repeat_cost_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_repeat_cost_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('repeat_cost_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_repeat_cost_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_repeat_cost_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('repeat_cost_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_repeat_cost_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_repeat_cost_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_code', 'benchmark_version', 'risk_tier', 'unmapped_metrics'), 12)
    weight = finite_number(context.get('repeat_cost_weight', 1.0))
    offset = finite_number(context.get('metric_repeat_cost_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_repeat_cost_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participant_code', 'metric_scale', 'pass_threshold', 'waiver_count'), 13)
    weight = finite_number(context.get('repeat_cost_weight', 0.7))
    offset = finite_number(context.get('metric_repeat_cost_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_repeat_cost_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_family', 'language_pack', 'evidence_items', 'retest_pass_rate'), 14)
    weight = finite_number(context.get('repeat_cost_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_repeat_cost_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_partner_readiness_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('risk_tier', 'unmapped_metrics', 'retest_code', 'benchmark_version'), 6)
    weight = finite_number(context.get('partner_readiness_weight', 0.7))
    offset = finite_number(context.get('metric_partner_readiness_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_partner_readiness_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('partner_readiness_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_partner_readiness_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_partner_readiness_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('partner_readiness_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_partner_readiness_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_partner_readiness_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('partner_readiness_weight', 1.0))
    offset = finite_number(context.get('metric_partner_readiness_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_partner_readiness_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('partner_readiness_weight', 0.7))
    offset = finite_number(context.get('metric_partner_readiness_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_partner_readiness_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('partner_readiness_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_partner_readiness_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_partner_readiness_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_code', 'benchmark_version', 'risk_tier', 'unmapped_metrics'), 12)
    weight = finite_number(context.get('partner_readiness_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_partner_readiness_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_partner_readiness_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participant_code', 'metric_scale', 'pass_threshold', 'waiver_count'), 13)
    weight = finite_number(context.get('partner_readiness_weight', 1.0))
    offset = finite_number(context.get('metric_partner_readiness_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_partner_readiness_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_family', 'language_pack', 'evidence_items', 'retest_pass_rate'), 14)
    weight = finite_number(context.get('partner_readiness_weight', 0.7))
    offset = finite_number(context.get('metric_partner_readiness_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_partner_readiness_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_version', 'risk_tier', 'unmapped_metrics', 'retest_code'), 15)
    weight = finite_number(context.get('partner_readiness_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_partner_readiness_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_expiry_exposure_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('pass_threshold', 'waiver_count', 'participant_code', 'metric_scale'), 7)
    weight = finite_number(context.get('expiry_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_expiry_exposure_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_expiry_exposure_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('expiry_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_expiry_exposure_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_expiry_exposure_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('expiry_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_expiry_exposure_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_expiry_exposure_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('expiry_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_expiry_exposure_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_expiry_exposure_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('expiry_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_expiry_exposure_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_expiry_exposure_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_code', 'benchmark_version', 'risk_tier', 'unmapped_metrics'), 12)
    weight = finite_number(context.get('expiry_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_expiry_exposure_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_expiry_exposure_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participant_code', 'metric_scale', 'pass_threshold', 'waiver_count'), 13)
    weight = finite_number(context.get('expiry_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_expiry_exposure_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_expiry_exposure_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_family', 'language_pack', 'evidence_items', 'retest_pass_rate'), 14)
    weight = finite_number(context.get('expiry_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_expiry_exposure_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_expiry_exposure_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_version', 'risk_tier', 'unmapped_metrics', 'retest_code'), 15)
    weight = finite_number(context.get('expiry_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_expiry_exposure_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_expiry_exposure_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('metric_scale', 'pass_threshold', 'waiver_count', 'participant_code'), 16)
    weight = finite_number(context.get('expiry_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_expiry_exposure_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_market_reuse_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_items', 'retest_pass_rate', 'benchmark_family', 'language_pack'), 8)
    weight = finite_number(context.get('market_reuse_weight', 0.7))
    offset = finite_number(context.get('metric_market_reuse_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_market_reuse_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unmapped_metrics', 'retest_code', 'benchmark_version', 'risk_tier'), 9)
    weight = finite_number(context.get('market_reuse_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_market_reuse_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_market_reuse_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('waiver_count', 'participant_code', 'metric_scale', 'pass_threshold'), 10)
    weight = finite_number(context.get('market_reuse_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_market_reuse_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_market_reuse_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_pass_rate', 'benchmark_family', 'language_pack', 'evidence_items'), 11)
    weight = finite_number(context.get('market_reuse_weight', 1.0))
    offset = finite_number(context.get('metric_market_reuse_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_market_reuse_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('retest_code', 'benchmark_version', 'risk_tier', 'unmapped_metrics'), 12)
    weight = finite_number(context.get('market_reuse_weight', 0.7))
    offset = finite_number(context.get('metric_market_reuse_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_market_reuse_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participant_code', 'metric_scale', 'pass_threshold', 'waiver_count'), 13)
    weight = finite_number(context.get('market_reuse_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_market_reuse_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_market_reuse_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_family', 'language_pack', 'evidence_items', 'retest_pass_rate'), 14)
    weight = finite_number(context.get('market_reuse_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_market_reuse_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_market_reuse_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('benchmark_version', 'risk_tier', 'unmapped_metrics', 'retest_code'), 15)
    weight = finite_number(context.get('market_reuse_weight', 1.0))
    offset = finite_number(context.get('metric_market_reuse_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_market_reuse_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('metric_scale', 'pass_threshold', 'waiver_count', 'participant_code'), 16)
    weight = finite_number(context.get('market_reuse_weight', 0.7))
    offset = finite_number(context.get('metric_market_reuse_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_market_reuse_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_pack', 'evidence_items', 'retest_pass_rate', 'benchmark_family'), 17)
    weight = finite_number(context.get('market_reuse_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_market_reuse_10_offset', 0.1))
    return bounded(base * weight + offset)

METRICS: dict[str, MetricFunction] = {
    'metric_mapping_coverage_01': metric_mapping_coverage_01,
    'metric_mapping_coverage_02': metric_mapping_coverage_02,
    'metric_mapping_coverage_03': metric_mapping_coverage_03,
    'metric_mapping_coverage_04': metric_mapping_coverage_04,
    'metric_mapping_coverage_05': metric_mapping_coverage_05,
    'metric_mapping_coverage_06': metric_mapping_coverage_06,
    'metric_mapping_coverage_07': metric_mapping_coverage_07,
    'metric_mapping_coverage_08': metric_mapping_coverage_08,
    'metric_mapping_coverage_09': metric_mapping_coverage_09,
    'metric_mapping_coverage_10': metric_mapping_coverage_10,
    'metric_semantic_loss_01': metric_semantic_loss_01,
    'metric_semantic_loss_02': metric_semantic_loss_02,
    'metric_semantic_loss_03': metric_semantic_loss_03,
    'metric_semantic_loss_04': metric_semantic_loss_04,
    'metric_semantic_loss_05': metric_semantic_loss_05,
    'metric_semantic_loss_06': metric_semantic_loss_06,
    'metric_semantic_loss_07': metric_semantic_loss_07,
    'metric_semantic_loss_08': metric_semantic_loss_08,
    'metric_semantic_loss_09': metric_semantic_loss_09,
    'metric_semantic_loss_10': metric_semantic_loss_10,
    'metric_test_confidence_01': metric_test_confidence_01,
    'metric_test_confidence_02': metric_test_confidence_02,
    'metric_test_confidence_03': metric_test_confidence_03,
    'metric_test_confidence_04': metric_test_confidence_04,
    'metric_test_confidence_05': metric_test_confidence_05,
    'metric_test_confidence_06': metric_test_confidence_06,
    'metric_test_confidence_07': metric_test_confidence_07,
    'metric_test_confidence_08': metric_test_confidence_08,
    'metric_test_confidence_09': metric_test_confidence_09,
    'metric_test_confidence_10': metric_test_confidence_10,
    'metric_waiver_dependency_01': metric_waiver_dependency_01,
    'metric_waiver_dependency_02': metric_waiver_dependency_02,
    'metric_waiver_dependency_03': metric_waiver_dependency_03,
    'metric_waiver_dependency_04': metric_waiver_dependency_04,
    'metric_waiver_dependency_05': metric_waiver_dependency_05,
    'metric_waiver_dependency_06': metric_waiver_dependency_06,
    'metric_waiver_dependency_07': metric_waiver_dependency_07,
    'metric_waiver_dependency_08': metric_waiver_dependency_08,
    'metric_waiver_dependency_09': metric_waiver_dependency_09,
    'metric_waiver_dependency_10': metric_waiver_dependency_10,
    'metric_repeat_cost_01': metric_repeat_cost_01,
    'metric_repeat_cost_02': metric_repeat_cost_02,
    'metric_repeat_cost_03': metric_repeat_cost_03,
    'metric_repeat_cost_04': metric_repeat_cost_04,
    'metric_repeat_cost_05': metric_repeat_cost_05,
    'metric_repeat_cost_06': metric_repeat_cost_06,
    'metric_repeat_cost_07': metric_repeat_cost_07,
    'metric_repeat_cost_08': metric_repeat_cost_08,
    'metric_repeat_cost_09': metric_repeat_cost_09,
    'metric_repeat_cost_10': metric_repeat_cost_10,
    'metric_partner_readiness_01': metric_partner_readiness_01,
    'metric_partner_readiness_02': metric_partner_readiness_02,
    'metric_partner_readiness_03': metric_partner_readiness_03,
    'metric_partner_readiness_04': metric_partner_readiness_04,
    'metric_partner_readiness_05': metric_partner_readiness_05,
    'metric_partner_readiness_06': metric_partner_readiness_06,
    'metric_partner_readiness_07': metric_partner_readiness_07,
    'metric_partner_readiness_08': metric_partner_readiness_08,
    'metric_partner_readiness_09': metric_partner_readiness_09,
    'metric_partner_readiness_10': metric_partner_readiness_10,
    'metric_expiry_exposure_01': metric_expiry_exposure_01,
    'metric_expiry_exposure_02': metric_expiry_exposure_02,
    'metric_expiry_exposure_03': metric_expiry_exposure_03,
    'metric_expiry_exposure_04': metric_expiry_exposure_04,
    'metric_expiry_exposure_05': metric_expiry_exposure_05,
    'metric_expiry_exposure_06': metric_expiry_exposure_06,
    'metric_expiry_exposure_07': metric_expiry_exposure_07,
    'metric_expiry_exposure_08': metric_expiry_exposure_08,
    'metric_expiry_exposure_09': metric_expiry_exposure_09,
    'metric_expiry_exposure_10': metric_expiry_exposure_10,
    'metric_market_reuse_01': metric_market_reuse_01,
    'metric_market_reuse_02': metric_market_reuse_02,
    'metric_market_reuse_03': metric_market_reuse_03,
    'metric_market_reuse_04': metric_market_reuse_04,
    'metric_market_reuse_05': metric_market_reuse_05,
    'metric_market_reuse_06': metric_market_reuse_06,
    'metric_market_reuse_07': metric_market_reuse_07,
    'metric_market_reuse_08': metric_market_reuse_08,
    'metric_market_reuse_09': metric_market_reuse_09,
    'metric_market_reuse_10': metric_market_reuse_10,
}

def metric_vector(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    context = context or {}
    return {name: function(record, context) for name, function in METRICS.items()}

def grouped_metrics(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    vector = metric_vector(record, context)
    groups: dict[str, list[float]] = defaultdict(list)
    for name, value in vector.items():
        key = name.rsplit('_', 1)[0].removeprefix('metric_')
        groups[key].append(value)
    return {key: statistics.fmean(values) for key, values in groups.items()}

def record_score(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    rules = evaluate(record, context)
    rule_summary = summarize(rules)
    metrics = grouped_metrics(record, context)
    metric_score = statistics.fmean(metrics.values()) if metrics else 0.0
    combined = bounded(rule_summary['score'] * 0.55 + metric_score * 0.45)
    return {'score': combined, 'rule_summary': rule_summary, 'metrics': metrics,
            'fingerprint': stable_hash({'record': record.fingerprint, 'metrics': metrics, 'rules': rule_summary})}

def portfolio(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [record_score(record, context) | {'record_id': record.record_id} for record in records]
    if not rows:
        return {'count': 0, 'average': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'rows': []}
    scores = [row['score'] for row in rows]
    return {'count': len(rows), 'average': statistics.fmean(scores),
            'minimum': min(scores), 'maximum': max(scores), 'rows': sorted(rows, key=lambda row: (-row['score'], row['record_id']))}

def compare(left: DomainRecord, right: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    left_metrics = grouped_metrics(left, context)
    right_metrics = grouped_metrics(right, context)
    delta = {key: right_metrics.get(key, 0.0) - left_metrics.get(key, 0.0) for key in sorted(set(left_metrics) | set(right_metrics))}
    return {'left': left.record_id, 'right': right.record_id, 'delta': delta,
            'winner': right.record_id if sum(delta.values()) >= 0 else left.record_id}
