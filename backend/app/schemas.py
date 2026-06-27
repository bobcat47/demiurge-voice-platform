"""
Demiurge Voice Platform — Pydantic Schemas

Request/response models for all API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ═══════════════════════════════════════════════════════════════════
# SHARED
# ═══════════════════════════════════════════════════════════════════
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    timestamp: datetime
    services: Dict[str, str] = {}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


# ═══════════════════════════════════════════════════════════════════
# AGENT
# ═══════════════════════════════════════════════════════════════════
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    product_key: Optional[str] = None
    squad_key: Optional[str] = None
    system_prompt: str = "You are a helpful voice assistant."
    voice_provider: str = "kokoro"
    voice_id: str = "af_bella"
    language: str = "en"
    stt_provider: str = "whisper"
    tts_provider: str = "kokoro"
    llm_provider: str = "openrouter"
    llm_model: str = "google/gemini-2.0-flash-001"
    tools_enabled: List[str] = []
    memory_enabled: bool = True
    active: bool = True
    metadata: Dict[str, Any] = {}


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_key: Optional[str] = None
    squad_key: Optional[str] = None
    system_prompt: Optional[str] = None
    voice_provider: Optional[str] = None
    voice_id: Optional[str] = None
    language: Optional[str] = None
    stt_provider: Optional[str] = None
    tts_provider: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    tools_enabled: Optional[List[str]] = None
    memory_enabled: Optional[bool] = None
    active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ═══════════════════════════════════════════════════════════════════
# CALL
# ═══════════════════════════════════════════════════════════════════
class CallBase(BaseModel):
    agent_id: Optional[UUID] = None
    direction: str = "inbound"  # inbound | outbound | test
    phone_number: Optional[str] = None
    status: str = "queued"
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tags: List[str] = []


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    status: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class CallResponse(CallBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ═══════════════════════════════════════════════════════════════════
# VOICE
# ═══════════════════════════════════════════════════════════════════
class VoiceBase(BaseModel):
    provider: str
    provider_voice_id: str
    name: str
    language: str = "en"
    gender: Optional[str] = None
    sample_url: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = {}


class VoiceCreate(VoiceBase):
    pass


class VoiceUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    gender: Optional[str] = None
    sample_url: Optional[str] = None
    enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class VoiceResponse(VoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ═══════════════════════════════════════════════════════════════════
# TOOL
# ═══════════════════════════════════════════════════════════════════
class ToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    endpoint_url: Optional[str] = None
    method: str = "POST"
    auth_type: str = "none"
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    enabled: bool = True
    metadata: Dict[str, Any] = {}


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    description: Optional[str] = None
    endpoint_url: Optional[str] = None
    method: Optional[str] = None
    auth_type: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolResponse(ToolBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ═══════════════════════════════════════════════════════════════════
# CAMPAIGN
# ═══════════════════════════════════════════════════════════════════
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    agent_id: Optional[UUID] = None
    target_source: str = "manual"
    status: str = "draft"
    schedule: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    agent_id: Optional[UUID] = None
    target_source: Optional[str] = None
    status: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CampaignResponse(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ═══════════════════════════════════════════════════════════════════
# MEMORY
# ═══════════════════════════════════════════════════════════════════
class MemoryEntry(BaseModel):
    role: str  # system | user | assistant | tool
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None


class MemoryCreate(MemoryEntry):
    call_id: Optional[UUID] = None


class MemoryResponse(MemoryEntry):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agent_id: UUID
    call_id: Optional[UUID] = None
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════════════
class AnalyticsSummary(BaseModel):
    total_calls: int
    total_agents: int
    avg_duration_seconds: float
    calls_today: int
    calls_this_week: int
    provider_health: Dict[str, str]
    recent_calls: List[CallResponse] = []


# ═══════════════════════════════════════════════════════════════════
# VOICE PIPELINE
# ═══════════════════════════════════════════════════════════════════
class PipelineConfig(BaseModel):
    agent_id: UUID
    phone_number: Optional[str] = None
    direction: str = "inbound"
    metadata: Dict[str, Any] = {}


class PipelineStartResponse(BaseModel):
    call_id: UUID
    status: str
    message: str
    ws_url: Optional[str] = None


class TranscriptSegment(BaseModel):
    speaker: str  # agent | user
    text: str
    timestamp: datetime
    is_final: bool = True


class CallSummaryRequest(BaseModel):
    transcript: str
    agent_id: Optional[UUID] = None


class CallSummaryResponse(BaseModel):
    summary: str
    key_points: List[str] = []
    sentiment: Optional[str] = None
    action_items: List[str] = []
    duration_seconds: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════
# PROVIDER CONFIG
# ═══════════════════════════════════════════════════════════════════
class ProviderConfig(BaseModel):
    provider_type: str  # llm | stt | tts | telephony
    provider_name: str
    config: Dict[str, Any]
    enabled: bool = True


class ProviderHealthResponse(BaseModel):
    provider_type: str
    provider_name: str
    status: str
    latency_ms: Optional[int] = None
    last_check_at: Optional[datetime] = None
    error_message: Optional[str] = None
