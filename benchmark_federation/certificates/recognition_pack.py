from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from benchmark_federation.benchmarks.contract import Decision, DomainRecord, stable_hash, utc_now


def ensure_output(path: str | Path) -> Path:
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_json(path: Path, value: Any) -> str:
    body = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    path.write_text(body + "\n", encoding="utf-8")
    return stable_hash(value)


def write_records(path: Path, records: Iterable[DomainRecord], decisions: Mapping[str, Decision]) -> int:
    rows = []
    for record in records:
        decision = decisions.get(record.record_id)
        rows.append({"record_id": record.record_id, "state": record.state, "version": record.version,
                     "source": record.source, "fingerprint": record.fingerprint,
                     "outcome": decision.outcome if decision else "", "score": decision.score if decision else ""})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "state", "version", "source", "fingerprint", "outcome", "score"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_rules(path: Path, decisions: Mapping[str, Decision]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "code", "passed", "score", "severity", "message"])
        writer.writeheader()
        for record_id, decision in sorted(decisions.items()):
            for result in decision.rule_results:
                writer.writerow({"record_id": record_id, "code": result.code, "passed": result.passed,
                                 "score": result.score, "severity": result.severity, "message": result.message})
                count += 1
    return count


def build_summary(records: list[DomainRecord], decisions: Mapping[str, Decision], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    for decision in decisions.values():
        outcomes[decision.outcome] = outcomes.get(decision.outcome, 0) + 1
    scores = [decision.score for decision in decisions.values()]
    return {"product": '多国人工智能评测基准互认验证台', "entity": 'benchmark_case', "generated_at": utc_now(),
            "record_count": len(records), "decision_count": len(decisions), "outcomes": outcomes,
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "minimum_score": min(scores) if scores else 0.0, "maximum_score": max(scores) if scores else 0.0,
            "repository": snapshot}


def export_bundle(output: str | Path, records: list[DomainRecord], decisions: Mapping[str, Decision],
                  snapshot: Mapping[str, Any], events: list[dict[str, Any]],
                  comparability: Mapping[str, Any] | None = None,
                  certificates: list[Any] | None = None,
                  supporting: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = ensure_output(output)
    summary = build_summary(records, decisions, snapshot)
    if comparability is not None:
        summary["comparability"] = comparability.get("summary", {})
        summary["comparability_context"] = {
            "baseline": comparability.get("baseline"),
            "mappings": comparability.get("mappings"),
            "policy_digest": comparability.get("policy_digest"),
            "aggregate_basis": "comparable metrics only",
        }
    record_count = write_records(root / "records.csv", records, decisions)
    rule_count = write_rules(root / "rules.csv", decisions)
    summary_hash = write_json(root / "summary.json", summary)
    decision_hash = write_json(root / "decisions.json", [value.as_dict() for _, value in sorted(decisions.items())])
    event_hash = write_json(root / "audit-events.json", events)
    files = {"summary.json": summary_hash, "decisions.json": decision_hash,
             "audit-events.json": event_hash}
    supporting_files: dict[str, str] = {}
    if comparability is not None:
        supporting_files["comparability.json"] = write_json(root / "comparability.json", dict(comparability))
    if certificates is not None:
        supporting_files["certificates.json"] = write_json(
            root / "certificates.json", [item.as_dict() for item in certificates]
        )
    for name, value in (supporting or {}).items():
        supporting_files[name] = write_json(root / name, value)
    manifest = {"files": files, "record_rows": record_count,
                "rule_rows": rule_count, "created_at": utc_now()}
    if supporting_files:
        manifest["supporting_files"] = supporting_files
    manifest["manifest_hash"] = stable_hash(manifest)
    write_json(root / "manifest.json", manifest)
    return manifest


def verify_comparability(output: str | Path) -> list[str]:
    """Check the exported comparability surface for denominator integrity.

    This is a structural audit of the bundle, independent of the database:
    excluded metrics must never be counted, and the declared pass rate must be
    the weighted rate over comparable metrics only.
    """
    root = Path(output)
    path = root / "comparability.json"
    if not path.is_file():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["comparability.json is not valid JSON"]
    errors: list[str] = []
    for assessment in value.get("assessments", []):
        record_id = assessment.get("record_id", "<unknown>")
        metrics = assessment.get("metrics", [])
        denominator = assessment.get("denominator", {})
        comparable = [item for item in metrics if item.get("status") == "comparable"]
        counted = [item for item in metrics if item.get("counted")]
        if {item["metric_code"] for item in comparable} != {item["metric_code"] for item in counted}:
            errors.append(f"{record_id}: counted metrics differ from comparable metrics")
        declared = sum(float(item.get("weight", 0.0)) for item in metrics)
        comparable_weight = sum(float(item.get("weight", 0.0)) for item in comparable)
        if abs(declared - float(denominator.get("declared_weight", -1.0))) > 1e-6:
            errors.append(f"{record_id}: declared weight is inconsistent")
        if abs(comparable_weight - float(denominator.get("comparable_weight", -1.0))) > 1e-6:
            errors.append(f"{record_id}: comparable weight is inconsistent")
        for item in metrics:
            if item.get("status") != "comparable":
                if item.get("passed") is not None:
                    errors.append(f"{record_id}: excluded metric {item.get('metric_code')} carries a pass verdict")
                if item.get("normalized_value") is not None:
                    errors.append(f"{record_id}: excluded metric {item.get('metric_code')} carries a normalized value")
        effective = assessment.get("overall_pass_rate")
        if comparable_weight > 0:
            expected = sum(float(item.get("weight", 0.0)) for item in comparable if item.get("passed"))
            expected /= comparable_weight
            if effective is None or abs(float(effective) - expected) > 1e-6:
                errors.append(f"{record_id}: effective pass rate does not match comparable denominator")
        elif effective is not None:
            errors.append(f"{record_id}: effective pass rate present without a comparable denominator")
    errors.extend(_verify_certificate_cross_reference(root, value))
    return errors


def _verify_certificate_cross_reference(root: Path, comparability: Mapping[str, Any]) -> list[str]:
    """Certificates must restate the exact review they were issued from.

    This catches a bundle where the certificate face and the comparability
    surface disagree, which would otherwise let a verified conclusion appear
    to drift without a new review.
    """
    path = root / "certificates.json"
    if not path.is_file():
        return []
    errors: list[str] = []
    try:
        certificates = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["certificates.json is not valid JSON"]
    assessments = {item.get("record_id"): item for item in comparability.get("assessments", [])}
    baseline_digest = comparability.get("baseline_digest")
    for certificate in certificates:
        record_id = certificate.get("record_id")
        body = certificate.get("body", {})
        assessment = assessments.get(record_id)
        if assessment is None:
            errors.append(f"certificate {record_id} has no comparability assessment")
            continue
        if body.get("review_digest") != assessment.get("review_digest"):
            errors.append(f"certificate {record_id} was issued from a different review")
        if body.get("baseline", {}).get("digest") != baseline_digest:
            errors.append(f"certificate {record_id} references a different baseline")
        if certificate.get("conclusion") != assessment.get("conclusion"):
            errors.append(f"certificate {record_id} conclusion differs from its assessment")
        if body.get("effective_pass_rate") != assessment.get("overall_pass_rate"):
            errors.append(f"certificate {record_id} pass rate differs from its assessment")
        mapping_digest = (body.get("mapping") or {}).get("digest")
        if mapping_digest and mapping_digest not in (comparability.get("mapping_digests") or {}).values():
            errors.append(f"certificate {record_id} references an unknown mapping revision")
    return errors


def verify_bundle(output: str | Path) -> list[str]:
    root = Path(output)
    errors: list[str] = []
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return ["manifest.json is missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest_hash = manifest.pop("manifest_hash", "")
    if stable_hash(manifest) != expected_manifest_hash:
        errors.append("manifest hash mismatch")
    declared = dict(manifest.get("files", {}))
    declared.update(manifest.get("supporting_files", {}))
    for name, expected in declared.items():
        path = root / name
        if not path.is_file():
            errors.append(f"{name} is missing")
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if stable_hash(value) != expected:
            errors.append(f"{name} hash mismatch")
    return errors
