"""
Database manager – CRUD helpers for scan runs, results, and API keys.
"""

from __future__ import annotations

import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from database.models import SessionLocal, ScanRun, ScanResult, APIKeyStore, init_db


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def get_session() -> Session:
    return SessionLocal()


def setup_database():
    """Idempotent DB bootstrap."""
    init_db()


# ---------------------------------------------------------------------------
# ScanRun CRUD
# ---------------------------------------------------------------------------

def create_scan_run(
    name: str,
    attacker_provider: str,
    attacker_model: str,
    target_provider: str,
    target_model: str,
    target_purpose: str = "",
    vulnerabilities: list | None = None,
    attacks: list | None = None,
    framework: str | None = None,
    attacks_per_vuln: int = 5,
    scan_type: str = "deepteam",
    strategy_id: str | None = None,
    topic: str | None = None,
    max_turns: int | None = None,
) -> ScanRun:
    with get_session() as session:
        run = ScanRun(
            name=name,
            status="pending",
            scan_type=scan_type,
            attacker_provider=attacker_provider,
            attacker_model=attacker_model,
            target_provider=target_provider,
            target_model=target_model,
            target_purpose=target_purpose,
            vulnerabilities=vulnerabilities or [],
            attacks=attacks or [],
            framework=framework,
            attacks_per_vuln=attacks_per_vuln,
            strategy_id=strategy_id,
            topic=topic,
            max_turns=max_turns,
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return run


def update_scan_status(
    scan_id: int,
    status: str,
    total_tests: int = 0,
    passed: int = 0,
    failed: int = 0,
    overall_score: float = 0.0,
):
    with get_session() as session:
        run = session.query(ScanRun).get(scan_id)
        if run:
            run.status = status
            run.total_tests = total_tests
            run.passed = passed
            run.failed = failed
            run.overall_score = overall_score
            if status in ("completed", "failed"):
                run.completed_at = datetime.datetime.utcnow()
            session.commit()


def get_scan_run(scan_id: int) -> Optional[ScanRun]:
    with get_session() as session:
        return session.query(ScanRun).filter(ScanRun.id == scan_id).first()


def update_scan_conversation(scan_id: int, conversation_data: dict):
    """Store the full conversation state JSON on a scan run."""
    with get_session() as session:
        run = session.query(ScanRun).get(scan_id)
        if run:
            run.conversation_data = conversation_data
            session.commit()


def list_scan_runs(limit: int = 50) -> List[ScanRun]:
    with get_session() as session:
        return (
            session.query(ScanRun)
            .order_by(ScanRun.created_at.desc())
            .limit(limit)
            .all()
        )


def delete_scan_run(scan_id: int):
    with get_session() as session:
        run = session.query(ScanRun).get(scan_id)
        if run:
            session.delete(run)
            session.commit()


# ---------------------------------------------------------------------------
# ScanResult CRUD
# ---------------------------------------------------------------------------

def add_scan_results(scan_id: int, results: list[dict]):
    """Bulk-insert result rows for a scan run."""
    with get_session() as session:
        for r in results:
            session.add(
                ScanResult(
                    scan_run_id=scan_id,
                    vulnerability_type=r.get("vulnerability_type", ""),
                    attack_type=r.get("attack_type", ""),
                    risk_category=r.get("risk_category", ""),
                    input_prompt=r.get("input_prompt", ""),
                    target_response=r.get("target_response", ""),
                    score=r.get("score", 0.0),
                    passed=r.get("passed", True),
                    reason=r.get("reason", ""),
                    extra_data=r.get("metadata", {}),
                )
            )
        session.commit()


def get_scan_results(scan_id: int) -> List[ScanResult]:
    with get_session() as session:
        return (
            session.query(ScanResult)
            .filter(ScanResult.scan_run_id == scan_id)
            .all()
        )


# ---------------------------------------------------------------------------
# API Key Store
# ---------------------------------------------------------------------------

def save_api_key(provider_id: str, api_key: str, extra_config: dict | None = None):
    with get_session() as session:
        existing = (
            session.query(APIKeyStore)
            .filter(APIKeyStore.provider_id == provider_id)
            .first()
        )
        if existing:
            existing.api_key = api_key
            existing.extra_config = extra_config or {}
        else:
            session.add(
                APIKeyStore(
                    provider_id=provider_id,
                    api_key=api_key,
                    extra_config=extra_config or {},
                )
            )
        session.commit()


def get_api_key(provider_id: str) -> Optional[APIKeyStore]:
    with get_session() as session:
        return (
            session.query(APIKeyStore)
            .filter(APIKeyStore.provider_id == provider_id)
            .first()
        )


def list_api_keys() -> List[APIKeyStore]:
    with get_session() as session:
        return session.query(APIKeyStore).all()
