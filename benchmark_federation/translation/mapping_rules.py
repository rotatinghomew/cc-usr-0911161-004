from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from benchmark_federation.benchmarks.contract import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_participant_code_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_participant_code_presence_threshold', 10.333)
    return _result('check_participant_code_presence', adjusted, threshold, True, 'validates participant_code presence',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_participant_code_range_threshold', 12.667)
    return _result('check_participant_code_range', adjusted, threshold, True, 'validates participant_code range',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_participant_code_stability_threshold', 15.0)
    return _result('check_participant_code_stability', adjusted, threshold, False, 'validates participant_code stability',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_participant_code_freshness_threshold', 17.333)
    return _result('check_participant_code_freshness', adjusted, threshold, True, 'validates participant_code freshness',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_participant_code_coverage_threshold', 19.667)
    return _result('check_participant_code_coverage', adjusted, threshold, True, 'validates participant_code coverage',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_participant_code_consistency_threshold', 22.0)
    return _result('check_participant_code_consistency', adjusted, threshold, False, 'validates participant_code consistency',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_participant_code_risk_threshold', 24.333)
    return _result('check_participant_code_risk', adjusted, threshold, True, 'validates participant_code risk',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_participant_code_confidence_threshold', 26.667)
    return _result('check_participant_code_confidence', adjusted, threshold, True, 'validates participant_code confidence',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_participant_code_dependency_threshold', 29.0)
    return _result('check_participant_code_dependency', adjusted, threshold, False, 'validates participant_code dependency',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participant_code_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participant_code')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_participant_code_readiness_threshold', 31.333)
    return _result('check_participant_code_readiness', adjusted, threshold, True, 'validates participant_code readiness',
                   {'field': 'participant_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_benchmark_family_presence_threshold', 9.333)
    return _result('check_benchmark_family_presence', adjusted, threshold, True, 'validates benchmark_family presence',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_benchmark_family_range_threshold', 11.667)
    return _result('check_benchmark_family_range', adjusted, threshold, False, 'validates benchmark_family range',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_benchmark_family_stability_threshold', 14.0)
    return _result('check_benchmark_family_stability', adjusted, threshold, True, 'validates benchmark_family stability',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_benchmark_family_freshness_threshold', 16.333)
    return _result('check_benchmark_family_freshness', adjusted, threshold, True, 'validates benchmark_family freshness',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_benchmark_family_coverage_threshold', 18.667)
    return _result('check_benchmark_family_coverage', adjusted, threshold, False, 'validates benchmark_family coverage',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_benchmark_family_consistency_threshold', 21.0)
    return _result('check_benchmark_family_consistency', adjusted, threshold, True, 'validates benchmark_family consistency',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_benchmark_family_risk_threshold', 23.333)
    return _result('check_benchmark_family_risk', adjusted, threshold, True, 'validates benchmark_family risk',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_benchmark_family_confidence_threshold', 25.667)
    return _result('check_benchmark_family_confidence', adjusted, threshold, False, 'validates benchmark_family confidence',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_benchmark_family_dependency_threshold', 28.0)
    return _result('check_benchmark_family_dependency', adjusted, threshold, True, 'validates benchmark_family dependency',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_family_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_family')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_benchmark_family_readiness_threshold', 30.333)
    return _result('check_benchmark_family_readiness', adjusted, threshold, True, 'validates benchmark_family readiness',
                   {'field': 'benchmark_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_benchmark_version_presence_threshold', 8.333)
    return _result('check_benchmark_version_presence', adjusted, threshold, False, 'validates benchmark_version presence',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_benchmark_version_range_threshold', 10.667)
    return _result('check_benchmark_version_range', adjusted, threshold, True, 'validates benchmark_version range',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_benchmark_version_stability_threshold', 13.0)
    return _result('check_benchmark_version_stability', adjusted, threshold, True, 'validates benchmark_version stability',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_benchmark_version_freshness_threshold', 15.333)
    return _result('check_benchmark_version_freshness', adjusted, threshold, False, 'validates benchmark_version freshness',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_benchmark_version_coverage_threshold', 17.667)
    return _result('check_benchmark_version_coverage', adjusted, threshold, True, 'validates benchmark_version coverage',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_benchmark_version_consistency_threshold', 20.0)
    return _result('check_benchmark_version_consistency', adjusted, threshold, True, 'validates benchmark_version consistency',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_benchmark_version_risk_threshold', 22.333)
    return _result('check_benchmark_version_risk', adjusted, threshold, False, 'validates benchmark_version risk',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_benchmark_version_confidence_threshold', 24.667)
    return _result('check_benchmark_version_confidence', adjusted, threshold, True, 'validates benchmark_version confidence',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_benchmark_version_dependency_threshold', 27.0)
    return _result('check_benchmark_version_dependency', adjusted, threshold, True, 'validates benchmark_version dependency',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_benchmark_version_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'benchmark_version')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_benchmark_version_readiness_threshold', 29.333)
    return _result('check_benchmark_version_readiness', adjusted, threshold, False, 'validates benchmark_version readiness',
                   {'field': 'benchmark_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_metric_scale_presence_threshold', 31.667)
    return _result('check_metric_scale_presence', adjusted, threshold, True, 'validates metric_scale presence',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_metric_scale_range_threshold', 9.667)
    return _result('check_metric_scale_range', adjusted, threshold, True, 'validates metric_scale range',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_metric_scale_stability_threshold', 12.0)
    return _result('check_metric_scale_stability', adjusted, threshold, False, 'validates metric_scale stability',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_metric_scale_freshness_threshold', 14.333)
    return _result('check_metric_scale_freshness', adjusted, threshold, True, 'validates metric_scale freshness',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_metric_scale_coverage_threshold', 16.667)
    return _result('check_metric_scale_coverage', adjusted, threshold, True, 'validates metric_scale coverage',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_metric_scale_consistency_threshold', 19.0)
    return _result('check_metric_scale_consistency', adjusted, threshold, False, 'validates metric_scale consistency',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_metric_scale_risk_threshold', 21.333)
    return _result('check_metric_scale_risk', adjusted, threshold, True, 'validates metric_scale risk',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_metric_scale_confidence_threshold', 23.667)
    return _result('check_metric_scale_confidence', adjusted, threshold, True, 'validates metric_scale confidence',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_metric_scale_dependency_threshold', 26.0)
    return _result('check_metric_scale_dependency', adjusted, threshold, False, 'validates metric_scale dependency',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_metric_scale_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'metric_scale')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_metric_scale_readiness_threshold', 28.333)
    return _result('check_metric_scale_readiness', adjusted, threshold, True, 'validates metric_scale readiness',
                   {'field': 'metric_scale', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_language_pack_presence_threshold', 30.667)
    return _result('check_language_pack_presence', adjusted, threshold, True, 'validates language_pack presence',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_language_pack_range_threshold', 8.667)
    return _result('check_language_pack_range', adjusted, threshold, False, 'validates language_pack range',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_language_pack_stability_threshold', 11.0)
    return _result('check_language_pack_stability', adjusted, threshold, True, 'validates language_pack stability',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_language_pack_freshness_threshold', 13.333)
    return _result('check_language_pack_freshness', adjusted, threshold, True, 'validates language_pack freshness',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_language_pack_coverage_threshold', 15.667)
    return _result('check_language_pack_coverage', adjusted, threshold, False, 'validates language_pack coverage',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_language_pack_consistency_threshold', 18.0)
    return _result('check_language_pack_consistency', adjusted, threshold, True, 'validates language_pack consistency',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_language_pack_risk_threshold', 20.333)
    return _result('check_language_pack_risk', adjusted, threshold, True, 'validates language_pack risk',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_language_pack_confidence_threshold', 22.667)
    return _result('check_language_pack_confidence', adjusted, threshold, False, 'validates language_pack confidence',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_language_pack_dependency_threshold', 25.0)
    return _result('check_language_pack_dependency', adjusted, threshold, True, 'validates language_pack dependency',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_language_pack_readiness_threshold', 27.333)
    return _result('check_language_pack_readiness', adjusted, threshold, True, 'validates language_pack readiness',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_risk_tier_presence_threshold', 29.667)
    return _result('check_risk_tier_presence', adjusted, threshold, False, 'validates risk_tier presence',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_risk_tier_range_threshold', 32.0)
    return _result('check_risk_tier_range', adjusted, threshold, True, 'validates risk_tier range',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_risk_tier_stability_threshold', 10.0)
    return _result('check_risk_tier_stability', adjusted, threshold, True, 'validates risk_tier stability',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_risk_tier_freshness_threshold', 12.333)
    return _result('check_risk_tier_freshness', adjusted, threshold, False, 'validates risk_tier freshness',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_risk_tier_coverage_threshold', 14.667)
    return _result('check_risk_tier_coverage', adjusted, threshold, True, 'validates risk_tier coverage',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_risk_tier_consistency_threshold', 17.0)
    return _result('check_risk_tier_consistency', adjusted, threshold, True, 'validates risk_tier consistency',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_risk_tier_risk_threshold', 19.333)
    return _result('check_risk_tier_risk', adjusted, threshold, False, 'validates risk_tier risk',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_risk_tier_confidence_threshold', 21.667)
    return _result('check_risk_tier_confidence', adjusted, threshold, True, 'validates risk_tier confidence',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_risk_tier_dependency_threshold', 24.0)
    return _result('check_risk_tier_dependency', adjusted, threshold, True, 'validates risk_tier dependency',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_risk_tier_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'risk_tier')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_risk_tier_readiness_threshold', 26.333)
    return _result('check_risk_tier_readiness', adjusted, threshold, False, 'validates risk_tier readiness',
                   {'field': 'risk_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_pass_threshold_presence_threshold', 28.667)
    return _result('check_pass_threshold_presence', adjusted, threshold, True, 'validates pass_threshold presence',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_pass_threshold_range_threshold', 31.0)
    return _result('check_pass_threshold_range', adjusted, threshold, True, 'validates pass_threshold range',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_pass_threshold_stability_threshold', 9.0)
    return _result('check_pass_threshold_stability', adjusted, threshold, False, 'validates pass_threshold stability',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_pass_threshold_freshness_threshold', 11.333)
    return _result('check_pass_threshold_freshness', adjusted, threshold, True, 'validates pass_threshold freshness',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_pass_threshold_coverage_threshold', 13.667)
    return _result('check_pass_threshold_coverage', adjusted, threshold, True, 'validates pass_threshold coverage',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_pass_threshold_consistency_threshold', 16.0)
    return _result('check_pass_threshold_consistency', adjusted, threshold, False, 'validates pass_threshold consistency',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_pass_threshold_risk_threshold', 18.333)
    return _result('check_pass_threshold_risk', adjusted, threshold, True, 'validates pass_threshold risk',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_pass_threshold_confidence_threshold', 20.667)
    return _result('check_pass_threshold_confidence', adjusted, threshold, True, 'validates pass_threshold confidence',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_pass_threshold_dependency_threshold', 23.0)
    return _result('check_pass_threshold_dependency', adjusted, threshold, False, 'validates pass_threshold dependency',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_pass_threshold_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'pass_threshold')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_pass_threshold_readiness_threshold', 25.333)
    return _result('check_pass_threshold_readiness', adjusted, threshold, True, 'validates pass_threshold readiness',
                   {'field': 'pass_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_evidence_items_presence_threshold', 27.667)
    return _result('check_evidence_items_presence', adjusted, threshold, True, 'validates evidence_items presence',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_evidence_items_range_threshold', 30.0)
    return _result('check_evidence_items_range', adjusted, threshold, False, 'validates evidence_items range',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_evidence_items_stability_threshold', 8.0)
    return _result('check_evidence_items_stability', adjusted, threshold, True, 'validates evidence_items stability',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_evidence_items_freshness_threshold', 10.333)
    return _result('check_evidence_items_freshness', adjusted, threshold, True, 'validates evidence_items freshness',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_evidence_items_coverage_threshold', 12.667)
    return _result('check_evidence_items_coverage', adjusted, threshold, False, 'validates evidence_items coverage',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_evidence_items_consistency_threshold', 15.0)
    return _result('check_evidence_items_consistency', adjusted, threshold, True, 'validates evidence_items consistency',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_evidence_items_risk_threshold', 17.333)
    return _result('check_evidence_items_risk', adjusted, threshold, True, 'validates evidence_items risk',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_evidence_items_confidence_threshold', 19.667)
    return _result('check_evidence_items_confidence', adjusted, threshold, False, 'validates evidence_items confidence',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_evidence_items_dependency_threshold', 22.0)
    return _result('check_evidence_items_dependency', adjusted, threshold, True, 'validates evidence_items dependency',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_evidence_items_readiness_threshold', 24.333)
    return _result('check_evidence_items_readiness', adjusted, threshold, True, 'validates evidence_items readiness',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_unmapped_metrics_presence_threshold', 26.667)
    return _result('check_unmapped_metrics_presence', adjusted, threshold, False, 'validates unmapped_metrics presence',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_unmapped_metrics_range_threshold', 29.0)
    return _result('check_unmapped_metrics_range', adjusted, threshold, True, 'validates unmapped_metrics range',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_unmapped_metrics_stability_threshold', 31.333)
    return _result('check_unmapped_metrics_stability', adjusted, threshold, True, 'validates unmapped_metrics stability',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_unmapped_metrics_freshness_threshold', 9.333)
    return _result('check_unmapped_metrics_freshness', adjusted, threshold, False, 'validates unmapped_metrics freshness',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_unmapped_metrics_coverage_threshold', 11.667)
    return _result('check_unmapped_metrics_coverage', adjusted, threshold, True, 'validates unmapped_metrics coverage',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_unmapped_metrics_consistency_threshold', 14.0)
    return _result('check_unmapped_metrics_consistency', adjusted, threshold, True, 'validates unmapped_metrics consistency',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_unmapped_metrics_risk_threshold', 16.333)
    return _result('check_unmapped_metrics_risk', adjusted, threshold, False, 'validates unmapped_metrics risk',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_unmapped_metrics_confidence_threshold', 18.667)
    return _result('check_unmapped_metrics_confidence', adjusted, threshold, True, 'validates unmapped_metrics confidence',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_unmapped_metrics_dependency_threshold', 21.0)
    return _result('check_unmapped_metrics_dependency', adjusted, threshold, True, 'validates unmapped_metrics dependency',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_metrics_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_metrics')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_unmapped_metrics_readiness_threshold', 23.333)
    return _result('check_unmapped_metrics_readiness', adjusted, threshold, False, 'validates unmapped_metrics readiness',
                   {'field': 'unmapped_metrics', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_waiver_count_presence_threshold', 25.667)
    return _result('check_waiver_count_presence', adjusted, threshold, True, 'validates waiver_count presence',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_waiver_count_range_threshold', 28.0)
    return _result('check_waiver_count_range', adjusted, threshold, True, 'validates waiver_count range',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_waiver_count_stability_threshold', 30.333)
    return _result('check_waiver_count_stability', adjusted, threshold, False, 'validates waiver_count stability',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_waiver_count_freshness_threshold', 8.333)
    return _result('check_waiver_count_freshness', adjusted, threshold, True, 'validates waiver_count freshness',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_waiver_count_coverage_threshold', 10.667)
    return _result('check_waiver_count_coverage', adjusted, threshold, True, 'validates waiver_count coverage',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_waiver_count_consistency_threshold', 13.0)
    return _result('check_waiver_count_consistency', adjusted, threshold, False, 'validates waiver_count consistency',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_waiver_count_risk_threshold', 15.333)
    return _result('check_waiver_count_risk', adjusted, threshold, True, 'validates waiver_count risk',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_waiver_count_confidence_threshold', 17.667)
    return _result('check_waiver_count_confidence', adjusted, threshold, True, 'validates waiver_count confidence',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_waiver_count_dependency_threshold', 20.0)
    return _result('check_waiver_count_dependency', adjusted, threshold, False, 'validates waiver_count dependency',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_waiver_count_readiness_threshold', 22.333)
    return _result('check_waiver_count_readiness', adjusted, threshold, True, 'validates waiver_count readiness',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_retest_pass_rate_presence_threshold', 24.667)
    return _result('check_retest_pass_rate_presence', adjusted, threshold, True, 'validates retest_pass_rate presence',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_retest_pass_rate_range_threshold', 27.0)
    return _result('check_retest_pass_rate_range', adjusted, threshold, False, 'validates retest_pass_rate range',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_retest_pass_rate_stability_threshold', 29.333)
    return _result('check_retest_pass_rate_stability', adjusted, threshold, True, 'validates retest_pass_rate stability',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_retest_pass_rate_freshness_threshold', 31.667)
    return _result('check_retest_pass_rate_freshness', adjusted, threshold, True, 'validates retest_pass_rate freshness',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_retest_pass_rate_coverage_threshold', 9.667)
    return _result('check_retest_pass_rate_coverage', adjusted, threshold, False, 'validates retest_pass_rate coverage',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_retest_pass_rate_consistency_threshold', 12.0)
    return _result('check_retest_pass_rate_consistency', adjusted, threshold, True, 'validates retest_pass_rate consistency',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_retest_pass_rate_risk_threshold', 14.333)
    return _result('check_retest_pass_rate_risk', adjusted, threshold, True, 'validates retest_pass_rate risk',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_retest_pass_rate_confidence_threshold', 16.667)
    return _result('check_retest_pass_rate_confidence', adjusted, threshold, False, 'validates retest_pass_rate confidence',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_retest_pass_rate_dependency_threshold', 19.0)
    return _result('check_retest_pass_rate_dependency', adjusted, threshold, True, 'validates retest_pass_rate dependency',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_pass_rate_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_pass_rate')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_retest_pass_rate_readiness_threshold', 21.333)
    return _result('check_retest_pass_rate_readiness', adjusted, threshold, True, 'validates retest_pass_rate readiness',
                   {'field': 'retest_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_retest_code_presence_threshold', 23.667)
    return _result('check_retest_code_presence', adjusted, threshold, False, 'validates retest_code presence',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_retest_code_range_threshold', 26.0)
    return _result('check_retest_code_range', adjusted, threshold, True, 'validates retest_code range',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_retest_code_stability_threshold', 28.333)
    return _result('check_retest_code_stability', adjusted, threshold, True, 'validates retest_code stability',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_retest_code_freshness_threshold', 30.667)
    return _result('check_retest_code_freshness', adjusted, threshold, False, 'validates retest_code freshness',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_retest_code_coverage_threshold', 8.667)
    return _result('check_retest_code_coverage', adjusted, threshold, True, 'validates retest_code coverage',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_retest_code_consistency_threshold', 11.0)
    return _result('check_retest_code_consistency', adjusted, threshold, True, 'validates retest_code consistency',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_retest_code_risk_threshold', 13.333)
    return _result('check_retest_code_risk', adjusted, threshold, False, 'validates retest_code risk',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_retest_code_confidence_threshold', 15.667)
    return _result('check_retest_code_confidence', adjusted, threshold, True, 'validates retest_code confidence',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_retest_code_dependency_threshold', 18.0)
    return _result('check_retest_code_dependency', adjusted, threshold, True, 'validates retest_code dependency',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_retest_code_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'retest_code')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_retest_code_readiness_threshold', 20.333)
    return _result('check_retest_code_readiness', adjusted, threshold, False, 'validates retest_code readiness',
                   {'field': 'retest_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_participant_code_presence,
    check_participant_code_range,
    check_participant_code_stability,
    check_participant_code_freshness,
    check_participant_code_coverage,
    check_participant_code_consistency,
    check_participant_code_risk,
    check_participant_code_confidence,
    check_participant_code_dependency,
    check_participant_code_readiness,
    check_benchmark_family_presence,
    check_benchmark_family_range,
    check_benchmark_family_stability,
    check_benchmark_family_freshness,
    check_benchmark_family_coverage,
    check_benchmark_family_consistency,
    check_benchmark_family_risk,
    check_benchmark_family_confidence,
    check_benchmark_family_dependency,
    check_benchmark_family_readiness,
    check_benchmark_version_presence,
    check_benchmark_version_range,
    check_benchmark_version_stability,
    check_benchmark_version_freshness,
    check_benchmark_version_coverage,
    check_benchmark_version_consistency,
    check_benchmark_version_risk,
    check_benchmark_version_confidence,
    check_benchmark_version_dependency,
    check_benchmark_version_readiness,
    check_metric_scale_presence,
    check_metric_scale_range,
    check_metric_scale_stability,
    check_metric_scale_freshness,
    check_metric_scale_coverage,
    check_metric_scale_consistency,
    check_metric_scale_risk,
    check_metric_scale_confidence,
    check_metric_scale_dependency,
    check_metric_scale_readiness,
    check_language_pack_presence,
    check_language_pack_range,
    check_language_pack_stability,
    check_language_pack_freshness,
    check_language_pack_coverage,
    check_language_pack_consistency,
    check_language_pack_risk,
    check_language_pack_confidence,
    check_language_pack_dependency,
    check_language_pack_readiness,
    check_risk_tier_presence,
    check_risk_tier_range,
    check_risk_tier_stability,
    check_risk_tier_freshness,
    check_risk_tier_coverage,
    check_risk_tier_consistency,
    check_risk_tier_risk,
    check_risk_tier_confidence,
    check_risk_tier_dependency,
    check_risk_tier_readiness,
    check_pass_threshold_presence,
    check_pass_threshold_range,
    check_pass_threshold_stability,
    check_pass_threshold_freshness,
    check_pass_threshold_coverage,
    check_pass_threshold_consistency,
    check_pass_threshold_risk,
    check_pass_threshold_confidence,
    check_pass_threshold_dependency,
    check_pass_threshold_readiness,
    check_evidence_items_presence,
    check_evidence_items_range,
    check_evidence_items_stability,
    check_evidence_items_freshness,
    check_evidence_items_coverage,
    check_evidence_items_consistency,
    check_evidence_items_risk,
    check_evidence_items_confidence,
    check_evidence_items_dependency,
    check_evidence_items_readiness,
    check_unmapped_metrics_presence,
    check_unmapped_metrics_range,
    check_unmapped_metrics_stability,
    check_unmapped_metrics_freshness,
    check_unmapped_metrics_coverage,
    check_unmapped_metrics_consistency,
    check_unmapped_metrics_risk,
    check_unmapped_metrics_confidence,
    check_unmapped_metrics_dependency,
    check_unmapped_metrics_readiness,
    check_waiver_count_presence,
    check_waiver_count_range,
    check_waiver_count_stability,
    check_waiver_count_freshness,
    check_waiver_count_coverage,
    check_waiver_count_consistency,
    check_waiver_count_risk,
    check_waiver_count_confidence,
    check_waiver_count_dependency,
    check_waiver_count_readiness,
    check_retest_pass_rate_presence,
    check_retest_pass_rate_range,
    check_retest_pass_rate_stability,
    check_retest_pass_rate_freshness,
    check_retest_pass_rate_coverage,
    check_retest_pass_rate_consistency,
    check_retest_pass_rate_risk,
    check_retest_pass_rate_confidence,
    check_retest_pass_rate_dependency,
    check_retest_pass_rate_readiness,
    check_retest_code_presence,
    check_retest_code_range,
    check_retest_code_stability,
    check_retest_code_freshness,
    check_retest_code_coverage,
    check_retest_code_consistency,
    check_retest_code_risk,
    check_retest_code_confidence,
    check_retest_code_dependency,
    check_retest_code_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
