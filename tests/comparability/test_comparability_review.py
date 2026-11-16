from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from benchmark_federation.benchmarks.contract import ContractError, DomainRecord, records_from_fixture
from benchmark_federation.certificates.certificate import build_certificate, ensure_no_silent_drift
from benchmark_federation.certificates.recognition_pack import export_bundle, verify_bundle, verify_comparability
from benchmark_federation.comparability.engine import (
    CONDITIONAL,
    INSUFFICIENT_EVIDENCE,
    NOT_RECOGNIZED,
    RECOGNIZED,
    assess,
    summarize,
)
from benchmark_federation.comparability.model import ReviewDefinition
from benchmark_federation.federation import Application, run, verify
from benchmark_federation.recognition.certificate_ledger import Repository

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "comparability.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def load_review() -> ReviewDefinition:
    return ReviewDefinition.from_dict(load_fixture()["comparability"])


def load_records() -> list[DomainRecord]:
    return records_from_fixture(load_fixture())


def assessment_by_id() -> dict[str, object]:
    review = load_review()
    return {record.record_id: assess(record, review) for record in load_records()}


class DenominatorAttributionTests(unittest.TestCase):
    def setUp(self):
        self.rows = assessment_by_id()

    def test_all_declared_metrics_are_attributed(self):
        for row in self.rows.values():
            self.assertEqual(len(row.metrics), 4)
            self.assertEqual(row.denominator["declared_metrics"], 4)

    def test_missing_metric_is_excluded_not_zero(self):
        row = self.rows["benchmark_case-c02"]
        self.assertEqual(row.metric("calibration").status, "missing")
        self.assertIsNone(row.metric("calibration").passed)
        self.assertFalse(row.metric("calibration").counted)
        self.assertEqual(row.denominator["comparable_weight"], 2.0)
        self.assertEqual(row.denominator["missing"], ["calibration", "latency_ms"])
        # Two comparable metrics both pass -> rate is 1.0, not 0.5.
        self.assertEqual(row.overall_pass_rate, 1.0)

    def test_waived_metric_is_excluded_not_zero_and_surfaced(self):
        row = self.rows["benchmark_case-c03"]
        waived = row.metric("refusal_rate")
        self.assertEqual(waived.status, "waived")
        self.assertIsNone(waived.passed)
        self.assertFalse(waived.counted)
        self.assertEqual(waived.waiver["waiver_id"], "WV-001")
        self.assertEqual(row.denominator["waived"], ["refusal_rate"])
        self.assertEqual(row.denominator["comparable_weight"], 3.0)
        self.assertEqual(row.overall_pass_rate, 1.0)
        self.assertEqual(row.conclusion, CONDITIONAL)

    def test_expired_waiver_is_not_honoured(self):
        review = ReviewDefinition.from_dict({
            **load_fixture()["comparability"],
            "reviewed_at": "2028-01-01T00:00:00+00:00",
        })
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c03")
        row = assess(record, review)
        self.assertEqual(row.metric("refusal_rate").status, "incomparable")
        self.assertIn("waiver_expired", row.metric("refusal_rate").reason)

    def test_scale_mapping_changes_value_not_denominator(self):
        row = self.rows["benchmark_case-c04"]
        accuracy = row.metric("accuracy")
        self.assertEqual(accuracy.status, "comparable")
        self.assertEqual(accuracy.raw_value, 83.0)
        self.assertAlmostEqual(accuracy.normalized_value, 0.83, places=6)
        self.assertEqual(accuracy.scale_factor, 0.01)
        latency = row.metric("latency_ms")
        self.assertEqual(latency.raw_value, 0.11)
        self.assertAlmostEqual(latency.normalized_value, 110.0, places=6)
        self.assertEqual(row.denominator["comparable_weight"], 4.0)

    def test_unapproved_conversion_is_incomparable(self):
        row = self.rows["benchmark_case-c06"]
        calibration = row.metric("calibration")
        self.assertEqual(calibration.status, "incomparable")
        self.assertEqual(calibration.reason, "unsupported_scale_conversion")
        self.assertIsNone(calibration.normalized_value)
        self.assertFalse(calibration.counted)

    def test_wrong_benchmark_version_is_incomparable(self):
        row = self.rows["benchmark_case-c08"]
        calibration = row.metric("calibration")
        self.assertEqual(calibration.status, "incomparable")
        self.assertEqual(calibration.reason, "benchmark_version_mismatch")

    def test_language_pack_without_mapping_has_no_decomposable_denominator(self):
        row = self.rows["benchmark_case-c05"]
        self.assertTrue(all(item.status == "incomparable" for item in row.metrics))
        self.assertEqual(row.denominator["comparable_weight"], 0.0)
        self.assertIsNone(row.overall_pass_rate)
        self.assertEqual(row.conclusion, INSUFFICIENT_EVIDENCE)

    def test_thin_denominator_does_not_turn_exclusions_into_failure(self):
        row = self.rows["benchmark_case-c08"]
        self.assertEqual(row.overall_pass_rate, 0.5)
        self.assertEqual(row.conclusion, INSUFFICIENT_EVIDENCE)
        self.assertIn("comparability_below_minimum", row.conclusion_reasons)

    def test_sensitivity_is_descriptive_only(self):
        row = self.rows["benchmark_case-c02"]
        sensitivity = row.metric("calibration").sensitivity
        self.assertIn("if_counted_as_pass", sensitivity)
        self.assertIn("if_counted_as_failure", sensitivity)
        # The reported denominator never moves because sensitivity was computed.
        self.assertEqual(row.denominator["comparable_weight"], 2.0)

    def test_summary_excludes_inadmissible_records_from_aggregate(self):
        summary = summarize(self.rows.values())
        self.assertEqual(summary["records"], 8)
        self.assertEqual(summary["conclusions"][INSUFFICIENT_EVIDENCE], 4)
        self.assertEqual(summary["records_excluded_from_aggregate"], 4)
        self.assertEqual(summary["records_in_aggregate"], 4)
        self.assertEqual(summary["excluded_records"],
                         ["benchmark_case-c02", "benchmark_case-c05", "benchmark_case-c06", "benchmark_case-c08"])
        self.assertAlmostEqual(summary["mean_effective_pass_rate"], 1.0)
        self.assertNotAlmostEqual(summary["mean_effective_pass_rate"],
                                 summary["mean_recorded_pass_rate"])

    def test_excess_waivers_do_not_create_a_failure(self):
        payload = load_fixture()
        payload["comparability"]["policy"]["max_waiver_share"] = 0.1
        review = ReviewDefinition.from_dict(payload["comparability"])
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c03")
        row = assess(record, review)
        self.assertEqual(row.overall_pass_rate, 1.0)
        self.assertEqual(row.conclusion, "insufficient_evidence")
        self.assertIn("waiver_share_above_limit", row.conclusion_reasons)

    def test_comparable_failure_still_fails(self):
        payload = load_fixture()
        payload["comparability"]["policy"]["minimum_comparability"] = 0.4
        payload["comparability"]["policy"]["allow_conditional"] = True
        review = ReviewDefinition.from_dict(payload["comparability"])
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c08")
        row = assess(record, review)
        # Only accuracy and latency are comparable; latency misses its threshold.
        self.assertEqual(row.overall_pass_rate, 0.5)
        self.assertEqual(row.conclusion, NOT_RECOGNIZED)

    def test_undeclared_observation_is_not_counted(self):
        payload = load_fixture()
        payload["comparability"]["observations"]["benchmark_case-c01"].append(
            {"metric_code": "rogue_metric", "value": 0.1, "evidence_ref": "x", "evidence_digest": "y"}
        )
        review = ReviewDefinition.from_dict(payload["comparability"])
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c01")
        row = assess(record, review)
        self.assertEqual(row.denominator["declared_weight"], 4.0)
        self.assertEqual(row.denominator["undeclared_observations"][0]["metric_code"], "rogue_metric")


