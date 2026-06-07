# DMML — Dungeon Master Machine Language

An AI-powered assistant for Dungeon Masters running tabletop RPG campaigns.

---

## Project Description

DMML leverages **LangChain RAG** (Retrieval-Augmented Generation) to help Dungeon Masters manage game sessions in real time. The assistant generates narrative suggestions, NPC dialogue, enemy encounters, and loot — all grounded in your campaign's history.

**Frontend:** A Flask web interface lets DMs manage NPCs, create player character sheets, and chat with NPCs powered by an LLM.

**Database:** Stores player profiles, campaign logs, and per-NPC structured chat history.

**AI Backend (swappable):**
| Provider | Use Case | Requirement |
|---|---|---|
| `openai` (default) | Cloud-hosted, best quality | `OPENAI_API_KEY` |
| `ollama` | Fully offline / laptop | Ollama running locally |

---

## Setup

### Option A — Local Development (SQLite + Ollama or OpenAI)

**1. Create and activate the virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**
```bash
cp .env.example .env
# Edit .env and set AI_PROVIDER and the relevant API key
```

**4. Initialise the database**
```bash
flask db upgrade
```

**5. Run the app**
```bash
python run.py
# → http://127.0.0.1:5000/
```

---

### Option B — Docker (PostgreSQL + full stack demo)

```bash
docker-compose up --build
# → http://127.0.0.1:5000/
```

> **Laptop users:** Leave `DATABASE_URL` unset in your `.env` and skip the `db` service.
> The app will fall back to SQLite automatically.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `openai` | `openai` or `ollama` |
| `OPENAI_API_KEY` | — | Required when `AI_PROVIDER=openai` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `llama3` | Model to use with Ollama |
| `DATABASE_URL` | `sqlite:///data.db` | SQLAlchemy connection string |
| `SECRET_KEY` | `change-me-in-production` | Flask session secret |
| `FLASK_DEBUG` | `0` | Set to `1` to enable debug routes |

---

## API Reference

### NPCs — `/npc`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/npc` | List all NPCs |
| `POST` | `/npc` | Create an NPC (requires `name`, `role`) |
| `POST` | `/npc/generate` | Generate a random NPC from curated pools |
| `GET` | `/npc/<id>` | Get a single NPC with full chat history |
| `PUT` | `/npc/<id>` | Update an NPC |
| `DELETE` | `/npc/<id>` | Delete an NPC and its chat history |
| `POST` | `/npc/<id>/chat` | Send a player message; receive AI NPC response |
| `GET` | `/npc/<id>/chat` | Retrieve full chat history |
| `POST` | `/npc/<id>/generate_quest` | Generate an AI quest (requires `location`) |
| `POST` | `/npc/<id>/generate_loot` | Generate AI loot (optional `quest_name`) |

### Player Profiles — `/player_profiles`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/player_profiles` | List all player profiles |
| `POST` | `/player_profiles` | Create a player profile (requires `name`, `species`, `character_class`) |
| `GET` | `/player_profiles/<id>` | Get a single profile |
| `PUT` | `/player_profiles/<id>` | Update a profile |
| `DELETE` | `/player_profiles/<id>` | Delete a profile |

### Campaign Logs — `/campaigns`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/campaigns` | List all campaign logs |
| `GET` | `/campaigns/<id>` | Get a single log |

### Debug (dev only, requires `FLASK_DEBUG=1`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/debug/campaign_logs` | Inspect campaign logs |
| `POST` | `/debug/seed_campaign_logs` | Seed example logs (idempotent) |

---

## Folder Structure

```
/DMML
│
├── app/                          # Flask application package
│   ├── __init__.py               # App factory (create_app)
│   ├── routes/                   # Route blueprints (one file per domain)
│   │   ├── __init__.py
│   │   ├── npc.py                # NPC CRUD + AI chat/quest/loot
│   │   ├── player.py             # Player profile CRUD
│   │   ├── campaign.py           # Campaign log read routes
│   │   └── debug.py              # Dev-only seed & inspect routes
│   ├── models/                   # SQLAlchemy models + AI layer
│   │   ├── npc.py                # NPC model (with curated random generation)
│   │   ├── player_profile.py     # Player character sheet model
│   │   ├── campaign.py           # Campaign log model
│   │   ├── chat_message.py       # Structured NPC chat history
│   │   ├── ai.py                 # Public AI facade
│   │   └── ai_providers/         # Swappable LLM backends
│   │       ├── __init__.py       # Provider registry (reads AI_PROVIDER)
│   │       ├── base.py           # Abstract AIProvider interface
│   │       ├── openai_provider.py# LangChain + FAISS + OpenAI (cached)
│   │       └── ollama_provider.py# Local Ollama (lightweight, no FAISS)
│   ├── templates/
│   │   └── index.html            # Main web interface
│   └── static/
│       └── style.css             # App styles
│
├── migrations/                   # Flask-Migrate / Alembic migrations
├── .env.example                  # Example environment variable file
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py                        # Entrypoint: calls create_app()
```

---

## Future Goals

1. **Campaign management UI** — Let DMs create and edit campaign logs directly in the browser.
2. **Per-NPC vector memory** — Store NPC-specific embeddings so each NPC truly "remembers" past interactions across sessions.
3. **Streaming responses** — Stream AI dialogue token-by-token for a more immersive feel.
4. **Local model swap** — Support additional Ollama models (Mistral, Phi-3, etc.) via the `OLLAMA_MODEL` env var.
5. **PDF character sheet export** — Auto-fill a WotC 5e character sheet PDF from a saved `PlayerProfile`.
6. **D&D 5e SRD data ingestion** — Ingest official SRD PDFs so the RAG layer can answer rules questions in-context.