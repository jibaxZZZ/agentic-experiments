# SQL Agent API

Backend FastAPI orchestrant l'agent `sql_agent_llm` et exposant des endpoints REST pour
poser des questions en langage naturel, persister l'historique dans Postgres et suivre
les métriques Prometheus.

## Stack

- FastAPI + Uvicorn (ASGI)
- SQLAlchemy async + asyncpg (persistence Postgres)
- Structlog pour le logging JSON
- Prometheus client pour les métriques
- Intégration directe du package `sql_agent_llm`

## Configuration

Copiez `.env.example` vers `.env` et renseignez les variables :

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sql_agent
OPENAI_API_KEY=...
LANGSMITH_API_KEY=...
MCP_SERVER_URL=http://127.0.0.1:8080
MCP_SSE_PATH=/sse
```

Le fichier `.env` est partagé avec `sql_agent_llm` (variables identiques) et ajoute la
connexion Postgres.

## Installation

```bash
uv venv .venv
. .venv/bin/activate
uv sync
```

## Lancement

```bash
uv run uvicorn sql_agent_api.main:app --reload --host 0.0.0.0 --port 9000
```

Métriques exposées sur `/metrics`. Les endpoints principaux :

- `POST /queries` – lance l'agent sur une question
- `GET /queries/{id}` – récupère une requête persistée
- `GET /queries` – liste paginée des historiques

## Prochaines étapes

- Ajouter un système de tâches asynchrones pour les requêtes longues
- Authentifier les appels (API key / OAuth) selon les besoins
- Étendre le schéma de persistance pour tracker davantage de métadonnées
