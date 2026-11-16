from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from benchmark_federation.benchmarks.contract import ContractError, Decision, DomainRecord, RuleResult, bounded
from benchmark_federation.reuse.cost_model import grouped_metrics, record_score
from benchmark_federation.translation.mapping_rules import evaluate

STATES = ['profiled', 'mapped', 'executed', 'reconciled', 'recognized', 'expired']
TRANSITIONS = {state: tuple(STATES[i + 1:i + 3]) for i, state in enumerate(STATES)}

@dataclass(frozen=True)
class TransitionPlan:
    from_state: str
    to_state: str
    allowed: bool
    reasons: tuple[str, ...]
    score: float

def allowed_targets(state: str) -> tuple[str, ...]:
    if state not in TRANSITIONS:
        raise ContractError('unknown workflow state')
    return TRANSITIONS[state]

def plan_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> TransitionPlan:
    context = context or {}
    if target not in STATES:
        raise ContractError('unknown target state')
    scorecard = record_score(record, context)
    reasons: list[str] = []
    structurally_allowed = target in allowed_targets(record.state)
    if not structurally_allowed:
        reasons.append('transition is not adjacent in the lifecycle')
    threshold = float(context.get('transition_threshold', 0.42))
    if scorecard['score'] < threshold:
        reasons.append('record score is below the transition threshold')
    return TransitionPlan(record.state, target, structurally_allowed and not reasons, tuple(reasons or ['eligible']), scorecard['score'])

def apply_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> DomainRecord:
    plan = plan_transition(record, target, context)
    if not plan.allowed:
        raise ContractError('; '.join(plan.reasons))
    return record.with_state(target)

