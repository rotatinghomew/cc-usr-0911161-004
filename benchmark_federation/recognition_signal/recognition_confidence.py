from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def recognition_confidence(payload: Mapping[str, Any]) -> DomainSignal:
    pass_rate = ratio(payload, 'retest_pass_rate')
    threshold = ratio(payload, 'pass_threshold', 0.7)
    evidence = number(payload, 'evidence_items')
    unmapped = number(payload, 'unmapped_metrics')
    waivers = number(payload, 'waiver_count')
    risk = min(1.0, number(payload, 'risk_tier') / 5.0)
    coverage = 0.0 if evidence + unmapped <= 0 else evidence / (evidence + unmapped)
    semantic_loss = min(1.0, unmapped / max(1.0, evidence) + waivers * 0.04)
    margin = clamp(0.5 + (pass_rate - threshold) / 2.0)
    score = clamp(coverage * 0.36 + margin * 0.34 + (1-semantic_loss) * 0.2 + (1-risk) * 0.1)
    severity = 'critical' if pass_rate < threshold or coverage < 0.5 else 'warning' if semantic_loss > 0.25 else 'info'
    return DomainSignal('recognition_confidence', score, severity, {'coverage': coverage, 'semantic_loss': semantic_loss, 'pass_margin': pass_rate-threshold, 'waivers': waivers})

def peer_distribution(records: Iterable[Any], group_field: str = 'benchmark_family') -> dict[str, Any]:
    families = {}
    for record in records:
        payload = getattr(record, 'payload', record); key = str(payload.get(group_field, 'unknown'))
        families.setdefault(key, []).append(recognition_confidence(payload).score)
    return {'families': {k:min(v) for k,v in families.items()}, 'count': sum(len(v) for v in families.values()), 'weakest_family': min((min(v),k) for k,v in families.items())[1] if families else ''}

def augment_context(record: Any, repository: Any) -> dict[str, Any]:
    signal = recognition_confidence(record.payload); peers = peer_distribution(repository.list_records())
    return {'domain_signal': signal.score, 'domain_severity': signal.severity, 'weakest_family': peers['weakest_family'], 'peer_count': peers['count']}
