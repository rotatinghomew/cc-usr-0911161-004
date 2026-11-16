from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from benchmark_federation.benchmarks.contract import ContractError, DomainRecord, RuleResult, bounded, stable_hash
from benchmark_federation.translation.mapping_rules import RULE_INDEX, evaluate, summarize
from benchmark_federation.reuse.cost_model import METRICS, compare, grouped_metrics, metric_vector, portfolio, record_score

FIELDS = ['participant_code', 'benchmark_family', 'benchmark_version', 'metric_scale', 'language_pack', 'risk_tier', 'pass_threshold', 'evidence_items', 'unmapped_metrics', 'waiver_count', 'retest_pass_rate', 'retest_code']

def make_record(seed: int = 1, state: str | None = None) -> DomainRecord:
    payload = {}
    for index, field in enumerate(FIELDS):
        selector = (seed + index) % 4
        if selector == 0:
            payload[field] = seed * 9.5 + index * 1.25
        elif selector == 1:
            payload[field] = f'{field}-{seed % 5}'
        elif selector == 2:
            payload[field] = (seed + index) / 10.0
        else:
            payload[field] = (seed + index) % 2 == 0
    return DomainRecord(f'benchmark_case-{seed:03d}', payload, state or 'profiled')

class RuleGroup3Tests(unittest.TestCase):
    def test_evaluate_returns_complete_catalog(self):
        record = make_record()
        results = evaluate(record, {})
        self.assertEqual(len(results), len(RULE_INDEX))
        self.assertTrue(all(isinstance(item, RuleResult) for item in results))
        self.assertTrue(all(0.0 <= item.score <= 1.0 for item in results))

    def test_summary_is_conservative_and_counted(self):
        results = evaluate(make_record(2), {'risk_weight': 0.8})
        summary = summarize(results)
        self.assertEqual(summary['passed'] + summary['failed'], len(results))
        self.assertGreaterEqual(summary['critical'], 0)
        self.assertGreaterEqual(summary['score'], 0.0)
        self.assertLessEqual(summary['score'], 1.0)

    def test_check_pass_threshold_presence_03_01(self):
        record = make_record(5)
        result = RULE_INDEX['check_pass_threshold_presence'](record, {'check_pass_threshold_presence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_range_03_02(self):
        record = make_record(6)
        result = RULE_INDEX['check_pass_threshold_range'](record, {'check_pass_threshold_range_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_stability_03_03(self):
        record = make_record(7)
        result = RULE_INDEX['check_pass_threshold_stability'](record, {'check_pass_threshold_stability_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_freshness_03_04(self):
        record = make_record(8)
        result = RULE_INDEX['check_pass_threshold_freshness'](record, {'check_pass_threshold_freshness_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_coverage_03_05(self):
        record = make_record(9)
        result = RULE_INDEX['check_pass_threshold_coverage'](record, {'check_pass_threshold_coverage_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_consistency_03_06(self):
        record = make_record(10)
        result = RULE_INDEX['check_pass_threshold_consistency'](record, {'check_pass_threshold_consistency_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_risk_03_07(self):
        record = make_record(11)
        result = RULE_INDEX['check_pass_threshold_risk'](record, {'check_pass_threshold_risk_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_confidence_03_08(self):
        record = make_record(12)
        result = RULE_INDEX['check_pass_threshold_confidence'](record, {'check_pass_threshold_confidence_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_dependency_03_09(self):
        record = make_record(13)
        result = RULE_INDEX['check_pass_threshold_dependency'](record, {'check_pass_threshold_dependency_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_pass_threshold_readiness_03_10(self):
        record = make_record(14)
        result = RULE_INDEX['check_pass_threshold_readiness'](record, {'check_pass_threshold_readiness_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_pass_threshold_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_presence_03_11(self):
        record = make_record(15)
        result = RULE_INDEX['check_evidence_items_presence'](record, {'check_evidence_items_presence_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_range_03_12(self):
        record = make_record(16)
        result = RULE_INDEX['check_evidence_items_range'](record, {'check_evidence_items_range_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_stability_03_13(self):
        record = make_record(17)
        result = RULE_INDEX['check_evidence_items_stability'](record, {'check_evidence_items_stability_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_freshness_03_14(self):
        record = make_record(18)
        result = RULE_INDEX['check_evidence_items_freshness'](record, {'check_evidence_items_freshness_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_coverage_03_15(self):
        record = make_record(19)
        result = RULE_INDEX['check_evidence_items_coverage'](record, {'check_evidence_items_coverage_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_consistency_03_16(self):
        record = make_record(20)
        result = RULE_INDEX['check_evidence_items_consistency'](record, {'check_evidence_items_consistency_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_risk_03_17(self):
        record = make_record(21)
        result = RULE_INDEX['check_evidence_items_risk'](record, {'check_evidence_items_risk_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_confidence_03_18(self):
        record = make_record(22)
        result = RULE_INDEX['check_evidence_items_confidence'](record, {'check_evidence_items_confidence_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_dependency_03_19(self):
        record = make_record(23)
        result = RULE_INDEX['check_evidence_items_dependency'](record, {'check_evidence_items_dependency_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_evidence_items_readiness_03_20(self):
        record = make_record(24)
        result = RULE_INDEX['check_evidence_items_readiness'](record, {'check_evidence_items_readiness_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_evidence_items_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_presence_03_21(self):
        record = make_record(25)
        result = RULE_INDEX['check_unmapped_metrics_presence'](record, {'check_unmapped_metrics_presence_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_range_03_22(self):
        record = make_record(26)
        result = RULE_INDEX['check_unmapped_metrics_range'](record, {'check_unmapped_metrics_range_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_stability_03_23(self):
        record = make_record(27)
        result = RULE_INDEX['check_unmapped_metrics_stability'](record, {'check_unmapped_metrics_stability_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_freshness_03_24(self):
        record = make_record(28)
        result = RULE_INDEX['check_unmapped_metrics_freshness'](record, {'check_unmapped_metrics_freshness_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_coverage_03_25(self):
        record = make_record(29)
        result = RULE_INDEX['check_unmapped_metrics_coverage'](record, {'check_unmapped_metrics_coverage_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_consistency_03_26(self):
        record = make_record(30)
        result = RULE_INDEX['check_unmapped_metrics_consistency'](record, {'check_unmapped_metrics_consistency_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_risk_03_27(self):
        record = make_record(31)
        result = RULE_INDEX['check_unmapped_metrics_risk'](record, {'check_unmapped_metrics_risk_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_confidence_03_28(self):
        record = make_record(32)
        result = RULE_INDEX['check_unmapped_metrics_confidence'](record, {'check_unmapped_metrics_confidence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_dependency_03_29(self):
        record = make_record(33)
        result = RULE_INDEX['check_unmapped_metrics_dependency'](record, {'check_unmapped_metrics_dependency_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unmapped_metrics_readiness_03_30(self):
        record = make_record(34)
        result = RULE_INDEX['check_unmapped_metrics_readiness'](record, {'check_unmapped_metrics_readiness_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unmapped_metrics_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

class MetricGroup3Tests(unittest.TestCase):
    def test_metric_vector_is_deterministic(self):
        record = make_record(11)
        first = metric_vector(record, {})
        second = metric_vector(record, {})
        self.assertEqual(first, second)
        self.assertEqual(set(first), set(METRICS))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in first.values()))

    def test_grouped_metrics_match_business_catalog(self):
        grouped = grouped_metrics(make_record(4), {})
        self.assertEqual(set(grouped), {'test_confidence', 'mapping_coverage', 'semantic_loss', 'partner_readiness', 'expiry_exposure', 'waiver_dependency', 'market_reuse', 'repeat_cost'})
        self.assertTrue(all(math.isfinite(value) for value in grouped.values()))

    def test_portfolio_orders_by_descending_score(self):
        result = portfolio([make_record(2), make_record(3), make_record(4)])
        scores = [row['score'] for row in result['rows']]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result['count'], 3)
        self.assertGreaterEqual(result['maximum'], result['minimum'])

    def test_compare_has_all_metric_deltas(self):
        result = compare(make_record(5), make_record(6))
        self.assertEqual(set(result['delta']), {'test_confidence', 'mapping_coverage', 'semantic_loss', 'partner_readiness', 'expiry_exposure', 'waiver_dependency', 'market_reuse', 'repeat_cost'})
        self.assertIn(result['winner'], {make_record(5).record_id, make_record(6).record_id})

    def test_score_fingerprint_changes_with_payload(self):
        left = record_score(make_record(7))
        right = record_score(make_record(8))
        self.assertNotEqual(left['fingerprint'], right['fingerprint'])
        self.assertNotEqual(stable_hash(left['metrics']), stable_hash(right['metrics']))

if __name__ == '__main__':
    unittest.main()
