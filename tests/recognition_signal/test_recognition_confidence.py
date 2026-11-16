from __future__ import annotations
import unittest
from benchmark_federation.recognition_signal.recognition_confidence import recognition_confidence, peer_distribution
class Record:
    def __init__(self, payload): self.payload = payload
class SignalTests(unittest.TestCase):
    def setUp(self): self.payload = {'participant_code': 'lab-a', 'benchmark_family': 'safety', 'benchmark_version': 'v2', 'metric_scale': 'normalized', 'language_pack': 'zh', 'risk_tier': 2, 'pass_threshold': 0.75, 'evidence_items': 80, 'unmapped_metrics': 4, 'waiver_count': 1, 'retest_pass_rate': 0.88, 'laboratory_code': 'lab-a'}
    def test_signal_is_bounded_and_explainable(self):
        signal = recognition_confidence(self.payload)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)
        self.assertIn(signal.severity, {'info', 'warning', 'critical'})
        self.assertTrue({'coverage', 'semantic_loss', 'pass_margin'}.issubset(signal.evidence))
    def test_peer_distribution_uses_business_group(self):
        other = dict(self.payload); other['benchmark_family'] = 'group-b'
        result = peer_distribution([Record(self.payload), Record(other)])
        self.assertEqual(result['count'], 2)
        self.assertIn('families', result)
    def test_material_business_change_is_observable(self):
        changed = dict(self.payload); changed['unmapped_metrics'] = 50
        self.assertNotEqual(recognition_confidence(changed).score, recognition_confidence(self.payload).score)
    def test_business_variant_1(self):
        changed = dict(self.payload)
        changed['benchmark_version'] = self.payload['benchmark_version']
        signal = recognition_confidence(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_2(self):
        changed = dict(self.payload)
        changed['metric_scale'] = self.payload['metric_scale']
        signal = recognition_confidence(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_3(self):
        changed = dict(self.payload)
        changed['language_pack'] = self.payload['language_pack']
        signal = recognition_confidence(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

if __name__ == '__main__': unittest.main()
