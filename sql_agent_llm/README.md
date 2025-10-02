# SQL Agent LLM

Agent LLM orchestré avec LangGraph, connecté au serveur MCP `mcp-server-sql` pour exécuter
et sécuriser des requêtes SQL en langage naturel.

## Pré-requis

- Python 3.10+
- `uv`
- Serveur MCP `mcp-server-sql` démarré en mode SSE (`uv run python -m mcp_server_sql.cli --transport sse --host 0.0.0.0 --port 8080`).

## Installation

```bash
uv venv .venv
. .venv/bin/activate
uv sync
cp .env.example .env
# Renseigner OPENAI_API_KEY, OPENAI_MODEL (ex: gpt-5-nano ou gpt-4o-mini), MCP_SERVER_URL...
```

## Utilisation

Démarrer l'agent depuis la CLI :

```bash
uv run python -m sql_agent_llm.cli query "Donne-moi le nombre de techniciens créés cette semaine"
```

Le run :
- Initialise le logging structuré et les métriques Prometheus (`http://127.0.0.1:9001/metrics`)
- Ouvre une session MCP via SSE et expose les outils (`list_tables`, `describe_table`, `run_sql_query`, ...)
- Utilise LangGraph + GPT pour choisir la bonne séquence de tools, générer la requête SQL puis synthétiser la réponse.

## Observabilité

- Logging JSON avec Structlog
- Compteurs/Histogrammes Prometheus sur les exécutions agent et les appels tools
- Support LangSmith via variables d’environnement (`LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`) pour tracer les runs

## Prochaines étapes

- Ajouter des tests d’intégration avec une base factice
- Câbler l’UI front-end qui consommera cette CLI / future API
- Étendre les prompts pour gérer des accès multi-tenants et des politiques d’accès
