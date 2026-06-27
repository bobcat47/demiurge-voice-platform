"""
Demiurge Voice Platform — SQLAlchemy Models

All tables use UUID primary keys (PostgreSQL native).
Compatible with Supabase / Neon / Railway Postgres.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone

from app.database import Base, TimestampMixin


def utc_now():
    return datetime.now(timezone.utc)


# ═══════════════════════════════════════════════════════════════════
# AGENT
# ═══════════════════════════════════════════════════════════════════
class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Product / Squad taxonomy for the Demiurge ecosystem
    product_key = Column(String(100), nullable=True, index=True)
    squad_key = Column(String(100), nullable=True, index=True)

    # Core prompt
    system_prompt = Column(Text, nullable=False, default="You are a helpful voice assistant.")

    # Voice configuration
    voice_provider = Column(String(50), default="kokoro")
    voice_id = Column(String(100), default="af_bella")
    language = Column(String(10), default="en")

    # Pipeline providers
    stt_provider = Column(String(50), default="whisper")
    tts_provider = Column(String(50), default="kokoro")
    llm_provider = Column(String(50), default="openrouter")
    llm_model = Column(String(100), default="google/gemini-2.0-flash-001")

    # Capabilities
    tools_enabled = Column(JSONB, default=list)  # list of enabled tool names
    memory_enabled = Column(Boolean, default=True)

    # Status
    active = Column(Boolean, default=True, index=True)
    metadata = Column(JSONB, default=dict)

    # Relationships (not enforced at DB level for flexibility)
    # calls -> back_populated in Call model


# ═══════════════════════════════════════════════════════════════════
# CALL
# ═══════════════════════════════════════════════════════════════════
class Call(Base, TimestampMixin):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)

    direction = Column(String(20), default="inbound")  # inbound | outbound | test
    phone_number = Column(String(30), nullable=True)
    status = Column(String(30), default="queued")  # queued | ringing | in_progress | completed | failed | cancelled

    # Content
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    recording_url = Column(String(500), nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Metadata
    metadata = Column(JSONB, default=dict)
    tags = Column(ARRAY(String), default=list)


# ═══════════════════════════════════════════════════════════════════
# VOICE PRESET
# ═══════════════════════════════════════════════════════════════════
class Voice(Base, TimestampMixin):
    __tablename__ = "voices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(50), nullable=False)  # kokoro | piper | elevenlabs | cartesia
    provider_voice_id = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    language = Column(String(10), default="en")
    gender = Column(String(20), nullable=True)
    sample_url = Column(String(500), nullable=True)
    enabled = Column(Boolean, default=True)
    metadata = Column(JSONB, default=dict)


# ═══════════════════════════════════════════════════════════════════
# TOOL
# ═══════════════════════════════════════════════════════════════════
class Tool(Base, TimestampMixin):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    endpoint_url = Column(String(500), nullable=True)
    method = Column(String(10), default="POST")
    auth_type = Column(String(30), default="none")  # none | bearer | api_key | demiurge
    input_schema = Column(JSONB, default=dict)
    output_schema = Column(JSONB, default=dict)
    enabled = Column(Boolean, default=True)
    metadata = Column(JSONB, default=dict)


# ═══════════════════════════════════════════════════════════════════
# CAMPAIGN
# ═══════════════════════════════════════════════════════════════════
class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)

    target_source = Column(String(50), default="manual")  # manual | csv | api | lead_intel
    status = Column(String(30), default="draft")  # draft | scheduled | running | paused | completed
    schedule = Column(JSONB, default=dict)  # {cron: "0 9 * * *", timezone: "America/New_York"}
    metadata = Column(JSONB, default=dict)


# ═══════════════════════════════════════════════════════════════════
# MEMORY (per-agent conversation memory)
# ═══════════════════════════════════════════════════════════════════
class Memory(Base, TimestampMixin):
    __tablename__ = "memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="SET NULL"), nullable=True)

    role = Column(String(20), nullable=False)  # system | user | assistant | tool
    content = Column(Text, nullable=False)
    tool_calls = Column(JSONB, nullable=True)
    tool_results = Column(JSONB, nullable=True)
    embedding = Column(ARRAY(Float), nullable=True)  # for vector search (future)


# ═══════════════════════════════════════════════════════════════════
# ANALYTICS DAILY SUMMARY
# ═══════════════════════════════════════════════════════════════════
class AnalyticsDaily(Base, TimestampMixin):
    __tablename__ = "analytics_daily"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    total_calls = Column(Integer, default=0)
    inbound_calls = Column(Integer, default=0)
    outbound_calls = Column(Integer, default=0)
    avg_duration_seconds = Column(Float, default=0.0)
    total_cost_usd = Column(Float, default=0.0)
    tool_calls_count = Column(Integer, default=0)
    successful_tool_calls = Column(Integer, default=0)
    metadata = Column(JSONB, default=dict)


# ═══════════════════════════════════════════════════════════════════
# PROVIDER HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════
class ProviderHealth(Base, TimestampMixin):
    __tablename__ = "provider_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_type = Column(String(50), nullable=False)  # llm | stt | tts | telephony
    provider_name = Column(String(100), nullable=False)
    status = Column(String(20), default="unknown")  # healthy | degraded | down | unknown
    latency_ms = Column(Integer, nullable=True)
    last_check_at = Column(DateTime(timezone=True), default=utc_now)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSONB, default=dict)
