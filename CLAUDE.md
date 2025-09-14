# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

**Application Type**: Trading tool avec interface web Next.js et API FastAPI
**Structure**: Monorepo avec deux applications principales :
- `frontend/` : Application Next.js 15 avec TypeScript et Tailwind CSS
- `backend/` : API FastAPI avec SQLAlchemy et PostgreSQL

### Architecture Backend
- **FastAPI** : Framework web moderne pour l'API REST
- **SQLAlchemy** : ORM avec Alembic pour les migrations
- **PostgreSQL** : Base de données relationnelle
- **Structure MVC** : Models, routes, schemas séparés
- **Authentification** : Système d'utilisateurs intégré

### Architecture Frontend
- **Next.js 15** : Framework React avec App Router
- **TypeScript** : Typage strict activé
- **State Management** : Zustand pour l'état global
- **UI Components** : Radix UI avec Tailwind CSS
- **Form Handling** : React Hook Form + Zod validation
- **API Client** : Axios pour les appels HTTP

## Commandes Principales

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Démarrage développement
npm run build        # Build production
npm run lint         # Vérification ESLint
npm run lint:fix     # Correction automatique ESLint
npm run type-check   # Vérification TypeScript
```

### Base de Données
```bash
cd backend
docker-compose up -d postgres  # Démarrer PostgreSQL
alembic upgrade head           # Appliquer les migrations
alembic revision --autogenerate -m "message"  # Créer migration
```

## Configuration Environnement

### Backend (.env)
- Configuration PostgreSQL et clés API dans `backend/.env`
- Variables sensibles jamais committées

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` : URL de l'API backend (défaut: http://localhost:8000)
- `NEXTAUTH_URL` et `NEXTAUTH_SECRET` pour l'authentification

## Points d'Attention

### TypeScript
- Typage strict activé sur les deux projets
- Utiliser les types définis dans `lib/types/` (frontend)
- Toujours typer les réponses API

### Styling
- **Frontend uniquement** : Tailwind CSS avec thème crypto (couleurs cyan/vert)
- Components UI réutilisables dans `components/ui/`
- Pas de CSS custom, utiliser les utilities Tailwind

### Base de Données
- Toujours créer des migrations Alembic pour les changements de schéma
- Models SQLAlchemy dans `backend/app/models/`
- Schémas Pydantic dans `backend/app/schemas/`

### Structure Projet
- **Backend** : app/models, app/routes, app/schemas
- **Frontend** : app/ (App Router), components/, lib/
- Pas de modification des node_modules ou venv