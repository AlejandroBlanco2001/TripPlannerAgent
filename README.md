# GCP Agent

A multi-agent travel assistant built with [Google ADK](https://google.github.io/adk-docs/) and Gemini 2.5 Flash. It searches real flights via Google Flights, resolves airport IATA codes, and generates trip itineraries — all through a conversational interface.

## Architecture

```
root_agent
└── planning_agent
    ├── FlightPlannerandApprovalAgent (SequentialAgent)
    │   ├── flight_planner_agent     — searches flights + resolves IATA codes
    │   └── request_flight_approval_agent — presents options & captures user selection
    └── itenary_agent                — builds itinerary using Google Search
```

Sessions are persisted in PostgreSQL. Traces are collected by [Arize Phoenix](https://phoenix.arize.com/).

## Stack

- **[Google ADK](https://google.github.io/adk-docs/)** — agent framework
- **[fast-flights](https://github.com/AWeirdDev/flights)** — Google Flights scraper
- **FastAPI + Uvicorn** — HTTP server
- **PostgreSQL** — session persistence
- **Arize Phoenix** — observability / tracing
- **Docker Compose** — local orchestration

## Setup

### 1. Copy env file

```bash
cp .env.example .env
```

Set `GOOGLE_API_KEY` (or configure Vertex AI). Adjust other values as needed.

### 2. Run with Docker

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Agent API | http://localhost:8000 |
| Phoenix UI | http://localhost:6006 |

### 3. Run locally (without Docker)

```bash
# requires uv
uv sync
uv run main.py
```

You'll need a running PostgreSQL instance and to set `SESSION_SERVICE_URI` accordingly.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Gemini API key |
| `GOOGLE_GENAI_USE_VERTEXAI` | `1` to use Vertex AI instead of API key |
| `SESSION_SERVICE_URI` | PostgreSQL URI for session storage |
| `PHOENIX_COLLECTOR_ENDPOINT` | OTLP endpoint for Phoenix tracing |
| `AIRPORTS_SQLITE_PATH` | Path to the bundled `airports.sqlite` |
| `PORT` | Server port (default `8000`) |
| `WEB_ALLOWED` | Enable ADK web UI |
