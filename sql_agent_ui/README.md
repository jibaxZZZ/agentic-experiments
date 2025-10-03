# SQL Agent UI

Interface Next.js pour interroger le backend `sql-agent-api` et visualiser les résultats de
l'agent LLM.

## Stack

- Next.js 14 (App Router) + React 18
- Tailwind CSS pour le styling
- TanStack Query pour la gestion des requêtes

## Démarrage

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

Par défaut, l'UI appelle `http://localhost:9000` (`NEXT_PUBLIC_API_BASE_URL`).

## Fonctionnalités

- Formulaire de question en langage naturel
- Historique des requêtes persisté via le backend
- Affichage des résultats avec statut et latence
- Rafraîchissement automatique de l'historique

## Prochaines étapes

- Ajouter l'authentification utilisateur
- Charts et visualisations avancées à partir des résultats SQL
- Gestion temps-réel via SSE / Websocket pour le streaming de réponses
