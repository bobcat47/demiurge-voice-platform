# Claude Handoff — Demiurge Voice Platform MVP

## What Was Built Tonight

### Foundation (Complete)
- **FastAPI backend** with full API surface for agents, calls, voices, tools, memory, analytics, and campaigns
- **PostgreSQL database layer** with SQLAlchemy 2.0 async ORM — compatible with Supabase, Neon, Railway Postgres
- **Provider abstraction layer** — LLM (OpenRouter, Gemini, Groq, OpenAI), STT (Whisper), TTS (Kokoro, Piper), Telephony (Twilio)
- **Tool registry** with 13 built-in Demiurge tools (ds_event_emit, ds_lead_search, ds_calendar_book, etc.)
- **Voice pipeline service** with session management, agent runtime, transcript store, and call summary generation
- **React admin console** with sidebar navigation, dashboard, agent CRUD, call logs, tool registry, campaigns, and settings
- **Docker + Railway config** for immediate deployment
- **Health check endpoint** at `/health` for Railway/load balancer compatibility

### API Routes Implemented (All Working)
- `GET /health` — Health check
- `GET/POST /api/v1/agents` — Agent CRUD
- `GET/POST /api/v1/calls` — Call management + pipeline start/end/text-turn
- `GET/POST /api/v1/voices` — Voice presets
- `GET/POST /api/v1/tools` + `/builtin` + `/{name}/execute` — Tool registry
- `GET/POST /api/v1/memory/{agent_id}` — Per-agent memory
- `GET /api/v1/analytics/summary` + `/recordings` — Dashboard data
- `GET/POST /api/v1/campaigns` + start/pause actions
- `GET /api/v1/providers` + `/health` — Provider status

### Data Models (All Created)
- `Agent` — Full agent configuration with LLM/STT/TTS/provider settings
- `Call` — Call records with transcripts, summaries, timing
- `Voice` — TTS voice presets
- `Tool` — Custom tool definitions
- `Campaign` — Outbound campaign management
- `Memory` — Per-agent conversation memory
- `AnalyticsDaily` — Daily aggregated metrics
- `ProviderHealth` — Provider health check tracking

### What Is Working
1. **Full API** — All REST endpoints are operational
2. **Agent CRUD** — Create, read, update, deactivate agents
3. **Agent test chat** — Send test messages to agents via text (Agent Detail → Test tab)
4. **Provider abstraction** — LLM providers (OpenRouter, Gemini, Groq, OpenAI) with health checks
5. **Tool registry** — All 13 built-in tools registered with schemas and stub handlers
6. **Tool execution** — Execute tools via API with parameter validation
7. **Call management** — Create, track, summarize calls
8. **Analytics dashboard** — Summary stats, provider health, recent calls
9. **Campaign management** — Create, start, pause campaigns
10. **Admin console** — Full React UI for all features

### What Is Mocked / Stubbed
1. **Real-time audio pipeline** — LiveKit rooms are created but the actual WebRTC audio loop is mocked. The `VoicePipelineService.start_call()` creates sessions but does not yet process real audio frames.
2. **Pipecat pipeline** — The `PipecatAdapter` has session management and event hooks but does not run a real Pipecat pipeline. The `process_frame()` method routes frames correctly but uses placeholder data.
3. **LiveKit audio transport** — The `LiveKitAdapter` creates rooms and tokens but does not yet subscribe to audio tracks or publish audio.
4. **Tool implementations** — All 13 `ds_*` tools have stub handlers that log and return mock data. They do not yet connect to real external services.
5. **Telephony webhooks** — Twilio webhook handling returns TwiML but does not yet bridge to the LiveKit audio stream.
6. **Campaign execution** — Campaigns can be created and status-managed but do not yet auto-dial numbers.

