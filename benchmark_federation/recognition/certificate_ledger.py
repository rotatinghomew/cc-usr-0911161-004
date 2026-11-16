from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from benchmark_federation.benchmarks.contract import Decision, DomainRecord, ContractError, canonical_json, stable_hash, utc_now


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS records(
    record_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    state TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    source TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS record_versions(
    record_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    state TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    stored_at TEXT NOT NULL,
    PRIMARY KEY(record_id, version)
);
CREATE TABLE IF NOT EXISTS decisions(
    decision_id TEXT PRIMARY KEY,
    record_id TEXT NOT NULL,
    outcome TEXT NOT NULL,
    score REAL NOT NULL,
    decision_json TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    FOREIGN KEY(record_id) REFERENCES records(record_id)
);
CREATE TABLE IF NOT EXISTS events(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    aggregate_version INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    UNIQUE(aggregate_id, aggregate_version, event_type)
);
CREATE TABLE IF NOT EXISTS runs(
    run_id TEXT PRIMARY KEY,
    fixture_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    record_count INTEGER NOT NULL,
    result_json TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT
);
CREATE TABLE IF NOT EXISTS certificates(
    certificate_id TEXT PRIMARY KEY,
    record_id TEXT NOT NULL,
    baseline_family TEXT NOT NULL,
    baseline_version TEXT NOT NULL,
    baseline_digest TEXT NOT NULL,
    mapping_id TEXT,
    mapping_version INTEGER,
    mapping_digest TEXT,
    policy_digest TEXT NOT NULL,
    evidence_digest TEXT NOT NULL,
    review_digest TEXT NOT NULL,
    conclusion TEXT NOT NULL,
    status TEXT NOT NULL,
    supersedes_json TEXT NOT NULL,
    superseded_by TEXT,
    body_json TEXT NOT NULL,
    issued_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(record_id) REFERENCES records(record_id)
);
CREATE TABLE IF NOT EXISTS review_snapshots(
    review_digest TEXT PRIMARY KEY,
    baseline_digest TEXT NOT NULL,
    policy_digest TEXT NOT NULL,
    body_json TEXT NOT NULL,
    stored_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS baseline_snapshots(
    baseline_digest TEXT PRIMARY KEY,
    benchmark_family TEXT NOT NULL,
    benchmark_version TEXT NOT NULL,
    body_json TEXT NOT NULL,
    stored_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mapping_snapshots(
    mapping_digest TEXT PRIMARY KEY,
    mapping_id TEXT NOT NULL,
    mapping_version INTEGER NOT NULL,
    language_pack TEXT,
    body_json TEXT NOT NULL,
    stored_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence_ledger(
    evidence_digest TEXT NOT NULL,
    record_id TEXT NOT NULL,
    metric_code TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    body_json TEXT NOT NULL,
    stored_at TEXT NOT NULL,
    PRIMARY KEY(record_id, metric_code, evidence_digest)
);
CREATE INDEX IF NOT EXISTS idx_records_state ON records(state, updated_at);
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_id, event_id);
CREATE INDEX IF NOT EXISTS idx_decisions_record ON decisions(record_id, decided_at);
CREATE INDEX IF NOT EXISTS idx_certificates_record ON certificates(record_id, status, issued_at);
CREATE INDEX IF NOT EXISTS idx_evidence_record ON evidence_ledger(record_id, evidence_digest);
"""


class Repository:
    def __init__(self, database: str | Path):
        self.database = str(database)
        self._lock = threading.RLock()
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            connection = self.connect()
            try:
                connection.execute("BEGIN IMMEDIATE")
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()

    def _last_hash(self, connection: sqlite3.Connection) -> str:
        row = connection.execute("SELECT event_hash FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
        return row[0] if row else "0" * 64

    def append_event(self, connection: sqlite3.Connection, event_type: str,
                     aggregate_id: str, aggregate_version: int, payload: Mapping[str, Any]) -> str:
        previous = self._last_hash(connection)
        created_at = utc_now()
        event_hash = stable_hash({"event_type": event_type, "aggregate_id": aggregate_id,
                                  "aggregate_version": aggregate_version, "payload": payload,
                                  "previous_hash": previous, "created_at": created_at})
        try:
            connection.execute("INSERT INTO events(event_type,aggregate_id,aggregate_version,payload_json,previous_hash,event_hash,created_at) VALUES(?,?,?,?,?,?,?)",
                               (event_type, aggregate_id, aggregate_version, canonical_json(payload),
                                previous, event_hash, created_at))
        except sqlite3.IntegrityError:
            row = connection.execute("SELECT event_hash,payload_json FROM events WHERE aggregate_id=? AND aggregate_version=? AND event_type=?",
                                     (aggregate_id, aggregate_version, event_type)).fetchone()
            if row and row[1] == canonical_json(payload):
                return row[0]
            raise ContractError("conflicting event replay") from None
        return event_hash

    def save_record(self, record: DomainRecord, expected_version: int | None = None) -> str:
        with self.transaction() as connection:
            current = connection.execute("SELECT version,fingerprint FROM records WHERE record_id=?", (record.record_id,)).fetchone()
            if current and expected_version is not None and current[0] != expected_version:
                raise ContractError("optimistic version conflict")
            if current and current[1] == record.fingerprint:
                return record.fingerprint
            if current and record.version <= current[0]:
                raise ContractError("record version must advance")
            payload = canonical_json(record.payload)
            connection.execute("INSERT INTO records(record_id,version,state,payload_json,fingerprint,occurred_at,source,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(record_id) DO UPDATE SET version=excluded.version,state=excluded.state,payload_json=excluded.payload_json,fingerprint=excluded.fingerprint,occurred_at=excluded.occurred_at,source=excluded.source,updated_at=excluded.updated_at",
                               (record.record_id, record.version, record.state, payload, record.fingerprint,
                                record.occurred_at, record.source, utc_now()))
            connection.execute("INSERT INTO record_versions(record_id,version,state,payload_json,fingerprint,stored_at) VALUES(?,?,?,?,?,?)",
                               (record.record_id, record.version, record.state, payload, record.fingerprint, utc_now()))
            self.append_event(connection, "record.saved", record.record_id, record.version,
                              {"state": record.state, "fingerprint": record.fingerprint})
            return record.fingerprint

    def get_record(self, record_id: str) -> DomainRecord | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM records WHERE record_id=?", (record_id,)).fetchone()
        if not row:
            return None
        return DomainRecord(record_id=row["record_id"], payload=json.loads(row["payload_json"]),
                            state=row["state"], version=row["version"], occurred_at=row["occurred_at"],
                            source=row["source"])

    def list_records(self, state: str | None = None) -> list[DomainRecord]:
        query = "SELECT * FROM records"
        params: tuple[Any, ...] = ()
        if state:
            query += " WHERE state=?"
            params = (state,)
        query += " ORDER BY record_id"
        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [DomainRecord(record_id=row["record_id"], payload=json.loads(row["payload_json"]),
                             state=row["state"], version=row["version"], occurred_at=row["occurred_at"],
                             source=row["source"]) for row in rows]

    def save_decision(self, decision: Decision) -> str:
        decision_id = decision.fingerprint
        with self.transaction() as connection:
            if not connection.execute("SELECT 1 FROM records WHERE record_id=?", (decision.record_id,)).fetchone():
                raise ContractError("decision record does not exist")
            body = canonical_json(decision.as_dict())
            connection.execute("INSERT OR IGNORE INTO decisions(decision_id,record_id,outcome,score,decision_json,decided_at) VALUES(?,?,?,?,?,?)",
                               (decision_id, decision.record_id, decision.outcome, decision.score, body, decision.decided_at))
            self.append_event(connection, "decision.saved", decision.record_id,
                              self.event_count(decision.record_id, connection) + 1,
                              {"decision_id": decision_id, "outcome": decision.outcome, "score": decision.score})
        return decision_id

    def event_count(self, aggregate_id: str, connection: sqlite3.Connection | None = None) -> int:
        owns = connection is None
        connection = connection or self.connect()
        try:
            row = connection.execute("SELECT COUNT(*) FROM events WHERE aggregate_id=?", (aggregate_id,)).fetchone()
            return int(row[0])
        finally:
            if owns:
                connection.close()

    def begin_run(self, fixture_hash: str, record_count: int) -> str:
        run_id = stable_hash({"fixture_hash": fixture_hash, "record_count": record_count})[:24]
        with self.transaction() as connection:
            row = connection.execute("SELECT fixture_hash,record_count FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row and (row[0] != fixture_hash or row[1] != record_count):
                raise ContractError("run identifier collision")
            connection.execute("INSERT OR IGNORE INTO runs(run_id,fixture_hash,status,record_count,result_json,started_at) VALUES(?,?,?,?,?,?)",
                               (run_id, fixture_hash, "running", record_count, "{}", utc_now()))
        return run_id

    def completed_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT status,result_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not row or row["status"] != "finished":
            return None
        result = json.loads(row["result_json"])
        if not isinstance(result, dict):
            raise ContractError("stored run result is invalid")
        return result

    def finish_run(self, run_id: str, result: Mapping[str, Any]) -> None:
        with self.transaction() as connection:
            changed = connection.execute("UPDATE runs SET status='finished',result_json=?,finished_at=? WHERE run_id=?",
                                         (canonical_json(result), utc_now(), run_id)).rowcount
            if changed != 1:
                raise ContractError("unknown run")
            self.append_event(connection, "run.finished", run_id, 1, dict(result))

    def verify_chain(self) -> list[str]:
        errors: list[str] = []
        previous = "0" * 64
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM events ORDER BY event_id").fetchall()
        for row in rows:
            payload = json.loads(row["payload_json"])
            expected = stable_hash({"event_type": row["event_type"], "aggregate_id": row["aggregate_id"],
                                    "aggregate_version": row["aggregate_version"], "payload": payload,
                                    "previous_hash": row["previous_hash"], "created_at": row["created_at"]})
            if row["previous_hash"] != previous:
                errors.append(f"event {row['event_id']} previous hash mismatch")
            if row["event_hash"] != expected:
                errors.append(f"event {row['event_id']} content hash mismatch")
            previous = row["event_hash"]
        return errors

    def snapshot(self) -> dict[str, Any]:
        with self.connect() as connection:
            counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                      for table in ("records", "record_versions", "decisions", "events", "runs", "certificates")}
            states = {row[0]: row[1] for row in connection.execute("SELECT state,COUNT(*) FROM records GROUP BY state")}
        return {"counts": counts, "states": states, "chain_errors": self.verify_chain()}

    def decision_rows(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT decision_json FROM decisions ORDER BY record_id,decided_at").fetchall()
        return [json.loads(row[0]) for row in rows]

    def latest_certificate(self, record_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM certificates WHERE record_id=? AND status='verified' "
                "ORDER BY issued_at DESC, certificate_id DESC LIMIT 1",
                (record_id,),
            ).fetchone()
        return _certificate_row(row) if row else None

    def certificate_history(self, record_id: str | None = None) -> list[dict[str, Any]]:
        with self.connect() as connection:
            if record_id is None:
                rows = connection.execute("SELECT * FROM certificates ORDER BY record_id, issued_at, certificate_id").fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM certificates WHERE record_id=? ORDER BY issued_at, certificate_id", (record_id,)
                ).fetchall()
        return [_certificate_row(row) for row in rows]

    def certified_record_ids(self) -> set[str]:
        with self.connect() as connection:
            rows = connection.execute("SELECT DISTINCT record_id FROM certificates WHERE status='verified'").fetchall()
        return {row[0] for row in rows}

    def publish_certificate(self, certificate: Any, *, allow_supersession: bool = True,
                            review: Any | None = None) -> dict[str, Any]:
        """Persist a recognition certificate without letting verified conclusions drift.

        * Re-publishing the identical certificate is idempotent.
        * A previously verified certificate is never mutated or deleted; it is
          marked ``superseded`` and a new certificate is appended.
        * A new certificate can only supersede when its baseline, mapping,
          policy or evidence fingerprint actually changed.  Otherwise the
          differing conclusion is a silent drift and is rejected.
        * A record that already holds a verified certificate cannot be
          re-evaluated under the same review fingerprint at all.

        The baseline, mapping, policy and per-metric evidence referenced by the
        certificate are archived alongside it, so the certificate remains
        reproducible after later mapping or benchmark revisions.
        """
        errors = certificate.integrity_errors()
        if errors:
            raise ContractError("; ".join(errors))
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM certificates WHERE certificate_id=?", (certificate.certificate_id,)
            ).fetchone()
            if existing:
                if existing["status"] != "verified":
                    raise ContractError("a superseded certificate cannot be republished as verified")
                if existing["body_json"] != canonical_json(dict(certificate.body)):
                    raise ContractError("certificate identifier collision with different content")
                return _certificate_row(existing)
            self._archive_certificate(connection, certificate, review)
            previous_row = connection.execute(
                "SELECT * FROM certificates WHERE record_id=? AND status='verified' "
                "ORDER BY issued_at DESC, certificate_id DESC LIMIT 1",
                (certificate.record_id,),
            ).fetchone()
            if previous_row is not None:
                from benchmark_federation.certificates.certificate import ensure_no_silent_drift
                previous = _certificate_row(previous_row)
                ensure_no_silent_drift(previous, certificate)
                if not allow_supersession:
                    raise ContractError("supersession is not allowed for this review")
                connection.execute(
                    "UPDATE certificates SET status='superseded', superseded_by=?, updated_at=? WHERE certificate_id=?",
                    (certificate.certificate_id, utc_now(), previous["certificate_id"]),
                )
                self.append_event(connection, "certificate.superseded", certificate.record_id,
                                  self.event_count(certificate.record_id, connection) + 1,
                                  {"superseded": previous["certificate_id"],
                                   "superseded_by": certificate.certificate_id,
                                   "reason": _supersession_reason(previous, certificate)})
            connection.execute(
                "INSERT INTO certificates(certificate_id,record_id,baseline_family,baseline_version,baseline_digest,"
                "mapping_id,mapping_version,mapping_digest,policy_digest,evidence_digest,review_digest,conclusion,"
                "status,supersedes_json,superseded_by,body_json,issued_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (certificate.certificate_id, certificate.record_id, certificate.baseline_family,
                 certificate.baseline_version, certificate.baseline_digest, certificate.mapping_id,
                 int(certificate.mapping_version) if certificate.mapping_version is not None else None,
                 certificate.mapping_digest, certificate.policy_digest,
                 certificate.evidence_digest, certificate.review_digest, certificate.conclusion, "verified",
                 canonical_json([previous_row["certificate_id"]] if previous_row is not None else []),
                 None, canonical_json(dict(certificate.body)), certificate.issued_at, utc_now()),
            )
            self.append_event(connection, "certificate.published", certificate.record_id,
                              self.event_count(certificate.record_id, connection) + 1,
                              {"certificate_id": certificate.certificate_id, "conclusion": certificate.conclusion,
                               "baseline_digest": certificate.baseline_digest,
                               "mapping_digest": certificate.mapping_digest,
                               "evidence_digest": certificate.evidence_digest})
            row = connection.execute("SELECT * FROM certificates WHERE certificate_id=?",
                                     (certificate.certificate_id,)).fetchone()
        return _certificate_row(row)

    def _archive_certificate(self, connection: sqlite3.Connection, certificate: Any, review: Any | None) -> None:
        """Freeze the review surface a certificate points at.

        Snapshots are content-addressed and insert-or-ignore, so a later
        mapping or benchmark revision cannot rewrite what an existing
        certificate meant.
        """
        body = dict(certificate.body)
        baseline_body = review.baseline.as_dict() if review is not None else body.get("baseline", {})
        policy_body = review.policy.as_dict() if review is not None else body.get("policy", {})
        connection.execute(
            "INSERT OR IGNORE INTO baseline_snapshots(baseline_digest,benchmark_family,benchmark_version,body_json,stored_at) "
            "VALUES(?,?,?,?,?)",
            (certificate.baseline_digest, certificate.baseline_family, certificate.baseline_version,
             canonical_json(baseline_body), utc_now()),
        )
        if certificate.mapping_digest:
            mapping_body = {}
            if review is not None:
                for item in review.mappings:
                    if item.digest == certificate.mapping_digest:
                        mapping_body = item.as_dict()
                        break
            connection.execute(
                "INSERT OR IGNORE INTO mapping_snapshots(mapping_digest,mapping_id,mapping_version,language_pack,body_json,stored_at) "
                "VALUES(?,?,?,?,?,?)",
                (certificate.mapping_digest, certificate.mapping_id, certificate.mapping_version or 0,
                 body.get("mapping", {}).get("language_pack"), canonical_json(mapping_body), utc_now()),
            )
        connection.execute(
            "INSERT OR IGNORE INTO review_snapshots(review_digest,baseline_digest,policy_digest,body_json,stored_at) "
            "VALUES(?,?,?,?,?)",
            (certificate.review_digest, certificate.baseline_digest, certificate.policy_digest,
             canonical_json({"policy": policy_body, "metrics": body.get("metrics", []),
                             "denominator": body.get("denominator", {})}), utc_now()),
        )
        if review is not None:
            observations = {item.metric_code: item for item in review.for_record(certificate.record_id)}
        else:
            observations = {}
        for metric in body.get("metrics", []):
            digest = metric.get("evidence_digest")
            if not digest:
                continue
            observation = observations.get(metric.get("metric_code"))
            payload = {
                "metric_code": metric.get("metric_code"),
                "status": metric.get("status"),
                "reason": metric.get("reason"),
                "raw_value": metric.get("raw_value"),
                "source_scale": metric.get("source_scale"),
                "normalized_value": metric.get("normalized_value"),
                "evidence_ref": metric.get("evidence_ref"),
                "observation": observation.as_dict() if observation is not None else None,
            }
            connection.execute(
                "INSERT OR IGNORE INTO evidence_ledger(evidence_digest,record_id,metric_code,evidence_ref,body_json,stored_at) "
                "VALUES(?,?,?,?,?,?)",
                (digest, certificate.record_id, metric.get("metric_code") or "",
                 metric.get("evidence_ref") or "", canonical_json(payload), utc_now()),
            )

    def evidence_for(self, record_id: str, evidence_digest: str | None = None) -> list[dict[str, Any]]:
        with self.connect() as connection:
            if evidence_digest is None:
                rows = connection.execute(
                    "SELECT * FROM evidence_ledger WHERE record_id=? ORDER BY metric_code", (record_id,)
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM evidence_ledger WHERE record_id=? AND evidence_digest=? ORDER BY metric_code",
                    (record_id, evidence_digest),
                ).fetchall()
        return [{"evidence_digest": row["evidence_digest"], "record_id": row["record_id"],
                 "metric_code": row["metric_code"], "evidence_ref": row["evidence_ref"],
                 "body": json.loads(row["body_json"])} for row in rows]

    def mapping_snapshot(self, mapping_digest: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM mapping_snapshots WHERE mapping_digest=?",
                                     (mapping_digest,)).fetchone()
        return None if row is None else {"mapping_digest": row["mapping_digest"], "mapping_id": row["mapping_id"],
                                         "mapping_version": row["mapping_version"],
                                         "language_pack": row["language_pack"],
                                         "body": json.loads(row["body_json"])}

    def baseline_snapshot(self, baseline_digest: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM baseline_snapshots WHERE baseline_digest=?",
                                     (baseline_digest,)).fetchone()
        return None if row is None else {"baseline_digest": row["baseline_digest"],
                                         "benchmark_family": row["benchmark_family"],
                                         "benchmark_version": row["benchmark_version"],
                                         "body": json.loads(row["body_json"])}

    def certificate_rows(self) -> list[dict[str, Any]]:
        return self.certificate_history()

    def verify_certificates(self) -> list[str]:
        errors: list[str] = []
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM certificates ORDER BY record_id, issued_at, certificate_id").fetchall()
        verified_by_record: dict[str, int] = {}
        for row in rows:
            body = json.loads(row["body_json"])
            if stable_hash(body) != row["certificate_id"]:
                errors.append(f"certificate {row['certificate_id']} content hash mismatch")
            if body.get("baseline", {}).get("digest") != row["baseline_digest"]:
                errors.append(f"certificate {row['certificate_id']} baseline reference mismatch")
            if body.get("mapping", {}).get("digest") != row["mapping_digest"]:
                errors.append(f"certificate {row['certificate_id']} mapping reference mismatch")
            if body.get("conclusion") != row["conclusion"]:
                errors.append(f"certificate {row['certificate_id']} conclusion mismatch")
            if row["baseline_digest"] and not self._has_baseline_snapshot(row["baseline_digest"]):
                errors.append(f"certificate {row['certificate_id']} baseline snapshot is missing")
            if row["mapping_digest"] and not self._has_mapping_snapshot(row["mapping_digest"]):
                errors.append(f"certificate {row['certificate_id']} mapping snapshot is missing")
            if not self._has_review_snapshot(row["review_digest"]):
                errors.append(f"certificate {row['certificate_id']} review snapshot is missing")
            for metric in body.get("metrics", []):
                digest = metric.get("evidence_digest")
                if digest and not self._has_evidence(row["record_id"], digest):
                    errors.append(f"certificate {row['certificate_id']} evidence {digest} is missing")
            if row["status"] == "verified":
                verified_by_record[row["record_id"]] = verified_by_record.get(row["record_id"], 0) + 1
            elif row["status"] == "superseded" and not row["superseded_by"]:
                errors.append(f"certificate {row['certificate_id']} is superseded without a successor")
        for record_id, count in verified_by_record.items():
            if count > 1:
                errors.append(f"record {record_id} has {count} verified certificates")
        return errors

    def _has_baseline_snapshot(self, digest: str) -> bool:
        with self.connect() as connection:
            return connection.execute("SELECT 1 FROM baseline_snapshots WHERE baseline_digest=?",
                                      (digest,)).fetchone() is not None

    def _has_mapping_snapshot(self, digest: str) -> bool:
        with self.connect() as connection:
            return connection.execute("SELECT 1 FROM mapping_snapshots WHERE mapping_digest=?",
                                      (digest,)).fetchone() is not None

    def _has_review_snapshot(self, digest: str) -> bool:
        with self.connect() as connection:
            return connection.execute("SELECT 1 FROM review_snapshots WHERE review_digest=?",
                                      (digest,)).fetchone() is not None

    def _has_evidence(self, record_id: str, digest: str) -> bool:
        with self.connect() as connection:
            return connection.execute(
                "SELECT 1 FROM evidence_ledger WHERE record_id=? AND evidence_digest=?", (record_id, digest)
            ).fetchone() is not None

    def event_rows(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM events ORDER BY event_id").fetchall()
        return [dict(row) | {"payload": json.loads(row["payload_json"])} for row in rows]


def _certificate_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "certificate_id": row["certificate_id"],
        "record_id": row["record_id"],
        "baseline_family": row["baseline_family"],
        "baseline_version": row["baseline_version"],
        "baseline_digest": row["baseline_digest"],
        "mapping_id": row["mapping_id"],
        "mapping_version": row["mapping_version"],
        "mapping_digest": row["mapping_digest"],
        "policy_digest": row["policy_digest"],
        "evidence_digest": row["evidence_digest"],
        "review_digest": row["review_digest"],
        "conclusion": row["conclusion"],
        "status": row["status"],
        "supersedes": json.loads(row["supersedes_json"] or "[]"),
        "superseded_by": row["superseded_by"],
        "issued_at": row["issued_at"],
        "updated_at": row["updated_at"],
        "body": json.loads(row["body_json"]),
    }


def _supersession_reason(previous: Mapping[str, Any], replacement: Any) -> str:
    from benchmark_federation.certificates.certificate import supersession_reason
    return supersession_reason(previous, replacement)

