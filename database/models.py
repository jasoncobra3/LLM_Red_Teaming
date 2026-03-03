"""
SQLAlchemy ORM models for persisting scan configurations, results, and history.
"""

from __future__ import annotations

import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config.settings import settings

Base = declarative_base()


class ScanRun(Base):
    """A single red-teaming scan execution."""

    __tablename__ = "scan_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    status = Column(String(32), default="pending")  # pending | running | completed | failed
    scan_type = Column(String(32), default="deepteam")  # deepteam | custom_multi_turn | custom_static
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Model configuration
    attacker_provider = Column(String(64), nullable=False)
    attacker_model = Column(String(128), nullable=False)
    target_provider = Column(String(64), nullable=False)
    target_model = Column(String(128), nullable=False)
    target_purpose = Column(Text, default="")

    # Scan configuration (stored as JSON)
    vulnerabilities = Column(JSON, default=list)
    attacks = Column(JSON, default=list)
    framework = Column(String(64), nullable=True)
    attacks_per_vuln = Column(Integer, default=5)

    # Custom attack config (for custom_multi_turn / custom_static)
    strategy_id = Column(String(64), nullable=True)
    topic = Column(Text, nullable=True)
    max_turns = Column(Integer, nullable=True)
    conversation_data = Column(JSON, nullable=True)  # Full conversation state JSON

    # Summary metrics
    total_tests = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    overall_score = Column(Float, default=0.0)

    # Relations
    results = relationship("ScanResult", back_populates="scan_run", cascade="all, delete-orphan")


class ScanResult(Base):
    """Individual attack result within a scan."""

    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_run_id = Column(Integer, ForeignKey("scan_runs.id"), nullable=False)

    vulnerability_type = Column(String(128))
    attack_type = Column(String(128))
    risk_category = Column(String(64), nullable=True)

    input_prompt = Column(Text, default="")
    target_response = Column(Text, default="")
    score = Column(Float, default=0.0)
    passed = Column(Boolean, default=True)
    reason = Column(Text, default="")
    extra_data = Column("extra_data", JSON, default=dict)

    scan_run = relationship("ScanRun", back_populates="results")


class APIKeyStore(Base):
    """
    Optional: store provider API keys in the DB (encrypted at rest in prod).
    For this MVP we store them in plain text – encrypt in production.
    """

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String(64), unique=True, nullable=False)
    api_key = Column(Text, nullable=False)
    extra_config = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)
