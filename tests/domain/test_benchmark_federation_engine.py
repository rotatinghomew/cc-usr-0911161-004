from __future__ import annotations

import unittest
from benchmark_federation.benchmarks.contract import DomainRecord
from benchmark_federation.translation.metric_bridge import conformance_profile, convert_unit, map_field, reuse_matrix


class SemanticBridgeTests(unittest.TestCase):
    def record(self, key, market="my"):
        return DomainRecord(key, {"participant_code": market, "benchmark_family": "safety", "benchmark_version": "2",
            "metric_scale": "metric", "language_pack": "ms", "risk_tier": 2, "pass_threshold": .8,
            "evidence_items": 10, "unmapped_metrics": 1, "waiver_count": 1, "retest_pass_rate": .9, "retest_code": "lab"})

    def test_unit_and_alias_mapping(self):
        self.assertAlmostEqual(convert_unit(.83, "fraction", "percent"), 83.0)
        self.assertFalse(map_field("retest_pass_rate", "pass_rate", .9, {"retest_pass_rate": "pass_rate"}).lossy)

    def test_benchmarks_and_reuse(self):
        profile = conformance_profile(self.record("a"))
        self.assertGreater(profile["mapping_coverage"], profile["semantic_loss"])
        self.assertEqual(reuse_matrix([self.record("a"), self.record("b", "th")])["market_count"], 2.0)
