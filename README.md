# Demiurge Voice Platform

Self-hosted voice AI infrastructure for real-time conversational agents. The voice layer for the Demiurge Systems ecosystem.

## Overview

The Demiurge Voice Platform provides a complete backend for building, deploying, and managing voice AI agents. It is designed as a production-oriented, self-hosted alternative to Vapi with deep integration into the Demiurge ecosystem.

### Key Features

- **Agent Management**: Create and configure voice agents with custom prompts, LLM models, and voice settings
- **Provider Abstraction**: Swap LLM, STT, TTS, and telephony providers without changing code
- **Tool Registry**: Built-in Demiurge tools for CRM, calendar, lead intelligence, and more
- **Voice Pipeline**: Full pipeline from telephony → audio transport → STT → LLM → TTS → audio response
- **Campaign Management**: Outbound call campaigns with scheduling
- **Analytics**: Call metrics, provider health, and usage statistics
- **Admin Console**: React-based operational dashboard

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Demiurge Voice Platform                    │
├─────────────────┬───────────────────────────────────────────────┤
│  React Admin    │  FastAPI Backend                              │
│  Console        │                                               │
│                 │  ┌─────────┐  ┌─────────┐  ┌──────────────┐  │
│  /dashboard     │  │ Agents  │  │  Calls  │  │  Campaigns   │  │
│  /agents        │  └─────────┘  └─────────┘  └──────────────┘  │
│  /calls         │                                               │
│  /tools         │  ┌─────────┐  ┌─────────┐  ┌──────────────┐  │
│  /voices        │  │  Tools  │  │ Voices  │  │  Analytics   │  │
│  /settings      │  └─────────┘  └─────────┘  └──────────────┘  │
│                 │                                               │
├─────────────────┴───────────────────────────────────────────────┤
│                        Provider Abstraction Layer                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │   LLM    │ │   STT    │ │   TTS    │ │    Telephony     │   │
│  │OpenRouter│ │ Whisper  │ │  Kokoro  │ │     Twilio       │   │
│  │  Gemini  │ │          │ │  Piper   │ │                  │   │
│  │   Groq   │ │          │ │          │ │                  │   │
│  │  OpenAI  │ │          │ │          │ │                  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     Voice Pipeline (LiveKit + Pipecat)            │
│  Telephony → LiveKit → Pipecat → STT → LLM → Tools → TTS        │
├─────────────────────────────────────────────────────────────────┤
│                     Demiurge Ecosystem Integration                │
│  Secrets Service │ Lead Intelligence │ Console │ Event Bus        │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or Supabase/Neon)
- Node.js 20+ (for frontend)

### Backend Setup

```bash
# Clone and enter backend
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/agents` | List agents |
| POST | `/api/v1/agents` | Create agent |
| GET | `/api/v1/agents/{id}` | Get agent |
| PUT | `/api/v1/agents/{id}` | Update agent |
| DELETE | `/api/v1/agents/{id}` | Deactivate agent |
| GET | `/api/v1/calls` | List calls |
| POST | `/api/v1/calls` | Create call |
| GET | `/api/v1/calls/{id}` | Get call |
| PUT | `/api/v1/calls/{id}` | Update call |
| POST | `/api/v1/calls/{id}/start` | Start voice pipeline |
| POST | `/api/v1/calls/{id}/end` | End call |
| POST | `/api/v1/calls/{id}/text-turn` | Text-based turn |
| POST | `/api/v1/calls/{id}/summarize` | Summarize call |
| GET | `/api/v1/voices` | List voices |
| POST | `/api/v1/voices` | Create voice |
| GET | `/api/v1/tools` | List tools |
| POST | `/api/v1/tools` | Create tool |
| GET | `/api/v1/tools/builtin` | List built-in tools |
| POST | `/api/v1/tools/{name}/execute` | Execute tool |
| GET | `/api/v1/memory/{agent_id}` | Get agent memory |
| POST | `/api/v1/memory/{agent_id}` | Add memory entry |
| GET | `/api/v1/analytics/summary` | Analytics summary |
| GET | `/api/v1/analytics/recordings` | List recordings |
| GET | `/api/v1/campaigns` | List campaigns |
| POST | `/api/v1/campaigns` | Create campaign |
| GET | `/api/v1/campaigns/{id}` | Get campaign |
| PUT | `/api/v1/campaigns/{id}` | Update campaign |
| POST | `/api/v1/campaigns/{id}/start` | Start campaign |
| POST | `/api/v1/campaigns/{id}/pause` | Pause campaign |
| GET | `/api/v1/providers` | List providers |
| GET | `/api/v1/providers/health` | Provider health |

## Environment Variables

See `.env.example` for a complete list of environment variables.

### Required

- `DATABASE_URL` — PostgreSQL connection string
- At least one LLM API key (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENAI_API_KEY`)

### Optional

- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` — For real-time audio
- `TWILIO_*` — For telephony
- `DEMIURGE_*` — For ecosystem integration

## Deployment

### Railway

1. Connect your GitHub repo to Railway
2. Add a PostgreSQL database service
3. Set environment variables in Railway dashboard
4. Deploy — the `railway.json` and `Dockerfile` are pre-configured

### Manual

```bash
# Production build
cd backend
docker build -t demiurge-voice .
docker run -p 8000:8000 --env-file .env demiurge-voice
```

## License

Private — Demiurge Systems
