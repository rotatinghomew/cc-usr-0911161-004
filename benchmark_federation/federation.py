from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from benchmark_federation.benchmarks.contract import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from benchmark_federation.certificates.certificate import build_certificate
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
from benchmark_federation.recognition.certificate_ledger import Repository
from benchmark_federation.retest.execution import advance_for_outcome, decide
from benchmark_federation.translation.metric_bridge import derive_context

from benchmark_federation.recognition_signal.recognition_confidence import augment_context

COMPARABILITY_FLOOR = {
    RECOGNIZED: "approve",
    CONDITIONAL: "review",
    NOT_RECOGNIZED: "reject",
    # Insufficient evidence blocks approval but must not expire the record:
    # it goes back to review so new evidence or a new mapping can be supplied.
    INSUFFICIENT_EVIDENCE: "review",
}


class Application:
    def __init__(self, database: str | Path, context: Mapping[str, Any] | None = None,
                 review: ReviewDefinition | None = None):
        self.repository = Repository(database)
        self.context = dict(context or {})
        self.review = review
        self._certificates: dict[str, Any] = {}
        self._assessments: dict[str, Any] = {}

    def ingest(self, record: DomainRecord) -> DomainRecord:
        current = self.repository.get_record(record.record_id)
        if current is None:
            self.repository.save_record(record)
            return record
        if current.fingerprint == record.fingerprint:
            return current
        replacement = DomainRecord(record.record_id, record.payload, current.state,
                                   current.version + 1, record.occurred_at, record.source)
        self.repository.save_record(replacement, expected_version=current.version)
        return replacement

    def assess(self, record: DomainRecord) -> Any:
        if self.review is None:
            return None
        return assess(record, self.review, at=self.review.reviewed_at)

    def process(self, record: DomainRecord) -> tuple[DomainRecord, Decision]:
        stored = self.ingest(record)
        context = dict(self.context)
        context.update(derive_context(stored, self.repository))
        context.update(augment_context(stored, self.repository))
        decision = decide(stored, context)
        assessment = self.assess(stored)
        if assessment is not None:
            decision = self._gate(decision, assessment)
        self.repository.save_decision(decision)
        advanced = advance_for_outcome(stored, decision)
        if advanced.fingerprint != stored.fingerprint:
            self.repository.save_record(advanced, expected_version=stored.version)
        if assessment is not None:
            certificate = build_certificate(assessment)
            self.repository.publish_certificate(certificate, review=self.review)
            self._certificates[stored.record_id] = certificate
            self._assessments[stored.record_id] = assessment
        return advanced, decision

    @staticmethod
    def _gate(decision: Decision, assessment: Any) -> Decision:
        """Comparability conclusions gate *positive* recognition only.

        An incomparable or missing metric is never re-used as a failure or a
        zero, so it may not create a negative recognition outcome either.  It
        can only block an approval: approve is lowered to the comparability
        floor (review / reject / hold).  Existing review, reject or hold
        decisions are left untouched.
        """
        if decision.outcome != "approve":
            return decision
        floor = COMPARABILITY_FLOOR[assessment.conclusion]
        if floor == "approve":
            return decision
        reasons = decision.reasons + (
            f"comparability={assessment.conclusion}",
            f"effective_pass_rate={assessment.overall_pass_rate}",
        )
        return replace(decision, outcome=floor, reasons=reasons)

    def run_fixture(self, fixture: Mapping[str, Any], output: str | Path) -> dict[str, Any]:
        records = records_from_fixture(fixture)
        review = self.review
        comparability_payload = fixture.get("comparability")
        if review is None and isinstance(comparability_payload, Mapping):
            review = ReviewDefinition.from_dict(comparability_payload)
        self.review = review
        if review is not None:
            # Only the schema run needs the full review block; observations are
            # part of the review surface, so a different evidence set yields a
            # different fixture hash and a different run.
            fixture_hash = stable_hash({"fixture": fixture,
                                        "review_digest": review.digest,
                                        "observations_digest": stable_hash(
                                            {key: [item.as_dict() for item in value]
                                             for key, value in review.observations.items()})})
        else:
            fixture_hash = stable_hash(fixture)
        run_id = self.repository.begin_run(fixture_hash, len(records))
        completed = self.repository.completed_run(run_id)
        if completed is not None:
            return completed
        decisions: dict[str, Decision] = {}
        final_records: list[DomainRecord] = []
        assessments: list[Any] = []
        certificates: list[Any] = []
        self._certificates = {}
        self._assessments = {}
        for record in records:
            final_record, decision = self.process(record)
            final_records.append(final_record)
            decisions[record.record_id] = decision
            if review is not None:
                assessments.append(self._assessments[record.record_id])
                certificates.append(self._certificates[record.record_id])
        snapshot = self.repository.snapshot()
        certificate_errors = self.repository.verify_certificates()
        if snapshot["chain_errors"] or certificate_errors:
            raise ContractError("audit chain verification failed")
        comparability = None
        if review is not None:
            comparability = {
                "review": review.as_dict(),
                "review_definition_digest": review.digest,
                "baseline": review.baseline.as_dict(),
                "baseline_digest": review.baseline.digest,
                "mappings": [mapping.as_dict() for mapping in review.mappings],
                "mapping_digests": {mapping.mapping_id: mapping.digest for mapping in review.mappings},
                "policy_digest": stable_hash(review.policy.as_dict()),
                "assessments": [item.as_dict() for item in assessments],
                "summary": summarize(assessments),
            }
        manifest = export_bundle(output, final_records, decisions, snapshot, self.repository.event_rows(),
                                 comparability=comparability,
                                 certificates=certificates if review is not None else None,
                                 supporting=(self._review_archive(certificates) if review is not None else None))
        result = {"run_id": run_id, "fixture_hash": fixture_hash, "records": len(final_records),
                  "decisions": len(decisions), "manifest": manifest, "snapshot": snapshot}
        if comparability is not None:
            result["comparability"] = comparability["summary"]
            result["certificates"] = [item.certificate_id for item in certificates]
        self.repository.finish_run(run_id, result)
        return result

    def _review_archive(self, certificates: list[Any]) -> dict[str, Any]:
        """Bundle the pinned review surface next to the certificates.

        The archive is derived from the database snapshots that the ledger
        froze when each certificate was published, so re-exporting a bundle
        later still describes the mapping and evidence actually used.
        """
        mappings = {}
        baselines = {}
        evidence: dict[str, Any] = {}
        for certificate in certificates:
            if certificate.baseline_digest not in baselines:
                snapshot = self.repository.baseline_snapshot(certificate.baseline_digest)
                if snapshot is not None:
                    baselines[certificate.baseline_digest] = snapshot
            if certificate.mapping_digest and certificate.mapping_digest not in mappings:
                snapshot = self.repository.mapping_snapshot(certificate.mapping_digest)
                if snapshot is not None:
                    mappings[certificate.mapping_digest] = snapshot
            for item in self.repository.evidence_for(certificate.record_id):
                key = f"{item['record_id']}:{item['metric_code']}:{item['evidence_digest']}"
                evidence[key] = item
        return {
            "review-archive.json": {
                "baselines": baselines,
                "mappings": mappings,
                "evidence": evidence,
            }
        }

    def inspect(self) -> dict[str, Any]:
        return {"snapshot": self.repository.snapshot(),
                "records": [record.__dict__ for record in self.repository.list_records()],
                "decisions": self.repository.decision_rows(),
                "certificates": self.repository.certificate_rows()}


def load_review(path: str | Path) -> ReviewDefinition:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read review: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError("review root must be an object")
    return ReviewDefinition.from_dict(value)


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read fixture: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("fixture root must be an object")
    return value


def run(fixture_path: str | Path, database: str | Path, output: str | Path,
        context: Mapping[str, Any] | None = None, review: ReviewDefinition | None = None) -> dict[str, Any]:
    return Application(database, context, review).run_fixture(load_fixture(fixture_path), output)


def verify(database: str | Path, output: str | Path) -> dict[str, Any]:
    repository = Repository(database)
    chain_errors = repository.verify_chain()
    bundle_errors = verify_bundle(output)
    certificate_errors = repository.verify_certificates()
    comparability_errors = verify_comparability(output)
    return {"ok": not chain_errors and not bundle_errors and not certificate_errors and not comparability_errors,
            "chain_errors": chain_errors, "bundle_errors": bundle_errors,
            "certificate_errors": certificate_errors, "comparability_errors": comparability_errors,
            "snapshot": repository.snapshot()}