class GatingTests(unittest.TestCase):
    def test_insufficient_evidence_never_becomes_a_rejection(self):
        from benchmark_federation.benchmarks.contract import Decision
        from benchmark_federation.federation import Application
        assessment = assessment_by_id()["benchmark_case-c05"]
        decision = Decision("benchmark_case-c05", "reject", 0.1, ("low",), (), {})
        self.assertEqual(Application._gate(decision, assessment).outcome, "reject")

    def test_insufficient_evidence_blocks_approval(self):
        from benchmark_federation.benchmarks.contract import Decision
        from benchmark_federation.federation import Application
        assessment = assessment_by_id()["benchmark_case-c05"]
        decision = Decision("benchmark_case-c05", "approve", 0.9, ("high",), (), {})
        gated = Application._gate(decision, assessment)
        self.assertEqual(gated.outcome, "review")
        self.assertIn("comparability=insufficient_evidence", gated.reasons)

    def test_conditional_lowers_approval_to_review(self):
        from benchmark_federation.benchmarks.contract import Decision
        from benchmark_federation.federation import Application
        assessment = assessment_by_id()["benchmark_case-c03"]
        decision = Decision("benchmark_case-c03", "approve", 0.9, ("high",), (), {})
        self.assertEqual(Application._gate(decision, assessment).outcome, "review")


class CertificateTraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "review.sqlite3"
        self.output = self.root / "output"

    def run_once(self):
        return run(FIXTURE, self.database, self.output)

    def test_certificate_pins_baseline_mapping_and_evidence(self):
        result = self.run_once()
        certificates = json.loads((self.output / "certificates.json").read_text(encoding="utf-8"))
        self.assertEqual(len(certificates), 8)
        review = load_review()
        mapping_digest = {mapping.mapping_id: mapping.digest for mapping in review.mappings}
        for certificate in certificates:
            self.assertEqual(certificate["baseline_version"], review.baseline.benchmark_version)
            self.assertEqual(certificate["baseline_digest"], review.baseline.digest)
            if certificate["mapping_id"] is None:
                # An unmapped language pack keeps the gap visible; it is never
                # back-filled with a default mapping.
                self.assertFalse(certificate["body"]["mapping"]["mapping_id"] is not None)
                self.assertIsNone(certificate["mapping_digest"])
            else:
                self.assertIn(certificate["mapping_id"], mapping_digest)
                self.assertEqual(certificate["mapping_digest"], mapping_digest[certificate["mapping_id"]])
            self.assertTrue(certificate["body"]["evidence_digests"])
            self.assertEqual(certificate["conclusion"], certificate["body"]["conclusion"])
        self.assertEqual(len(result["certificates"]), 8)

    def test_verified_bundle_and_database_agree(self):
        self.run_once()
        verification = verify(self.database, self.output)
        self.assertTrue(verification["ok"], verification)
        self.assertEqual(verification["certificate_errors"], [])
        self.assertEqual(verification["comparability_errors"], [])

    def test_bundle_denominator_audit_detects_zero_filling(self):
        self.run_once()
        path = self.output / "comparability.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for assessment in payload["assessments"]:
            if assessment["record_id"] == "benchmark_case-c02":
                for metric in assessment["metrics"]:
                    if metric["status"] == "missing":
                        metric["normalized_value"] = 0.0
                        metric["passed"] = False
                        metric["counted"] = True
        path.write_text(json.dumps(payload), encoding="utf-8")
        errors = verify_comparability(self.output)
        self.assertTrue(any("excluded metric" in error for error in errors), errors)
        self.assertTrue(any("counted metrics differ" in error for error in errors), errors)

    def test_bundle_archives_mapping_and_evidence_for_every_certificate(self):
        self.run_once()
        archive = json.loads((self.output / "review-archive.json").read_text(encoding="utf-8"))
        certificates = json.loads((self.output / "certificates.json").read_text(encoding="utf-8"))
        mapping_digests = {item["mapping_digest"] for item in certificates if item["mapping_digest"]}
        self.assertEqual(set(archive["mappings"]), mapping_digests)
        for digest, snapshot in archive["mappings"].items():
            self.assertEqual(snapshot["mapping_digest"], digest)
            self.assertTrue(snapshot["body"]["aliases"] is not None)
        baseline_digests = {item["baseline_digest"] for item in certificates}
        self.assertEqual(set(archive["baselines"]), baseline_digests)
        certified_evidence = {
            (item["record_id"], metric["evidence_digest"])
            for item in certificates for metric in item["body"]["metrics"] if metric.get("evidence_digest")
        }
        archived_evidence = {(item["record_id"], item["evidence_digest"]) for item in archive["evidence"].values()}
        self.assertEqual(certified_evidence, archived_evidence)

    def test_archive_preserves_the_mapping_used_after_a_later_revision(self):
        self.run_once()
        before = json.loads((self.output / "review-archive.json").read_text(encoding="utf-8"))
        payload = load_fixture()
        changed = copy.deepcopy(payload["comparability"])
        for mapping in changed["mappings"]:
            mapping["mapping_version"] = 7
            mapping["aliases"] = {**mapping["aliases"], "novelty": "accuracy"}
        review = ReviewDefinition.from_dict(changed)
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c01")
        Application(self.database, review=review).process(record)
        repository = Repository(self.database)
        latest = repository.latest_certificate("benchmark_case-c01")
        old_digest = next(digest for digest in before["mappings"] if digest != latest["mapping_digest"])
        old_snapshot = repository.mapping_snapshot(old_digest)
        self.assertIsNotNone(old_snapshot)
        self.assertEqual(old_snapshot["mapping_version"], 1)
        self.assertNotIn("novelty", old_snapshot["body"]["aliases"])

    def test_certificate_cross_reference_detects_surface_mismatch(self):
        self.run_once()
        path = self.output / "certificates.json"
        certificates = json.loads(path.read_text(encoding="utf-8"))
        certificates[0]["conclusion"] = "not_recognized"
        certificates[0]["body"]["conclusion"] = "not_recognized"
        path.write_text(json.dumps(certificates), encoding="utf-8")
        errors = verify_comparability(self.output)
        self.assertTrue(any("differs from its assessment" in error for error in errors), errors)

    def test_certificate_tampering_is_detected(self):
        self.run_once()
        repository = Repository(self.database)
        with repository.transaction() as connection:
            connection.execute("UPDATE certificates SET conclusion='recognized' WHERE record_id='benchmark_case-c05'")
        errors = repository.verify_certificates()
        self.assertTrue(errors)

    def test_superseded_certificate_is_retained_with_link(self):
        self.run_once()
        repository = Repository(self.database)
        original = repository.latest_certificate("benchmark_case-c01")
        payload = load_fixture()
        # New retest evidence for one metric, same baseline/mapping/policy.
        payload["comparability"]["observations"]["benchmark_case-c01"][0]["evidence_digest"] = "9" * 64
        review = ReviewDefinition.from_dict(payload["comparability"])
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c01")
        application = Application(self.database, review=review)
        application.process(record)
        latest = repository.latest_certificate("benchmark_case-c01")
        self.assertNotEqual(latest["certificate_id"], original["certificate_id"])
        self.assertEqual(latest["supersedes"], [original["certificate_id"]])
        self.assertEqual(latest["conclusion"], original["conclusion"])
        history = repository.certificate_history("benchmark_case-c01")
        self.assertEqual([item["status"] for item in history], ["superseded", "verified"])
        self.assertEqual(history[0]["superseded_by"], latest["certificate_id"])
        # The archived certificate still carries the old mapping/evidence.
        self.assertEqual(history[0]["mapping_digest"], original["mapping_digest"])
        self.assertNotEqual(history[0]["evidence_digest"], latest["evidence_digest"])

    def test_mapping_update_only_affects_subsequent_reviews(self):
        self.run_once()
        repository = Repository(self.database)
        original = repository.latest_certificate("benchmark_case-c04")
        payload = load_fixture()
        changed = copy.deepcopy(payload["comparability"])
        for mapping in changed["mappings"]:
            mapping["mapping_version"] = 2
            if mapping["mapping_id"] == "lang-en-v1":
                mapping["confidence_floor"] = 0.95
        review = ReviewDefinition.from_dict(changed)
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c04")
        Application(self.database, review=review).process(record)
        latest = repository.latest_certificate("benchmark_case-c04")
        self.assertNotEqual(latest["certificate_id"], original["certificate_id"])
        self.assertNotEqual(latest["mapping_digest"], original["mapping_digest"])
        history = repository.certificate_history("benchmark_case-c04")
        self.assertEqual(history[0]["certificate_id"], original["certificate_id"])
        self.assertEqual(history[0]["status"], "superseded")

    def test_same_review_cannot_publish_a_different_verified_conclusion(self):
        self.run_once()
        repository = Repository(self.database)
        original = repository.latest_certificate("benchmark_case-c01")
        certificate = build_certificate(
            assess(next(item for item in load_records() if item.record_id == "benchmark_case-c01"), load_review())
        )
        # Same review fingerprint, different conclusion: this is exactly the
        # silent-drift case the ledger must refuse.
        from dataclasses import replace
        drifted = replace(certificate, conclusion="not_recognized",
                          body={**certificate.body, "conclusion": "not_recognized"})
        from benchmark_federation.certificates.certificate import Certificate
        rebuilt = Certificate(
            certificate_id=__import__("benchmark_federation.benchmarks.contract", fromlist=["stable_hash"]).stable_hash(
                dict(drifted.body)),
            record_id=drifted.record_id, baseline_family=drifted.baseline_family,
            baseline_version=drifted.baseline_version, baseline_digest=drifted.baseline_digest,
            mapping_id=drifted.mapping_id, mapping_version=drifted.mapping_version,
            mapping_digest=drifted.mapping_digest, policy_digest=drifted.policy_digest,
            evidence_digest=drifted.evidence_digest, review_digest=drifted.review_digest,
            conclusion="not_recognized", body=drifted.body, issued_at=drifted.issued_at,
        )
        with self.assertRaisesRegex(ContractError, "silently drift"):
            repository.publish_certificate(rebuilt)
        self.assertEqual(repository.latest_certificate("benchmark_case-c01")["certificate_id"],
                         original["certificate_id"])

    def test_repeated_review_is_idempotent(self):
        self.run_once()
        repository = Repository(self.database)
        before = repository.certificate_history()
        application = Application(self.database, review=load_review())
        for record in load_records():
            application.process(record)
        after = repository.certificate_history()
        self.assertEqual([item["certificate_id"] for item in before], [item["certificate_id"] for item in after])
        self.assertEqual({item["status"] for item in after}, {"verified"})

    def test_certificate_verification_rejects_duplicate_verified(self):
        self.run_once()
        repository = Repository(self.database)
        certificate = repository.latest_certificate("benchmark_case-c01")
        with repository.transaction() as connection:
            row = connection.execute("SELECT * FROM certificates WHERE certificate_id=?",
                                     (certificate["certificate_id"],)).fetchone()
            connection.execute(
                "INSERT INTO certificates(certificate_id,record_id,baseline_family,baseline_version,baseline_digest,"
                "mapping_id,mapping_version,mapping_digest,policy_digest,evidence_digest,review_digest,conclusion,"
                "status,supersedes_json,superseded_by,body_json,issued_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (row["certificate_id"] + "-copy", row["record_id"], row["baseline_family"], row["baseline_version"],
                 row["baseline_digest"], row["mapping_id"], row["mapping_version"], row["mapping_digest"],
                 row["policy_digest"], row["evidence_digest"], row["review_digest"], row["conclusion"],
                 "verified", row["supersedes_json"], None, row["body_json"], row["issued_at"], row["updated_at"]),
            )
        errors = repository.verify_certificates()
        self.assertTrue(any("has 2 verified certificates" in error for error in errors), errors)