## How to Run Locally

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Set DATABASE_URL and at least one LLM API key in .env
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173, API proxy to :8000
```

## How to Deploy to Railway

1. Push this repo to GitHub
2. In Railway: New Project → Deploy from GitHub Repo
3. Add PostgreSQL service (Railway creates DATABASE_URL automatically)
4. Add environment variables from `.env.example`
5. The `railway.json` and `backend/Dockerfile` handle the rest
6. Health check at `/health` ensures Railway knows the app is up

## Environment Variables Required

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `LLM_PROVIDER` | Yes | `openrouter` / `gemini` / `groq` / `openai` |
| `LLM_MODEL` | Yes | Model identifier |
| `OPENROUTER_API_KEY` | Yes* | If using OpenRouter |
| `GEMINI_API_KEY` | Yes* | If using Gemini |
| `GROQ_API_KEY` | Yes* | If using Groq |
| `OPENAI_API_KEY` | Yes* | If using OpenAI |
| `PORT` | Auto | Railway sets this automatically |

*At least one LLM provider key is required.

## How Claude Should Wire It Tomorrow

### Priority 1: Real-Time Audio Pipeline (Critical)
**Files to modify:**
- `app/providers/livekit/adapter.py` — Wire `subscribe_to_audio()` and `publish_audio()` methods
- `app/providers/pipecat/adapter.py` — Replace mock frame processing with actual Pipecat `PipelineTask`
- `app/services/voice_pipeline.py` — Connect the full loop: telephony → LiveKit → Pipecat → STT → LLM → TTS → audio out

**Approach:**
```python
# In PipecatAdapter.start_pipeline(), replace mock with:
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
# Create Transport → STT → LLM → TTS → Transport pipeline
```

### Priority 2: LiveKit Audio Transport
**Files to modify:**
- `app/providers/livekit/adapter.py`

**Add:**
- `AudioStream` subscription from participant tracks
- `AudioSource` for publishing TTS output
- Event handlers for `track_subscribed`, `track_unsubscribed`

### Priority 3: Tool Implementations
**Files to modify:**
- `app/tools/builtin.py` — Replace stub handlers with real HTTP calls to Demiurge services

**For each tool:**
- Use `DEMIURGE_LEAD_INTEL_URL` and `DEMIURGE_LEAD_INTEL_TOKEN` for lead tools
- Use `DEMIURGE_SECRETS_URL` for secrets access
- Add proper error handling and retry logic

### Priority 4: Campaign Auto-Dialer
**Files to modify:**
- `app/routers/campaigns.py` — Add `/execute` endpoint
- `app/services/campaign_runner.py` — New file

**Create:**
- Cron-like scheduler (use `croniter` or APScheduler)
- Batch dialer that reads targets and initiates calls via telephony provider
- Rate limiting and concurrency control

### Priority 5: WebSocket for Real-Time Console
**Files to create:**
- `app/routers/ws.py` — WebSocket endpoint for live call monitoring
- Frontend updates for real-time call status

### Priority 6: Demiurge Console Integration
- Add OAuth/auth middleware using Demiurge Console tokens
- Add `product_key` filtering scoped to console user
- Event emission to Demiurge event bus

## How to Connect to Demiurge Secrets Service

```python
from app.config import settings
import httpx

async def get_secret(key: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.DEMIURGE_SECRETS_URL}/api/secrets/{key}",
            headers={"Authorization": f"Bearer {settings.DEMIURGE_SECRETS_TOKEN}"}
        )
        return resp.json()["value"]
```

Use this to dynamically resolve API keys instead of storing them in environment variables.

## How to Connect to Demiurge Lead Intelligence

```python
from app.config import settings
import httpx

async def search_leads(query: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.DEMIURGE_LEAD_INTEL_URL}/api/leads/search",
            headers={"Authorization": f"Bearer {settings.DEMIURGE_LEAD_INTEL_TOKEN}"},
            json={"query": query}
        )
        return resp.json()
```

The `ds_lead_search` and `ds_lead_score` tools should use this pattern.

## How to Connect to Main Demiurge Console

The console should:
1. Call this platform's API using `DEMIURGE_CONSOLE_TOKEN` as bearer auth
2. Filter agents by `product_key` and `squad_key`
3. Display call analytics and recordings
4. Trigger campaign creation via `/api/v1/campaigns`

Add auth middleware to validate console tokens:
```python
# In app/core/security.py
async def verify_console_token(token: str = Header(...)):
    # Validate against Demiurge Console
    pass
