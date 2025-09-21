# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

**Application Type**: Trading tool avec interface web Next.js et API FastAPI
**Structure**: Monorepo avec deux applications principales :
- `frontend/` : Application Next.js 15 avec TypeScript et Tailwind CSS
- `backend/` : API FastAPI avec SQLAlchemy et PostgreSQL

### Architecture Backend
- **FastAPI** : Framework web moderne pour l'API REST
- **SQLAlchemy** : ORM avec migrations Alembic
- **PostgreSQL** : Base de données relationnelle avec Docker
- **Authentification JWT** : Access + refresh tokens sécurisés
- **Chiffrement AES** : Protection des clés API utilisateur
- **Structure MVC** : Models, routes, schemas, services séparés
- **Services** : Validators pour API externes (Anthropic, Hyperliquid)

### Architecture Frontend
- **Next.js 15** : Framework React avec App Router
- **TypeScript** : Typage strict activé
- **Zustand** : Gestion d'état global pour auth et préférences
- **Tailwind CSS** : Styling avec thème noir/blanc cohérent
- **React Hook Form + Zod** : Gestion et validation des formulaires
- **Axios centralisé** : Client API avec intercepteurs JWT automatiques
- **Protection des routes** : Middleware SSR + RouteGuard sans flash
- **Composants** : Structure modulaire réutilisable

## État Actuel de l'Application

### ✅ Fonctionnalités Implémentées
- **Authentification complète** : inscription, connexion, refresh tokens
- **Protection des routes** : middleware SSR + RouteGuard client sécurisé
- **Gestion utilisateur** : profil, clés API chiffrées
- **Système de préférences** : configuration trading personnalisée
- **Tests de connecteurs** : Anthropic API et Hyperliquid DEX
- **Interface responsive** : pages login, account, preferences, configuration
- **Diagnostics système** : santé backend et base de données

### ⏳ Non Implémentées (à développer)
- Dashboard de trading
- Module de trading actif
- Historique des transactions
- Algorithmes automatisés
- Graphiques et analytics

## Commandes de Développement

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Base de données
docker-compose up -d postgres  # Démarrer PostgreSQL + pgAdmin
alembic upgrade head           # Appliquer les migrations
alembic revision --autogenerate -m "message"  # Créer migration
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Développement (port 3000)
npm run build        # Build production
npm run lint         # Vérification ESLint
npm run type-check   # Vérification TypeScript
```

## Configuration Environnement

### Backend (.env)
```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/trading_db

# JWT & Sécurité
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-32-char-encryption-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Structure Détaillée

### Backend (`backend/app/`)
```
├── models/
│   ├── user.py              # Modèle User avec clés API chiffrées
│   └── user_preferences.py  # Modèle préférences trading
├── routes/
│   ├── auth.py              # Endpoints authentification
│   ├── users.py             # Gestion utilisateur
│   ├── user_preferences.py  # Endpoints préférences trading
│   └── connectors.py        # Tests API externes
├── schemas/
│   ├── auth.py              # Schémas JWT et auth
│   ├── user.py              # Schémas utilisateur
│   ├── user_preferences.py  # Schémas préférences (Pydantic v2)
│   └── connectors.py        # Schémas tests API
├── services/
│   ├── validators/
│   │   ├── api_validator.py # Validation APIs (Anthropic)
│   │   └── dex_validator.py # Validation DEX (Hyperliquid)
│   └── connectors/
├── auth.py                  # Utilitaires JWT et chiffrement
├── database.py              # Configuration SQLAlchemy
└── main.py                  # Point d'entrée FastAPI
```

### Frontend (`frontend/src/`)
```
├── app/
│   ├── page.tsx             # Page d'accueil (configuration)
│   ├── login/page.tsx       # Authentification avec RouteGuard
│   ├── account/page.tsx     # Gestion compte
│   ├── preferences/page.tsx # Configuration préférences trading
│   ├── layout.tsx           # Layout global avec AuthProvider
│   └── middleware.ts        # Protection SSR des routes
├── components/
│   ├── Navbar.tsx           # Navigation principale
│   ├── AuthProvider.tsx     # Provider auth avec RouteGuard
│   ├── RouteGuard.tsx       # Protection client anti-flash
│   ├── LoadingScreen.tsx    # Composants de chargement
│   ├── ApiKeysConfiguration.tsx  # Config clés API
│   ├── ConfigurationTest.tsx     # Tests système
│   └── preferences/         # Composants préférences spécialisés
├── lib/
│   ├── api/
│   │   ├── client.ts        # Instance Axios centralisée
│   │   ├── auth.ts          # Client API auth
│   │   └── preferences.ts   # Client API préférences
│   ├── types/
│   │   ├── auth.ts          # Types TypeScript auth + isInitialized
│   │   └── preferences.ts   # Types préférences trading
│   └── validation/
│       ├── auth.ts          # Schémas Zod auth
│       └── preferences.ts   # Schémas Zod préférences
└── store/
    ├── authStore.ts         # Store Zustand auth avec initialize()
    └── preferencesStore.ts  # Store Zustand préférences
```