class MappingAliasTests(unittest.TestCase):
    def test_non_latin_aliases_do_not_collapse(self):
        review = load_review()
        mapping = next(item for item in review.mappings if item.mapping_id == "lang-zh-v1")
        self.assertEqual(mapping.aliases["准确率"], "accuracy")
        self.assertEqual(mapping.aliases["拒绝率"], "refusal_rate")

    def test_source_metric_is_resolved_through_the_pinned_mapping(self):
        rows = assessment_by_id()
        self.assertEqual(rows["benchmark_case-c01"].metric("accuracy").status, "comparable")
        self.assertEqual(rows["benchmark_case-c01"].metric("refusal_rate").status, "comparable")

    def test_unmapped_source_metric_label_is_incomparable(self):
        payload = load_fixture()
        payload["comparability"]["observations"]["benchmark_case-c01"][0]["source_metric"] = "wrong_label"
        review = ReviewDefinition.from_dict(payload["comparability"])
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c01")
        row = assess(record, review)
        self.assertEqual(row.metric("accuracy").status, "incomparable")
        self.assertEqual(row.metric("accuracy").reason, "source_metric_not_mapped_to_baseline_metric")

    def test_conflicting_alias_targets_are_rejected(self):
        payload = load_fixture()["comparability"]
        payload["mappings"][1]["aliases"]["Accuracy"] = "refusal_rate"
        payload["mappings"][1]["aliases"]["accuracy"] = "accuracy"
        with self.assertRaisesRegex(ContractError, "conflicting targets"):
            ReviewDefinition.from_dict(payload)


