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

## Deploying to Cloud Run

### Prerequisites

The scripts `scripts/build-registry.py` and `scripts/deploy.py` interact with several GCP services. The person or service account running them needs the following permissions.

#### Required IAM roles (deploying user)

| Role | Purpose |
|------|---------|
| `roles/artifactregistry.admin` | Create the Artifact Registry repo and push Docker images |
| `roles/run.admin` | Deploy and update Cloud Run services |
| `roles/iam.serviceAccountUser` | Act as the Cloud Run service account during deployment |
| `roles/cloudsql.client` | (if verifying connectivity) Connect to Cloud SQL |

Grant them via the GCP Console under **IAM & Admin → IAM**, or with `gcloud`:

```bash
PROJECT=your-project-id
MEMBER=user:you@example.com   # or serviceAccount:sa@project.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding $PROJECT --member=$MEMBER --role=roles/artifactregistry.admin
gcloud projects add-iam-policy-binding $PROJECT --member=$MEMBER --role=roles/run.admin
gcloud projects add-iam-policy-binding $PROJECT --member=$MEMBER --role=roles/iam.serviceAccountUser
```

#### Required IAM roles (Cloud Run service account)

The identity that the Cloud Run service runs as (by default `<project-number>-compute@developer.gserviceaccount.com`) needs:

| Role | Purpose |
|------|---------|
| `roles/cloudsql.client` | Open the Cloud SQL Auth Proxy socket to `agentdb` |

```bash
SA=<project-number>-compute@developer.gserviceaccount.com

gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SA" --role=roles/cloudsql.client
```

#### Required GCP APIs

The following APIs must be enabled in your project:

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  vpcaccess.googleapis.com
```

#### Cloud SQL — private IP note

`agentdb` uses a **private IP only** (no public IP). The deploy script configures Cloud Run with Direct VPC Egress (`--network=default --subnet=default --vpc-egress=private-ranges-only`) so the service can reach the private IP. If you recreate the Cloud SQL instance, make sure it is attached to the same VPC (`default`) and that private IP is enabled.

### Run the deploy

```bash
# Full build + deploy
python scripts/deploy.py

# Deploy only (skip Docker build)
python scripts/deploy.py --skip-build
```

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