## API Endpoints Disponibles

### Authentification (`/auth`)
- `POST /auth/register` - Inscription utilisateur
- `POST /auth/login` - Connexion avec tokens JWT
- `POST /auth/refresh` - Rafraîchissement access token
- `GET /auth/me` - Profil utilisateur actuel
- `POST /auth/logout` - Déconnexion

### Utilisateurs (`/users`)
- `GET /users/me` - Informations utilisateur avec clés masquées
- `PUT /users/me` - Mise à jour profil
- `PUT /users/me/api-keys` - Configuration clés API chiffrées

### Préférences Trading (`/users/me/preferences`)
- `GET /users/me/preferences/` - Récupérer préférences utilisateur
- `PUT /users/me/preferences/` - Mettre à jour préférences
- `POST /users/me/preferences/` - Créer préférences complètes
- `DELETE /users/me/preferences/` - Reset aux valeurs par défaut
- `GET /users/me/preferences/default` - Valeurs par défaut
- `GET /users/me/preferences/validation-info` - Contraintes de validation

### Connecteurs (`/connectors`)
- `POST /connectors/test-anthropic` - Test API Anthropic avec nouvelle clé
- `POST /connectors/test-hyperliquid` - Test Hyperliquid avec nouvelle clé
- `POST /connectors/test-*-stored` - Test avec clés stockées en base
- `POST /connectors/validate-key-format` - Validation format clé
- `GET /connectors/supported-services` - Services supportés

### Santé (`/`)
- `GET /health` - Santé API FastAPI
- `GET /db-health` - Santé base de données PostgreSQL

## Conventions de Code

### TypeScript
- Typage strict activé sur les deux projets
- Types centralisés dans `frontend/src/lib/types/`
- Interfaces pour les réponses API
- Validation Zod pour les formulaires

### Styling
- **Tailwind CSS uniquement** - pas de CSS custom
- **Thème cohérent** : noir/blanc avec accents
- **Design responsive** : mobile-first
- **Composants réutilisables** sans dépendances UI externes

### Base de Données
- **Migrations Alembic obligatoires** pour tout changement de schéma
- **Chiffrement AES** pour toutes les clés API sensibles
- **Models SQLAlchemy** dans `backend/app/models/`
- **Schémas Pydantic** dans `backend/app/schemas/`

### Sécurité
- **Tokens JWT** avec expiration configurée et refresh automatique
- **Protection des routes** : middleware SSR + RouteGuard client
- **Aucun flash** de contenu non autorisé (race condition résolue)
- **Mots de passe** hashés avec bcrypt
- **Clés API** chiffrées en base de données avec AES
- **CORS** configuré pour localhost uniquement
- **Validation stricte** côté backend (Pydantic v2) et frontend (Zod)
- **Instance Axios centralisée** avec intercepteurs JWT automatiques

## Docker Services
```bash
# PostgreSQL (port 5432)
docker-compose up -d postgres

# pgAdmin (port 5050) - Accès: admin@trading.com / admin123
docker-compose up -d pgadmin
```

## Notes pour le Développement

### Ajout de Nouvelles Fonctionnalités
1. **Backend** : Créer model → schema → route → service si nécessaire
2. **Frontend** : Créer types → API client → composants → intégration
3. **Base de données** : Toujours créer migration Alembic
4. **Tests** : Tester via les endpoints `/connectors/test-*`

### Gestion des Clés API
- Toujours chiffrer avant stockage en base
- Utiliser les endpoints de test dédiés
- Masquer les clés dans les réponses utilisateur
- Valider le format avant acceptation

### Pages Actuelles
- `/` : Configuration et tests système
- `/login` : Authentification avec toggle inscription (RouteGuard requireAuth=false)
- `/account` : Gestion profil et clés API
- `/preferences` : Configuration préférences trading personnalisées
- **Protection automatique** : Toutes les routes sauf `/login` protégées par authentification
- **Sécurité renforcée** : Middleware SSR + RouteGuard client sans flash

## Bonnes Pratiques Techniques

### Architecture API
- **Client Axios centralisé** dans `lib/api/client.ts` pour tous les modules
- **Barrel exports** dans `lib/api/index.ts` pour imports propres
- **Gestion d'erreurs** unifiée avec intercepteurs automatiques
- **Types TypeScript** cohérents entre frontend et backend

### Protection des Routes
- **Middleware Next.js** : `src/middleware.ts` pour protection SSR
- **RouteGuard** : Protection client avec gestion des états de chargement
- **AuthStore.isInitialized** : État séparé pour éliminer les race conditions
- **LoadingScreen** : Composants de transition élégants

### Validation des Données
- **Backend** : Pydantic v2 avec `@field_validator` et `@classmethod`
- **Frontend** : Zod avec schémas de validation stricte
- **Préférences** : Validation croisée et contraintes métier