class ReviewDefinitionTests(unittest.TestCase):
    def test_language_pack_mapping_is_pinned(self):
        review = load_review()
        records = {record.record_id: record for record in load_records()}
        self.assertEqual(review.mapping_for(records["benchmark_case-c01"]).mapping_id, "lang-zh-v1")
        self.assertEqual(review.mapping_for(records["benchmark_case-c02"]).mapping_id, "lang-en-v1")

    def test_unknown_language_pack_is_not_silently_defaulted(self):
        payload = load_fixture()
        payload["comparability"]["default_mapping_id"] = "lang-en-v1"
        review = ReviewDefinition.from_dict(payload["comparability"])
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c05")
        # An explicit default is honoured; without one the pack is unmapped.
        self.assertEqual(review.mapping_for(record).mapping_id, "lang-en-v1")
        strict_review = ReviewDefinition.from_dict(load_fixture()["comparability"])
        with self.assertRaises(ContractError):
            strict_review.mapping_for(record)

    def test_duplicate_metric_codes_are_rejected(self):
        payload = load_fixture()["comparability"]
        payload["baseline"]["metrics"].append(copy.deepcopy(payload["baseline"]["metrics"][0]))
        with self.assertRaisesRegex(ContractError, "duplicate metric"):
            ReviewDefinition.from_dict(payload)

    def test_waiver_requires_scope_reason_and_approver(self):
        payload = load_fixture()["comparability"]
        waiver = payload["observations"]["benchmark_case-c03"][1]["waiver"]
        payload["observations"]["benchmark_case-c03"][1]["waiver"] = {**waiver, "scope": ["accuracy"]}
        review = ReviewDefinition.from_dict(payload)
        record = next(item for item in load_records() if item.record_id == "benchmark_case-c03")
        row = assess(record, review)
        self.assertEqual(row.metric("refusal_rate").status, "incomparable")
        self.assertEqual(row.metric("refusal_rate").reason, "waiver_scope_mismatch")


class NoFixtureReviewTests(unittest.TestCase):
    def test_plain_acceptance_fixture_is_unchanged(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        database, output = root / "plain.sqlite3", root / "plain"
        run(Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json", database, output)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["files"]), {"summary.json", "decisions.json", "audit-events.json"})
        self.assertNotIn("supporting_files", manifest)
        self.assertTrue(verify(database, output)["ok"])


if __name__ == "__main__":
    unittest.main()