def guard_participant_code_mapping_coverage_01(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_participant_code_mapping_coverage_01_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_mapping_coverage_01' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_semantic_loss_02(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_benchmark_family_semantic_loss_02_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_semantic_loss_02' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_test_confidence_03(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_benchmark_version_test_confidence_03_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_test_confidence_03' + (':passed' if allowed else ':blocked')

def guard_metric_scale_waiver_dependency_04(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_metric_scale_waiver_dependency_04_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_waiver_dependency_04' + (':passed' if allowed else ':blocked')

def guard_language_pack_repeat_cost_05(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_language_pack_repeat_cost_05_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_repeat_cost_05' + (':passed' if allowed else ':blocked')

def guard_risk_tier_partner_readiness_06(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_risk_tier_partner_readiness_06_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_partner_readiness_06' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_expiry_exposure_07(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_pass_threshold_expiry_exposure_07_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_expiry_exposure_07' + (':passed' if allowed else ':blocked')

def guard_evidence_items_market_reuse_08(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_evidence_items_market_reuse_08_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_market_reuse_08' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_mapping_coverage_09(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_unmapped_metrics_mapping_coverage_09_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_mapping_coverage_09' + (':passed' if allowed else ':blocked')

def guard_waiver_count_semantic_loss_10(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_waiver_count_semantic_loss_10_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_semantic_loss_10' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_test_confidence_11(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_retest_pass_rate_test_confidence_11_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_test_confidence_11' + (':passed' if allowed else ':blocked')

def guard_retest_code_waiver_dependency_12(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_retest_code_waiver_dependency_12_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_waiver_dependency_12' + (':passed' if allowed else ':blocked')

def guard_participant_code_repeat_cost_13(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_participant_code_repeat_cost_13_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_repeat_cost_13' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_partner_readiness_14(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_benchmark_family_partner_readiness_14_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_partner_readiness_14' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_expiry_exposure_15(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_benchmark_version_expiry_exposure_15_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_expiry_exposure_15' + (':passed' if allowed else ':blocked')

def guard_metric_scale_market_reuse_16(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_metric_scale_market_reuse_16_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_market_reuse_16' + (':passed' if allowed else ':blocked')

def guard_language_pack_mapping_coverage_17(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_language_pack_mapping_coverage_17_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_mapping_coverage_17' + (':passed' if allowed else ':blocked')

def guard_risk_tier_semantic_loss_18(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_risk_tier_semantic_loss_18_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_semantic_loss_18' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_test_confidence_19(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_pass_threshold_test_confidence_19_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_test_confidence_19' + (':passed' if allowed else ':blocked')

def guard_evidence_items_waiver_dependency_20(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_evidence_items_waiver_dependency_20_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_waiver_dependency_20' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_repeat_cost_21(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_unmapped_metrics_repeat_cost_21_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_repeat_cost_21' + (':passed' if allowed else ':blocked')

def guard_waiver_count_partner_readiness_22(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_waiver_count_partner_readiness_22_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_partner_readiness_22' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_expiry_exposure_23(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_retest_pass_rate_expiry_exposure_23_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_expiry_exposure_23' + (':passed' if allowed else ':blocked')

def guard_retest_code_market_reuse_24(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_retest_code_market_reuse_24_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_market_reuse_24' + (':passed' if allowed else ':blocked')

def guard_participant_code_mapping_coverage_25(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_participant_code_mapping_coverage_25_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_mapping_coverage_25' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_semantic_loss_26(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_benchmark_family_semantic_loss_26_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_semantic_loss_26' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_test_confidence_27(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_benchmark_version_test_confidence_27_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_test_confidence_27' + (':passed' if allowed else ':blocked')

def guard_metric_scale_waiver_dependency_28(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_metric_scale_waiver_dependency_28_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_waiver_dependency_28' + (':passed' if allowed else ':blocked')

def guard_language_pack_repeat_cost_29(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_language_pack_repeat_cost_29_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_repeat_cost_29' + (':passed' if allowed else ':blocked')

def guard_risk_tier_partner_readiness_30(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_risk_tier_partner_readiness_30_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_partner_readiness_30' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_expiry_exposure_31(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_pass_threshold_expiry_exposure_31_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_expiry_exposure_31' + (':passed' if allowed else ':blocked')

def guard_evidence_items_market_reuse_32(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_evidence_items_market_reuse_32_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_market_reuse_32' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_mapping_coverage_33(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_unmapped_metrics_mapping_coverage_33_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_mapping_coverage_33' + (':passed' if allowed else ':blocked')

def guard_waiver_count_semantic_loss_34(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_waiver_count_semantic_loss_34_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_semantic_loss_34' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_test_confidence_35(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_retest_pass_rate_test_confidence_35_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_test_confidence_35' + (':passed' if allowed else ':blocked')

def guard_retest_code_waiver_dependency_36(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_retest_code_waiver_dependency_36_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_waiver_dependency_36' + (':passed' if allowed else ':blocked')

def guard_participant_code_repeat_cost_37(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_participant_code_repeat_cost_37_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_repeat_cost_37' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_partner_readiness_38(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_benchmark_family_partner_readiness_38_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_partner_readiness_38' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_expiry_exposure_39(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_benchmark_version_expiry_exposure_39_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_expiry_exposure_39' + (':passed' if allowed else ':blocked')

def guard_metric_scale_market_reuse_40(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_metric_scale_market_reuse_40_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_market_reuse_40' + (':passed' if allowed else ':blocked')

def guard_language_pack_mapping_coverage_41(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_language_pack_mapping_coverage_41_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_mapping_coverage_41' + (':passed' if allowed else ':blocked')

def guard_risk_tier_semantic_loss_42(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_risk_tier_semantic_loss_42_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_semantic_loss_42' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_test_confidence_43(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_pass_threshold_test_confidence_43_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_test_confidence_43' + (':passed' if allowed else ':blocked')

def guard_evidence_items_waiver_dependency_44(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_evidence_items_waiver_dependency_44_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_waiver_dependency_44' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_repeat_cost_45(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_unmapped_metrics_repeat_cost_45_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_repeat_cost_45' + (':passed' if allowed else ':blocked')

def guard_waiver_count_partner_readiness_46(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_waiver_count_partner_readiness_46_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_partner_readiness_46' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_expiry_exposure_47(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_retest_pass_rate_expiry_exposure_47_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_expiry_exposure_47' + (':passed' if allowed else ':blocked')

def guard_retest_code_market_reuse_48(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_retest_code_market_reuse_48_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_market_reuse_48' + (':passed' if allowed else ':blocked')

def guard_participant_code_mapping_coverage_49(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_participant_code_mapping_coverage_49_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_mapping_coverage_49' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_semantic_loss_50(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_benchmark_family_semantic_loss_50_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_semantic_loss_50' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_test_confidence_51(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_benchmark_version_test_confidence_51_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_test_confidence_51' + (':passed' if allowed else ':blocked')

def guard_metric_scale_waiver_dependency_52(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_metric_scale_waiver_dependency_52_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_waiver_dependency_52' + (':passed' if allowed else ':blocked')

def guard_language_pack_repeat_cost_53(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_language_pack_repeat_cost_53_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_repeat_cost_53' + (':passed' if allowed else ':blocked')

def guard_risk_tier_partner_readiness_54(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_risk_tier_partner_readiness_54_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_partner_readiness_54' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_expiry_exposure_55(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_pass_threshold_expiry_exposure_55_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_expiry_exposure_55' + (':passed' if allowed else ':blocked')

def guard_evidence_items_market_reuse_56(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_evidence_items_market_reuse_56_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_market_reuse_56' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_mapping_coverage_57(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_unmapped_metrics_mapping_coverage_57_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_mapping_coverage_57' + (':passed' if allowed else ':blocked')

def guard_waiver_count_semantic_loss_58(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_waiver_count_semantic_loss_58_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_semantic_loss_58' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_test_confidence_59(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_retest_pass_rate_test_confidence_59_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_test_confidence_59' + (':passed' if allowed else ':blocked')

def guard_retest_code_waiver_dependency_60(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_retest_code_waiver_dependency_60_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_waiver_dependency_60' + (':passed' if allowed else ':blocked')

def guard_participant_code_repeat_cost_61(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_participant_code_repeat_cost_61_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_repeat_cost_61' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_partner_readiness_62(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_benchmark_family_partner_readiness_62_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_partner_readiness_62' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_expiry_exposure_63(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_benchmark_version_expiry_exposure_63_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_expiry_exposure_63' + (':passed' if allowed else ':blocked')

def guard_metric_scale_market_reuse_64(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_metric_scale_market_reuse_64_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_market_reuse_64' + (':passed' if allowed else ':blocked')

def guard_language_pack_mapping_coverage_65(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_language_pack_mapping_coverage_65_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_mapping_coverage_65' + (':passed' if allowed else ':blocked')

def guard_risk_tier_semantic_loss_66(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_risk_tier_semantic_loss_66_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_semantic_loss_66' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_test_confidence_67(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_pass_threshold_test_confidence_67_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_test_confidence_67' + (':passed' if allowed else ':blocked')

def guard_evidence_items_waiver_dependency_68(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_evidence_items_waiver_dependency_68_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_waiver_dependency_68' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_repeat_cost_69(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_unmapped_metrics_repeat_cost_69_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_repeat_cost_69' + (':passed' if allowed else ':blocked')

def guard_waiver_count_partner_readiness_70(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_waiver_count_partner_readiness_70_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_partner_readiness_70' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_expiry_exposure_71(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_retest_pass_rate_expiry_exposure_71_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_expiry_exposure_71' + (':passed' if allowed else ':blocked')

def guard_retest_code_market_reuse_72(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_retest_code_market_reuse_72_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_market_reuse_72' + (':passed' if allowed else ':blocked')

def guard_participant_code_mapping_coverage_73(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_participant_code_mapping_coverage_73_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_mapping_coverage_73' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_semantic_loss_74(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_benchmark_family_semantic_loss_74_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_semantic_loss_74' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_test_confidence_75(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_benchmark_version_test_confidence_75_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_test_confidence_75' + (':passed' if allowed else ':blocked')

def guard_metric_scale_waiver_dependency_76(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_metric_scale_waiver_dependency_76_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_waiver_dependency_76' + (':passed' if allowed else ':blocked')

def guard_language_pack_repeat_cost_77(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_language_pack_repeat_cost_77_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_repeat_cost_77' + (':passed' if allowed else ':blocked')

def guard_risk_tier_partner_readiness_78(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_risk_tier_partner_readiness_78_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_partner_readiness_78' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_expiry_exposure_79(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_pass_threshold_expiry_exposure_79_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_expiry_exposure_79' + (':passed' if allowed else ':blocked')

def guard_evidence_items_market_reuse_80(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_evidence_items_market_reuse_80_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_market_reuse_80' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_mapping_coverage_81(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_unmapped_metrics_mapping_coverage_81_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_mapping_coverage_81' + (':passed' if allowed else ':blocked')

def guard_waiver_count_semantic_loss_82(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_waiver_count_semantic_loss_82_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_semantic_loss_82' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_test_confidence_83(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_retest_pass_rate_test_confidence_83_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_test_confidence_83' + (':passed' if allowed else ':blocked')

def guard_retest_code_waiver_dependency_84(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_retest_code_waiver_dependency_84_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_waiver_dependency_84' + (':passed' if allowed else ':blocked')

def guard_participant_code_repeat_cost_85(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_participant_code_repeat_cost_85_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_repeat_cost_85' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_partner_readiness_86(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_benchmark_family_partner_readiness_86_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_partner_readiness_86' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_expiry_exposure_87(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_benchmark_version_expiry_exposure_87_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_expiry_exposure_87' + (':passed' if allowed else ':blocked')

def guard_metric_scale_market_reuse_88(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_metric_scale_market_reuse_88_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_market_reuse_88' + (':passed' if allowed else ':blocked')

def guard_language_pack_mapping_coverage_89(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_language_pack_mapping_coverage_89_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_mapping_coverage_89' + (':passed' if allowed else ':blocked')

def guard_risk_tier_semantic_loss_90(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_risk_tier_semantic_loss_90_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_semantic_loss_90' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_test_confidence_91(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_pass_threshold_test_confidence_91_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_test_confidence_91' + (':passed' if allowed else ':blocked')

def guard_evidence_items_waiver_dependency_92(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_evidence_items_waiver_dependency_92_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_waiver_dependency_92' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_repeat_cost_93(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_unmapped_metrics_repeat_cost_93_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_repeat_cost_93' + (':passed' if allowed else ':blocked')

def guard_waiver_count_partner_readiness_94(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_waiver_count_partner_readiness_94_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_partner_readiness_94' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_expiry_exposure_95(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_retest_pass_rate_expiry_exposure_95_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_expiry_exposure_95' + (':passed' if allowed else ':blocked')

def guard_retest_code_market_reuse_96(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_retest_code_market_reuse_96_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_market_reuse_96' + (':passed' if allowed else ':blocked')

def guard_participant_code_mapping_coverage_97(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_participant_code_mapping_coverage_97_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_mapping_coverage_97' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_semantic_loss_98(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_benchmark_family_semantic_loss_98_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_semantic_loss_98' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_test_confidence_99(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_benchmark_version_test_confidence_99_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_test_confidence_99' + (':passed' if allowed else ':blocked')

def guard_metric_scale_waiver_dependency_100(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_metric_scale_waiver_dependency_100_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_waiver_dependency_100' + (':passed' if allowed else ':blocked')

def guard_language_pack_repeat_cost_101(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_language_pack_repeat_cost_101_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_repeat_cost_101' + (':passed' if allowed else ':blocked')

def guard_risk_tier_partner_readiness_102(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_risk_tier_partner_readiness_102_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_partner_readiness_102' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_expiry_exposure_103(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_pass_threshold_expiry_exposure_103_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_expiry_exposure_103' + (':passed' if allowed else ':blocked')

def guard_evidence_items_market_reuse_104(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_evidence_items_market_reuse_104_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_market_reuse_104' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_mapping_coverage_105(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_unmapped_metrics_mapping_coverage_105_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_mapping_coverage_105' + (':passed' if allowed else ':blocked')

def guard_waiver_count_semantic_loss_106(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_waiver_count_semantic_loss_106_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_semantic_loss_106' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_test_confidence_107(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_retest_pass_rate_test_confidence_107_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_test_confidence_107' + (':passed' if allowed else ':blocked')

def guard_retest_code_waiver_dependency_108(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_retest_code_waiver_dependency_108_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_waiver_dependency_108' + (':passed' if allowed else ':blocked')

def guard_participant_code_repeat_cost_109(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_participant_code_repeat_cost_109_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_participant_code_repeat_cost_109' + (':passed' if allowed else ':blocked')

def guard_benchmark_family_partner_readiness_110(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_benchmark_family_partner_readiness_110_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_family_partner_readiness_110' + (':passed' if allowed else ':blocked')

def guard_benchmark_version_expiry_exposure_111(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_benchmark_version_expiry_exposure_111_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_benchmark_version_expiry_exposure_111' + (':passed' if allowed else ':blocked')

def guard_metric_scale_market_reuse_112(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_metric_scale_market_reuse_112_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_metric_scale_market_reuse_112' + (':passed' if allowed else ':blocked')

def guard_language_pack_mapping_coverage_113(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('mapping_coverage', 0.0)
    floor = float(context.get('guard_language_pack_mapping_coverage_113_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_language_pack_mapping_coverage_113' + (':passed' if allowed else ':blocked')

def guard_risk_tier_semantic_loss_114(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('semantic_loss', 0.0)
    floor = float(context.get('guard_risk_tier_semantic_loss_114_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_risk_tier_semantic_loss_114' + (':passed' if allowed else ':blocked')

def guard_pass_threshold_test_confidence_115(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('test_confidence', 0.0)
    floor = float(context.get('guard_pass_threshold_test_confidence_115_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_pass_threshold_test_confidence_115' + (':passed' if allowed else ':blocked')

def guard_evidence_items_waiver_dependency_116(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('waiver_dependency', 0.0)
    floor = float(context.get('guard_evidence_items_waiver_dependency_116_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('mapped')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_evidence_items_waiver_dependency_116' + (':passed' if allowed else ':blocked')

def guard_unmapped_metrics_repeat_cost_117(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('repeat_cost', 0.0)
    floor = float(context.get('guard_unmapped_metrics_repeat_cost_117_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('executed')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_unmapped_metrics_repeat_cost_117' + (':passed' if allowed else ':blocked')

def guard_waiver_count_partner_readiness_118(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('partner_readiness', 0.0)
    floor = float(context.get('guard_waiver_count_partner_readiness_118_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reconciled')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_waiver_count_partner_readiness_118' + (':passed' if allowed else ':blocked')

def guard_retest_pass_rate_expiry_exposure_119(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('expiry_exposure', 0.0)
    floor = float(context.get('guard_retest_pass_rate_expiry_exposure_119_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('recognized')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_pass_rate_expiry_exposure_119' + (':passed' if allowed else ':blocked')

def guard_retest_code_market_reuse_120(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('market_reuse', 0.0)
    floor = float(context.get('guard_retest_code_market_reuse_120_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('expired')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_retest_code_market_reuse_120' + (':passed' if allowed else ':blocked')

GUARDS: tuple[Callable[[DomainRecord, Mapping[str, Any]], tuple[bool, str]], ...] = (
    guard_participant_code_mapping_coverage_01,
    guard_benchmark_family_semantic_loss_02,
    guard_benchmark_version_test_confidence_03,
    guard_metric_scale_waiver_dependency_04,
    guard_language_pack_repeat_cost_05,
    guard_risk_tier_partner_readiness_06,
    guard_pass_threshold_expiry_exposure_07,
    guard_evidence_items_market_reuse_08,
    guard_unmapped_metrics_mapping_coverage_09,
    guard_waiver_count_semantic_loss_10,
    guard_retest_pass_rate_test_confidence_11,
    guard_retest_code_waiver_dependency_12,
    guard_participant_code_repeat_cost_13,
    guard_benchmark_family_partner_readiness_14,
    guard_benchmark_version_expiry_exposure_15,
    guard_metric_scale_market_reuse_16,
    guard_language_pack_mapping_coverage_17,
    guard_risk_tier_semantic_loss_18,
    guard_pass_threshold_test_confidence_19,
    guard_evidence_items_waiver_dependency_20,
    guard_unmapped_metrics_repeat_cost_21,
    guard_waiver_count_partner_readiness_22,
    guard_retest_pass_rate_expiry_exposure_23,
    guard_retest_code_market_reuse_24,
    guard_participant_code_mapping_coverage_25,
    guard_benchmark_family_semantic_loss_26,
    guard_benchmark_version_test_confidence_27,
    guard_metric_scale_waiver_dependency_28,
    guard_language_pack_repeat_cost_29,
    guard_risk_tier_partner_readiness_30,
    guard_pass_threshold_expiry_exposure_31,
    guard_evidence_items_market_reuse_32,
    guard_unmapped_metrics_mapping_coverage_33,
    guard_waiver_count_semantic_loss_34,
    guard_retest_pass_rate_test_confidence_35,
    guard_retest_code_waiver_dependency_36,
    guard_participant_code_repeat_cost_37,
    guard_benchmark_family_partner_readiness_38,
    guard_benchmark_version_expiry_exposure_39,
    guard_metric_scale_market_reuse_40,
    guard_language_pack_mapping_coverage_41,
    guard_risk_tier_semantic_loss_42,
    guard_pass_threshold_test_confidence_43,
    guard_evidence_items_waiver_dependency_44,
    guard_unmapped_metrics_repeat_cost_45,
    guard_waiver_count_partner_readiness_46,
    guard_retest_pass_rate_expiry_exposure_47,
    guard_retest_code_market_reuse_48,
    guard_participant_code_mapping_coverage_49,
    guard_benchmark_family_semantic_loss_50,
    guard_benchmark_version_test_confidence_51,
    guard_metric_scale_waiver_dependency_52,
    guard_language_pack_repeat_cost_53,
    guard_risk_tier_partner_readiness_54,
    guard_pass_threshold_expiry_exposure_55,
    guard_evidence_items_market_reuse_56,
    guard_unmapped_metrics_mapping_coverage_57,
    guard_waiver_count_semantic_loss_58,
    guard_retest_pass_rate_test_confidence_59,
    guard_retest_code_waiver_dependency_60,
    guard_participant_code_repeat_cost_61,
    guard_benchmark_family_partner_readiness_62,
    guard_benchmark_version_expiry_exposure_63,
    guard_metric_scale_market_reuse_64,
    guard_language_pack_mapping_coverage_65,
    guard_risk_tier_semantic_loss_66,
    guard_pass_threshold_test_confidence_67,
    guard_evidence_items_waiver_dependency_68,
    guard_unmapped_metrics_repeat_cost_69,
    guard_waiver_count_partner_readiness_70,
    guard_retest_pass_rate_expiry_exposure_71,
    guard_retest_code_market_reuse_72,
    guard_participant_code_mapping_coverage_73,
    guard_benchmark_family_semantic_loss_74,
    guard_benchmark_version_test_confidence_75,
    guard_metric_scale_waiver_dependency_76,
    guard_language_pack_repeat_cost_77,
    guard_risk_tier_partner_readiness_78,
    guard_pass_threshold_expiry_exposure_79,
    guard_evidence_items_market_reuse_80,
    guard_unmapped_metrics_mapping_coverage_81,
    guard_waiver_count_semantic_loss_82,
    guard_retest_pass_rate_test_confidence_83,
    guard_retest_code_waiver_dependency_84,
    guard_participant_code_repeat_cost_85,
    guard_benchmark_family_partner_readiness_86,
    guard_benchmark_version_expiry_exposure_87,
    guard_metric_scale_market_reuse_88,
    guard_language_pack_mapping_coverage_89,
    guard_risk_tier_semantic_loss_90,
    guard_pass_threshold_test_confidence_91,
    guard_evidence_items_waiver_dependency_92,
    guard_unmapped_metrics_repeat_cost_93,
    guard_waiver_count_partner_readiness_94,
    guard_retest_pass_rate_expiry_exposure_95,
    guard_retest_code_market_reuse_96,
    guard_participant_code_mapping_coverage_97,
    guard_benchmark_family_semantic_loss_98,
    guard_benchmark_version_test_confidence_99,
    guard_metric_scale_waiver_dependency_100,
    guard_language_pack_repeat_cost_101,
    guard_risk_tier_partner_readiness_102,
    guard_pass_threshold_expiry_exposure_103,
    guard_evidence_items_market_reuse_104,
    guard_unmapped_metrics_mapping_coverage_105,
    guard_waiver_count_semantic_loss_106,
    guard_retest_pass_rate_test_confidence_107,
    guard_retest_code_waiver_dependency_108,
    guard_participant_code_repeat_cost_109,
    guard_benchmark_family_partner_readiness_110,
    guard_benchmark_version_expiry_exposure_111,
    guard_metric_scale_market_reuse_112,
    guard_language_pack_mapping_coverage_113,
    guard_risk_tier_semantic_loss_114,
    guard_pass_threshold_test_confidence_115,
    guard_evidence_items_waiver_dependency_116,
    guard_unmapped_metrics_repeat_cost_117,
    guard_waiver_count_partner_readiness_118,
    guard_retest_pass_rate_expiry_exposure_119,
    guard_retest_code_market_reuse_120,
)

def guard_report(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = dict(context or {})
    context['_metrics'] = grouped_metrics(record, context)
    results = [guard(record, context) for guard in GUARDS]
    return {'passed': sum(item[0] for item in results), 'failed': sum(not item[0] for item in results),
            'messages': [item[1] for item in results]}

def decide(record: DomainRecord, context: Mapping[str, Any] | None = None) -> Decision:
    context = context or {}
    rules = evaluate(record, context)
    scorecard = record_score(record, context)
    guards = guard_report(record, context)
    effective_score = scorecard['score'] * 0.6 + float(context.get('domain_signal', 0.5)) * 0.4
    critical = sum(item.severity == 'critical' for item in rules)
    if context.get('domain_severity') == 'critical':
        outcome = 'hold'
    elif critical:
        outcome = 'hold'
    elif effective_score >= float(context.get('approve_threshold', 0.62)) and guards['passed'] >= guards['failed']:
        outcome = 'approve'
    elif effective_score >= float(context.get('review_threshold', 0.38)):
        outcome = 'review'
    else:
        outcome = 'reject'
    reasons = (f"score={scorecard['score']:.6f}", f"critical={critical}",
               f"guards={guards['passed']}/{guards['passed'] + guards['failed']}")
    return Decision(record.record_id, outcome, effective_score, reasons, rules, scorecard['metrics'])

def advance_for_outcome(record: DomainRecord, decision: Decision) -> DomainRecord:
    current = STATES.index(record.state)
    if decision.outcome == 'approve' and current + 1 < len(STATES):
        return record.with_state(STATES[current + 1])
    if decision.outcome == 'hold' and STATES[-1] != record.state:
        return record.with_state(STATES[-1])
    return record
