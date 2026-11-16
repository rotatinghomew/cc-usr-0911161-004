from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from benchmark_federation.benchmarks.contract import ContractError, stable_hash, utc_now
from benchmark_federation.comparability.engine import ComparabilityAssessment


CERTIFICATE_SCHEMA_VERSION = 1


def _review_digest(assessment: ComparabilityAssessment) -> str:
    return assessment.review_digest


def build_certificate_body(assessment: ComparabilityAssessment) -> dict[str, Any]:
    """Build the immutable body of a recognition certificate.

    Everything needed to reconstruct the recognition conclusion is in the
    body: the pinned baseline, the exact mapping version/digest (or the
    explicit statement that no mapping was resolved), the policy, the
    per-metric attribution, and the digests of the raw evidence.  No
    timestamp enters the body so that the same review produces the same
    certificate identifier and cannot silently drift.
    """
    return {
        "schema_version": CERTIFICATE_SCHEMA_VERSION,
        "record_id": assessment.record_id,
        "baseline": {
            "benchmark_family": assessment.baseline_family,
            "benchmark_version": assessment.baseline_version,
            "digest": assessment.baseline_digest,
        },
        "mapping": {
            "mapping_id": assessment.mapping_id,
            "mapping_version": assessment.mapping_version,
            "language_pack": assessment.mapping_language_pack,
            "resolved": assessment.mapping_resolved,
            "unresolved_reason": assessment.mapping_reason,
            "digest": assessment.mapping_digest,
        },
        "policy": assessment.policy,
        "policy_digest": assessment.policy_digest,
        "review_digest": _review_digest(assessment),
        "evidence_digest": stable_hash(list(assessment.evidence_digests)),
        "evidence_digests": list(assessment.evidence_digests),
        "denominator": assessment.denominator,
        "effective_pass_rate": assessment.overall_pass_rate,
        "recorded_retest_pass_rate": assessment.recorded_retest_pass_rate,
        "conclusion": assessment.conclusion,
        "conclusion_reasons": list(assessment.conclusion_reasons),
        "metrics": [item.as_dict() for item in assessment.metrics],
    }


@dataclass(frozen=True)
class Certificate:
    certificate_id: str
    record_id: str
    baseline_family: str
    baseline_version: str
    baseline_digest: str
    mapping_id: str | None
    mapping_version: int | None
    mapping_digest: str | None
    policy_digest: str
    evidence_digest: str
    review_digest: str
    conclusion: str
    body: Mapping[str, Any]
    issued_at: str
    status: str = "verified"

    @property
    def content_hash(self) -> str:
        return stable_hash(dict(self.body))

    def as_dict(self) -> dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "record_id": self.record_id,
            "baseline_family": self.baseline_family,
            "baseline_version": self.baseline_version,
            "baseline_digest": self.baseline_digest,
            "mapping_id": self.mapping_id,
            "mapping_version": self.mapping_version,
            "mapping_digest": self.mapping_digest,
            "policy_digest": self.policy_digest,
            "evidence_digest": self.evidence_digest,
            "review_digest": self.review_digest,
            "conclusion": self.conclusion,
            "status": self.status,
            "issued_at": self.issued_at,
            "body": dict(self.body),
        }

    def integrity_errors(self) -> list[str]:
        errors: list[str] = []
        if stable_hash(dict(self.body)) != self.certificate_id:
            errors.append("certificate content hash does not match certificate_id")
        baseline = self.body.get("baseline", {})
        mapping = self.body.get("mapping", {})
        if baseline.get("digest") != self.baseline_digest:
            errors.append("certificate baseline digest drift")
        if baseline.get("benchmark_version") != self.baseline_version:
            errors.append("certificate baseline version drift")
        if mapping.get("digest") != self.mapping_digest or mapping.get("mapping_id") != self.mapping_id:
            errors.append("certificate mapping reference drift")
        if mapping.get("language_pack") != self.body.get("mapping", {}).get("language_pack"):
            errors.append("certificate mapping language pack drift")
        if self.body.get("conclusion") != self.conclusion:
            errors.append("certificate conclusion drift")
        if stable_hash(list(self.body.get("evidence_digests", []))) != self.evidence_digest:
            errors.append("certificate evidence digest drift")
        return errors


def build_certificate(assessment: ComparabilityAssessment, issued_at: str | None = None) -> Certificate:
    body = build_certificate_body(assessment)
    certificate_id = stable_hash(body)
    return Certificate(
        certificate_id=certificate_id,
        record_id=assessment.record_id,
        baseline_family=assessment.baseline_family,
        baseline_version=assessment.baseline_version,
        baseline_digest=assessment.baseline_digest,
        mapping_id=assessment.mapping_id,
        mapping_version=assessment.mapping_version,
        mapping_digest=assessment.mapping_digest,
        policy_digest=assessment.policy_digest,
        evidence_digest=stable_hash(list(assessment.evidence_digests)),
        review_digest=_review_digest(assessment),
        conclusion=assessment.conclusion,
        body=body,
        issued_at=issued_at or utc_now(),
    )


def build_certificates(assessments: Any, issued_at: str | None = None) -> list[Certificate]:
    return [build_certificate(item, issued_at) for item in assessments]


def _field(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def supersession_reason(previous: Any, replacement: Any) -> str:
    """Name the review surface that changed between two certificates.

    Accepts either ``Certificate`` objects or certificate row mappings, so the
    ledger can record the reason without re-deriving it.
    """
    changes = []
    if _field(previous, "baseline_digest") != _field(replacement, "baseline_digest"):
        changes.append("baseline_updated")
    if _field(previous, "mapping_digest") != _field(replacement, "mapping_digest"):
        changes.append("mapping_updated")
    if _field(previous, "evidence_digest") != _field(replacement, "evidence_digest"):
        changes.append("retest_evidence_updated")
    if _field(previous, "policy_digest") != _field(replacement, "policy_digest"):
        changes.append("policy_updated")
    return "+".join(changes) or "recognition_reassessed"


def ensure_no_silent_drift(previous: Any, replacement: Any) -> None:
    """A verified conclusion may only change through a new review surface.

    If the baseline, mapping, policy and evidence are all identical, the
    recognition conclusion must be identical too.  A differing conclusion
    under an unchanged review fingerprint is a silent drift and is rejected.
    """
    if _field(previous, "certificate_id") == _field(replacement, "certificate_id"):
        return
    if _field(previous, "review_digest") == _field(replacement, "review_digest"):
        raise ContractError(
            "verified conclusion would silently drift for unchanged baseline/mapping/evidence/policy"
        )