```

## Remaining TODOs (Ranked by Priority)

### Critical (P0)
- [ ] Wire LiveKit audio subscription/publication
- [ ] Wire Pipecat real-time pipeline (STT → LLM → TTS)
- [ ] Implement actual audio frame processing loop
- [ ] Connect telephony webhooks to pipeline start

### High (P1)
- [ ] Replace tool stub handlers with real Demiurge service calls
- [ ] Implement campaign auto-dialer with scheduling
- [ ] Add WebSocket endpoint for live call monitoring
- [ ] Add authentication/authorization middleware
- [ ] Add rate limiting to API endpoints

### Medium (P2)
- [ ] Vector memory search (pgvector)
- [ ] Call recording storage (S3/R2)
- [ ] Transcript export (CSV, JSON)
- [ ] Agent version history
- [ ] A/B testing for agent prompts

### Low (P3)
- [ ] Multi-language TTS support
- [ ] Custom voice cloning
- [ ] SIP trunk support
- [ ] Call transfer capabilities
- [ ] Post-call survey

## File Map

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings & env vars
│   ├── database.py          # DB connection & session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── core/
│   │   ├── logger.py        # Structured logging
│   │   ├── errors.py        # Exception hierarchy
│   │   └── security.py      # API key auth
│   ├── routers/
│   │   ├── health.py        # Health check
│   │   ├── agents.py        # Agent CRUD
│   │   ├── calls.py         # Call management
│   │   ├── voices.py        # Voice presets
│   │   ├── tools.py         # Tool registry
│   │   ├── memory.py        # Conversation memory
│   │   ├── analytics.py     # Dashboard data
│   │   ├── campaigns.py     # Campaign management
│   │   └── providers.py     # Provider status
│   ├── providers/
│   │   ├── llm/             # LLM abstraction
│   │   │   ├── base.py      # Abstract base
│   │   │   ├── openrouter.py
│   │   │   ├── gemini.py
│   │   │   ├── groq.py
│   │   │   ├── openai_compat.py
│   │   │   └── factory.py
│   │   ├── stt/             # STT abstraction
│   │   │   ├── base.py
│   │   │   ├── whisper.py
│   │   │   └── factory.py
│   │   ├── tts/             # TTS abstraction
│   │   │   ├── base.py
│   │   │   ├── kokoro.py
│   │   │   ├── piper.py
│   │   │   └── factory.py
│   │   ├── telephony/       # Telephony abstraction
│   │   │   ├── base.py
│   │   │   ├── twilio.py
│   │   │   └── factory.py
│   │   ├── livekit/         # LiveKit adapter [MOCKED]
│   │   │   └── adapter.py
│   │   └── pipecat/         # Pipecat adapter [MOCKED]
│   │       └── adapter.py
│   ├── services/
│   │   ├── voice_pipeline.py    # Pipeline orchestrator [MOCKED]
│   │   ├── call_session_manager.py
│   │   ├── agent_runtime.py
│   │   ├── transcript_store.py
│   │   └── call_summary.py
│   └── tools/
│       ├── registry.py      # Tool registry
│       └── builtin.py       # Built-in tool definitions [STUBBED]
├── requirements.txt
└── Dockerfile

frontend/
├── src/
│   ├── App.tsx              # Routes
│   ├── main.tsx             # Entry point
│   ├── components/
│   │   └── Layout.tsx       # Sidebar + top bar
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Agents.tsx
│   │   ├── AgentDetail.tsx
│   │   ├── Calls.tsx
│   │   ├── Tools.tsx
│   │   ├── Voices.tsx
│   │   ├── Campaigns.tsx
│   │   └── Settings.tsx
│   └── hooks/
│       └── useApi.ts        # API client
└── Dockerfile
```

## Next Prompt for Claude

> Continue building the Demiurge Voice Platform. Wire the real-time audio pipeline:
> 1. Connect LiveKit audio transport — subscribe to participant audio tracks and publish TTS audio
> 2. Wire Pipecat PipelineTask with Transport → STT → LLM → TTS → Transport
> 3. Replace tool stub handlers with real HTTP calls to Demiurge Lead Intelligence and Secrets Service
> 4. Add WebSocket endpoint for live call monitoring in the admin console
> 5. Ensure the pipeline works end-to-end: phone call → agent response → audio playback
>
> Use the existing adapter interfaces in `app/providers/` and extend them. Do not break the existing API surface.
