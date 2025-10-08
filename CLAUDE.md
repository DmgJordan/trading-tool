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
- **Architecture DDD** : Domain-Driven Design avec séparation par domaines métier
  - `domains/auth/` : Authentification et sécurité
  - `domains/users/` : Gestion utilisateurs et tests API
  - `domains/market/` : Données de marché et CCXT
  - `domains/trading/` : Logique de trading
  - `domains/ai/` : Infrastructure IA multi-providers (Anthropic, OpenAI, DeepSeek)
  - `domains/ai_profile/` : Configuration IA utilisateur personnalisée
- **Services multi-providers** : Abstraction des providers IA avec interface unifiée

### Architecture Frontend
- **Next.js 15** : Framework React avec App Router et route groups `(app)` / `(public)`
- **TypeScript** : Typage strict activé
- **Zustand** : Gestion d'état global pour auth et préférences
- **TanStack Query** : Gestion du cache et des requêtes asynchrones
- **Tailwind CSS v4** : Styling avec thème noir/blanc cohérent (sans CSS custom)
- **React Hook Form + Zod** : Gestion et validation des formulaires
- **Axios centralisé** : Client API avec intercepteurs JWT automatiques
- **Protection des routes** : Middleware SSR + RouteGuard sans flash
- **Architecture Feature-Sliced** : Organisation par features métier
  - `features/auth/` : Authentification et sécurité
  - `features/trading/` : Trading et assistant IA
  - `features/preferences/` : Configuration utilisateur
  - `features/portfolio/` : Portfolio et positions
  - `features/dev-tools/` : Outils de développement
- **Composants réutilisables** : `shared/ui/` pour composants transversaux
- **Architecture DRY** : Utils, constants et hooks centralisés pour éliminer la duplication
- **Système de notifications** : Toast notifications pour feedback utilisateur

## État Actuel de l'Application

### ✅ Fonctionnalités Implémentées
- **Authentification complète** : inscription, connexion, refresh tokens, sécurité JWT
- **Protection des routes** : middleware SSR + RouteGuard client sécurisé sans flash
- **Gestion utilisateur** : profil, clés API chiffrées (Anthropic, Hyperliquid, CoinGecko)
- **Système de préférences trading** : configuration personnalisée par utilisateur
- **Tests de connecteurs API** : validation Anthropic, Hyperliquid DEX, CoinGecko
- **Interface responsive** : pages login, account, preferences, configuration, dashboard, trading
- **Diagnostics système** : santé backend, base de données, status connecteurs
- **Infrastructure IA multi-providers** : Support Anthropic, OpenAI, DeepSeek avec abstraction
- **Configuration IA utilisateur** : Profils IA personnalisés (AIProfile)
- **Analyse de marché CCXT** : Données multi-timeframes, indicateurs techniques (RSI, MA, Volume)
- **Assistant de trading IA** : Recommandations basées sur analyse technique et IA
- **Dashboard trading** : Vue d'ensemble portfolio, positions, performance
- **Système de notifications** : Toast notifications avec types (success, error, warning, info)

### ⏳ Non Implémentées (à développer)
- Exécution automatisée des trades
- Historique complet des transactions avec analytics
- Backtesting des stratégies
- Algorithmes de trading avancés
- Graphiques avancés avec TradingView ou similaire
- Alertes et notifications push

## Commandes de Développement

### Backend
```bash
cd backend

# Installation et démarrage
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Base de données (CRITICAL: TOUJOURS démarrer PostgreSQL avant le backend)
docker-compose up -d postgres  # Démarrer PostgreSQL (port 5432)
docker-compose up -d pgadmin   # Démarrer pgAdmin (port 5050)

# Migrations Alembic (CRITICAL: Obligatoires pour tout changement de modèle)
alembic upgrade head                           # Appliquer toutes les migrations
alembic revision --autogenerate -m "message"   # Créer nouvelle migration
alembic current                                # Voir la migration actuelle
alembic history                                # Historique des migrations
alembic downgrade -1                           # Revenir en arrière d'une migration
```

### Frontend
```bash
cd frontend

# Installation et démarrage
npm install
npm run dev          # Développement (port 3000)
npm run build        # Build production
npm run start        # Lancer build production

# Vérifications (ALWAYS: Exécuter avant commits)
npm run lint         # Vérification ESLint avec --fix automatique
npm run lint:check   # Vérification ESLint sans fix
npm run type-check   # Vérification TypeScript (CRITICAL: MUST pass)
npm run format       # Formatage Prettier avec auto-fix
npm run format:check # Vérification Prettier sans fix
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

### Backend (`backend/app/`) - Architecture DDD
```
├── domains/                      # Domaines métier (DDD)
│   ├── auth/                     # Authentification et sécurité
│   │   ├── models.py             # Modèle User avec clés API chiffrées
│   │   ├── schemas.py            # Schémas Pydantic JWT et auth
│   │   ├── service.py            # Logique métier authentification
│   │   └── router.py             # Endpoints /auth
│   ├── users/                    # Gestion utilisateurs
│   │   ├── models.py             # Modèle User étendu
│   │   ├── schemas.py            # Schémas utilisateur
│   │   ├── service.py            # Logique métier utilisateur
│   │   ├── api_key_testing.py    # Tests connecteurs API
│   │   └── router.py             # Endpoints /users
│   ├── market/                   # Données de marché
│   │   ├── models.py             # Modèle MarketData
│   │   ├── schemas.py            # Schémas données de marché
│   │   ├── service.py            # Logique métier marché
│   │   ├── adapters/             # Adaptateurs externes
│   │   │   └── ccxt_adapter.py   # Adaptateur CCXT
│   │   └── router.py             # Endpoints /market
│   ├── trading/                  # Logique de trading
│   │   ├── models.py             # Modèles trading (positions, ordres)
│   │   ├── schemas.py            # Schémas trading
│   │   ├── service.py            # Logique métier trading
│   │   ├── adapters/             # Adaptateurs exchanges
│   │   │   └── hyperliquid.py    # Adaptateur Hyperliquid
│   │   └── router.py             # Endpoints /trading
│   ├── ai/                       # Infrastructure IA multi-providers
│   │   ├── schemas.py            # Schémas IA unifiés
│   │   ├── service.py            # Service IA avec abstraction
│   │   ├── router.py             # Endpoints /ai
│   │   ├── providers/            # Providers IA
│   │   │   ├── base.py           # Interface BaseAIProvider
│   │   │   ├── anthropic.py      # Provider Anthropic Claude
│   │   │   ├── openai.py         # Provider OpenAI GPT
│   │   │   └── deepseek.py       # Provider DeepSeek
│   │   └── prompts/              # Prompts IA structurés
│   │       ├── system_prompts.py # Prompts système
│   │       ├── market_analysis.py # Prompts analyse marché
│   │       ├── trading_strategy.py # Prompts stratégie
│   │       └── risk_assessment.py # Prompts gestion risque
│   └── ai_profile/               # Configuration IA utilisateur
│       ├── models.py             # Modèle AIProfile
│       ├── schemas.py            # Schémas profil IA
│       ├── service.py            # Logique métier profil IA
│       └── router.py             # Endpoints /ai-profile
├── core.py                       # Configuration SQLAlchemy, DB, Base
└── main.py                       # Point d'entrée FastAPI avec routers DDD
```

### Frontend (`frontend/src/`) - Architecture Feature-Sliced Design
```
├── app/                          # Next.js 15 App Router
│   ├── (app)/                    # Route group protégé (authentification requise)
│   │   ├── page.tsx              # Page d'accueil / configuration
│   │   ├── account/page.tsx      # Gestion compte utilisateur
│   │   ├── preferences/page.tsx  # Configuration préférences trading
│   │   ├── dashboard/page.tsx    # Dashboard trading principal
│   │   ├── trading/page.tsx      # Page trading avec assistant IA
│   │   └── layout.tsx            # Layout app avec navigation
│   ├── (public)/                 # Route group public (pas d'auth)
│   │   ├── login/page.tsx        # Authentification et inscription
│   │   └── layout.tsx            # Layout public minimaliste
│   ├── layout.tsx                # Layout racine avec providers
│   └── middleware.ts             # Protection SSR des routes (CRITICAL)
│
├── features/                     # Features métier (Feature-Sliced Design)
│   ├── auth/                     # Authentification
│   │   ├── ui/                   # Composants UI auth
│   │   │   ├── LoginForm.tsx
│   │   │   └── RouteGuard.tsx    # Protection client anti-flash
│   │   └── model/                # Store et logique métier
│   │       └── authStore.ts      # Store Zustand auth
│   ├── trading/                  # Trading et assistant IA
│   │   ├── ui/                   # Composants UI trading
│   │   │   ├── TradingAssistant.tsx
│   │   │   ├── TradeRecommendations.tsx
│   │   │   ├── MarketAnalysis.tsx
│   │   │   └── PositionsList.tsx
│   │   ├── model/                # Store et logique métier
│   │   │   └── tradingStore.ts
│   │   └── api/                  # API trading
│   │       └── tradingApi.ts
│   ├── preferences/              # Préférences utilisateur
│   │   ├── ui/                   # Composants UI préférences
│   │   │   └── PreferencesForm.tsx
│   │   └── model/                # Store et logique métier
│   │       └── preferencesStore.ts
│   ├── portfolio/                # Portfolio et positions
│   │   ├── ui/                   # Composants UI portfolio
│   │   │   ├── PortfolioSummary.tsx
│   │   │   └── PositionsTable.tsx
│   │   └── model/                # Store et logique métier
│   │       └── portfolioStore.ts
│   └── dev-tools/                # Outils de développement
│       └── ui/                   # Composants UI dev
│           ├── ApiKeysConfiguration.tsx
│           ├── ConfigurationTest.tsx
│           └── CCXTTest.tsx
│
├── shared/                       # Code partagé transversal
│   ├── ui/                       # Composants UI réutilisables
│   │   ├── Toast.tsx             # Système de notifications
│   │   ├── RSIIndicator.tsx      # Indicateur RSI
│   │   ├── MACard.tsx            # Carte moyennes mobiles
│   │   ├── VolumeCard.tsx        # Carte volume
│   │   ├── PriceDisplay.tsx      # Affichage prix avec variation
│   │   ├── StatusBadge.tsx       # Badge de statut universel
│   │   ├── Navbar.tsx            # Navigation principale
│   │   ├── LoadingScreen.tsx     # Écrans de chargement
│   │   └── index.ts              # Barrel exports
│   ├── lib/                      # Utilitaires partagés
│   │   ├── formatters.ts         # Formatage nombres, prix, volumes
│   │   ├── ui.ts                 # Helpers UI (couleurs, icônes, labels)
│   │   └── index.ts              # Barrel exports
│   └── config/                   # Configuration partagée
│       ├── trading.ts            # Constantes trading (symboles, profils)
│       └── index.ts              # Barrel exports
│
├── app-providers/                # Providers globaux
│   ├── QueryProvider.tsx         # TanStack Query provider
│   └── AuthProvider.tsx          # Provider auth global
│
├── services/                     # Services API
│   ├── api.ts                    # Instance Axios centralisée
│   ├── auth.ts                   # Service API auth
│   ├── trading.ts                # Service API trading
│   ├── market.ts                 # Service API market
│   └── preferences.ts            # Service API préférences
│
├── lib/types/                    # Types TypeScript globaux
│   ├── api/                      # Types API
│   │   ├── auth.ts               # Types auth
│   │   ├── trading.ts            # Types trading
│   │   └── market.ts             # Types market
│   └── components/               # Types composants
│       └── ui.ts                 # Types UI
│
└── hooks/                        # Hooks personnalisés (DEPRECATED: Migrer vers features/*/model/)
    ├── useAuth.ts                # Hook authentification
    ├── usePreferences.ts         # Hook préférences
    ├── useHyperliquid.ts         # Hook Hyperliquid
    ├── useNotifications.ts       # Hook notifications toast
    ├── useCCXTAnalysis.ts        # Hook analyse CCXT
    ├── useApiKeyManagement.ts    # Hook gestion clés API
    └── index.ts                  # Barrel exports
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
- `POST /users/test-anthropic` - Test API Anthropic avec nouvelle clé
- `POST /users/test-hyperliquid` - Test Hyperliquid avec nouvelle clé
- `GET /users/supported-services` - Services API supportés

### Market Data (`/market`)
- `GET /market/ticker` - Prix actuel et variation 24h pour un symbole
- `GET /market/ohlcv` - Données OHLCV historiques
- `GET /market/analysis` - Analyse technique multi-timeframes (RSI, MA, Volume)
- `GET /market/supported-exchanges` - Exchanges supportés via CCXT

### Trading (`/trading`)
- `GET /trading/positions` - Positions ouvertes Hyperliquid
- `GET /trading/balance` - Balance du compte
- `POST /trading/order` - Créer un ordre
- `GET /trading/orders` - Liste des ordres
- `DELETE /trading/order/{id}` - Annuler un ordre

### Intelligence Artificielle (`/ai`)
- `POST /ai/analyze` - Analyse marché par IA (multi-provider)
- `POST /ai/recommend` - Recommandations trading par IA
- `POST /ai/risk-assessment` - Évaluation des risques par IA
- `GET /ai/providers` - Liste des providers IA disponibles

### Configuration IA (`/ai-profile`)
- `GET /ai-profile/me` - Récupérer profil IA utilisateur
- `PUT /ai-profile/me` - Mettre à jour profil IA
- `POST /ai-profile/me` - Créer profil IA
- `DELETE /ai-profile/me` - Supprimer profil IA

### Santé (`/`)
- `GET /health` - Santé API FastAPI
- `GET /db-health` - Santé base de données PostgreSQL

## Conventions de Code

### TypeScript
- Typage strict activé sur les deux projets
- Types centralisés dans `frontend/src/lib/types/`
- Interfaces pour les réponses API
- Validation Zod pour les formulaires
- **TOUJOURS** typer les réponses API avec génériques (`apiClient.post<ResponseType>()`)

### Styling
- **Tailwind CSS uniquement** - pas de CSS custom
- **Thème cohérent** : noir/blanc avec accents
- **Design responsive** : mobile-first
- **Composants réutilisables** sans dépendances UI externes

### DRY (Don't Repeat Yourself)
- **JAMAIS** dupliquer de fonctions utilitaires - toujours centraliser dans `utils/`
- **JAMAIS** dupliquer de constantes - toujours centraliser dans `constants/`
- **TOUJOURS** extraire la logique métier dans des hooks personnalisés
- **Barrel exports** obligatoires pour tous les modules (`index.ts`)
- **Pattern de composition** : utiliser des composants UI réutilisables

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

### Pages Actuelles (Next.js App Router)
- `/` : Page d'accueil avec configuration et tests système
- `/login` : Authentification et inscription (route publique)
- `/account` : Gestion profil utilisateur et clés API (protégée)
- `/preferences` : Configuration préférences trading personnalisées (protégée)
- `/dashboard` : Dashboard de trading principal (protégée)
- `/trading` : Page trading avec assistant IA (protégée)
- **Protection automatique** :
  - Route group `(app)` : Toutes les routes protégées par authentification
  - Route group `(public)` : Routes publiques accessibles sans auth
  - **CRITICAL**: Middleware SSR (`src/middleware.ts`) + RouteGuard client sans flash

## Bonnes Pratiques Techniques

### Architecture DDD Backend
- **CRITICAL**: TOUJOURS suivre la structure DDD par domaines
- **NEVER**: Créer de fichiers dans les anciens dossiers `models/`, `routes/`, `schemas/` (DEPRECATED)
- **ALWAYS**: Créer `models.py`, `schemas.py`, `service.py`, `router.py` dans `domains/<nom_domaine>/`
- **Pattern**: Domain → Service → Router (logique métier isolée dans service)
- **Adapters**: Utiliser le pattern adapter pour services externes (CCXT, APIs)

### Architecture Feature-Sliced Frontend
- **CRITICAL**: TOUJOURS suivre la structure Feature-Sliced Design
- **NEVER**: Créer de composants dans le dossier `components/` racine (DEPRECATED: migrer vers `features/` ou `shared/`)
- **ALWAYS**: Organiser par feature métier dans `features/<feature>/ui/`, `features/<feature>/model/`
- **Pattern**: UI → Model → API (séparation claire des responsabilités)
- **Shared**: Uniquement pour composants UI transversaux utilisés par 3+ features

### Architecture API Services
- **CRITICAL**: Utiliser `services/api.ts` comme instance Axios centralisée
- **ALWAYS**: Créer un service API par domaine (`services/auth.ts`, `services/trading.ts`, etc.)
- **Intercepteurs**: Refresh token automatique configuré dans `services/api.ts`
- **Types**: TOUJOURS typer les réponses avec génériques (`apiClient.post<ResponseType>()`)
- **Barrel exports**: Centraliser les exports dans `services/index.ts`

### Protection des Routes
- **CRITICAL**: Middleware Next.js (`src/middleware.ts`) pour protection SSR (MUST exist)
- **ALWAYS**: Utiliser route groups `(app)` pour routes protégées, `(public)` pour routes publiques
- **RouteGuard**: Protection client avec gestion des états de chargement (composant dans `features/auth/ui/`)
- **AuthStore.isInitialized**: État séparé pour éliminer les race conditions
- **NEVER**: Flash de contenu non autorisé (déjà résolu avec isInitialized)

### Validation des Données
- **Backend**: Pydantic v2 avec `@field_validator` et `@classmethod`
- **Frontend**: Zod v4 avec schémas de validation stricte
- **ALWAYS**: Valider côté backend ET frontend pour sécurité maximale
- **Contraintes métier**: Validation croisée dans les services (pas dans les schémas)

## Helpers et Utilitaires Disponibles

### `shared/lib/formatters.ts` - Formatage (CRITICAL: Utiliser ces fonctions, jamais dupliquer)
- `formatNumber(value: number, decimals?: number): string` - Formatage nombres avec séparateurs
- `formatPrice(price: number, minDecimals?: number): string` - Formatage prix avec décimales dynamiques
- `formatVolume(volume: number, decimals?: number): string` - Formatage volume avec K/M/B
- `formatPercentageChange(value: number, decimals?: number): string` - Formatage pourcentage avec +/-
- `formatTicker(ticker: string): string` - Normalisation symboles trading
- `formatTimeframe(timeframe: string): string` - Timeframes en lecture humaine
- `formatCurrency(amount: number, currency?: string): string` - Formatage monétaire
- `formatDate(date: Date | string): string` - Formatage dates

### `shared/lib/ui.ts` - Helpers UI (CRITICAL: Utiliser ces fonctions, jamais dupliquer)
- `getStatusColor(status: Status): string` - Classes Tailwind pour statuts
- `getStatusIcon(status: Status): JSX.Element` - Icônes pour statuts
- `getRSIColor(rsi: number): string` - Couleur selon niveau RSI
- `getRSILabel(rsi: number): string` - Label RSI (Surachat/Survente/etc)
- `getDirectionColors(direction: 'long'|'short')` - Couleurs long/short
- `getConfidenceColor(level: number): string` - Couleur niveau de confiance
- `getProfileLabel(profile: TradingProfile): string` - Label profil trading
- `getProfileDescription(profile: TradingProfile): string` - Description complète profil
- `INDICATOR_CARD_CLASSES` - Classes CSS préconfigurées pour cartes indicateurs

### `shared/config/trading.ts` - Constantes Trading (NEVER: Dupliquer ces constantes)
- `TRADING_SYMBOLS: readonly string[]` - Liste symboles disponibles
- `EXCHANGES: readonly string[]` - Liste exchanges supportés
- `TRADING_PROFILES: TradingProfileConfig[]` - Configuration profils trading complets
- `CLAUDE_MODELS` - Modèles Claude AI disponibles avec specs
- `API_SERVICES` - Services API supportés avec métadonnées

### Composants UI Réutilisables (CRITICAL: Utiliser depuis `shared/ui/`, NEVER dupliquer)

#### `<RSIIndicator />` - Indicateur RSI visuel
- Props: `value`, `size` (sm/md/lg), `showLabel`, `className`
- Couleurs automatiques selon niveau (survente/surachat)
- Import: `import { RSIIndicator } from '@/shared/ui'`

#### `<MACard />` - Carte moyennes mobiles
- Props: `indicators` (ma20, ma50, ma200), `timeframe`, `className`
- Affichage compact avec tendance visuelle
- Import: `import { MACard } from '@/shared/ui'`

#### `<VolumeCard />` - Carte volume trading
- Props: `indicators` (volume_24h, volume_ratio, volume_avg_14d), `timeframe`
- Formatage automatique avec K/M/B
- Import: `import { VolumeCard } from '@/shared/ui'`

#### `<PriceDisplay />` - Affichage prix avec variation
- Props: `symbol`, `price`, `change`, `change24h`
- Couleurs automatiques (rouge/vert) selon variation
- Import: `import { PriceDisplay } from '@/shared/ui'`

#### `<StatusBadge />` - Badge de statut universel
- Props: `status` (success/error/warning/info/testing), `label`, `size`
- Icônes et couleurs automatiques par statut
- Import: `import { StatusBadge } from '@/shared/ui'`

#### `<Toast />` - Système de notifications
- Utiliser le hook `useNotifications()` pour gérer
- Notifications empilées avec auto-dismiss
- Import: `import { useNotifications } from '@/hooks'`

#### `<Navbar />` - Navigation principale
- Navigation responsive avec links et déconnexion
- Protection auth intégrée
- Import: `import { Navbar } from '@/shared/ui'`

#### `<LoadingScreen />` - Écrans de chargement
- Variantes: spinner, skeleton, page complète
- Import: `import { LoadingScreen } from '@/shared/ui'`

## Principes de Développement et Refactorisation

### Principes DRY (Don't Repeat Yourself) - CRITICAL
1. **NEVER dupliquer de fonctions utilitaires**
   - ALWAYS utiliser `shared/lib/formatters.ts` pour formatage
   - ALWAYS utiliser `shared/lib/ui.ts` pour helpers UI
   - BEFORE créer une fonction, vérifier si elle existe déjà

2. **NEVER dupliquer de constantes**
   - ALWAYS utiliser `shared/config/trading.ts` pour constantes trading
   - NEVER hardcoder des valeurs répétées (symboles, exchanges, etc.)

3. **ALWAYS extraire la logique métier**
   - Backend: Logique dans `service.py`, pas dans `router.py`
   - Frontend: Logique dans hooks ou stores, pas dans composants
   - Pattern: Composant UI → Hook/Store → Service API

4. **ALWAYS utiliser des composants réutilisables**
   - BEFORE créer un composant, vérifier `shared/ui/`
   - Composant utilisé 2+ fois = extraire dans `shared/ui/`
   - Composant spécifique à feature = rester dans `features/<feature>/ui/`

5. **Barrel exports obligatoires**
   - ALWAYS créer `index.ts` dans chaque dossier de modules
   - Facilite les imports : `import { A, B } from '@/shared/ui'`

6. **Notifications unifiées**
   - NEVER utiliser `alert()` ou `console.log` pour feedback utilisateur
   - ALWAYS utiliser le système toast (`useNotifications()`)

### Workflow de Développement

#### Ajout de Nouvelle Fonctionnalité Backend
1. **Créer domaine** : `backend/app/domains/<nom_domaine>/`
2. **Créer modèle** : `models.py` avec SQLAlchemy
3. **Créer schémas** : `schemas.py` avec Pydantic v2
4. **Créer service** : `service.py` avec logique métier
5. **Créer router** : `router.py` avec endpoints FastAPI
6. **Migration Alembic** : `alembic revision --autogenerate -m "description"`
7. **Appliquer migration** : `alembic upgrade head`
8. **Enregistrer router** : Dans `main.py`, `app.include_router(nouveau_router)`

#### Ajout de Nouvelle Fonctionnalité Frontend
1. **Créer feature** : `frontend/src/features/<feature>/`
2. **Créer types** : `lib/types/api/<feature>.ts`
3. **Créer service API** : `services/<feature>.ts` avec Axios
4. **Créer store** : `features/<feature>/model/<feature>Store.ts` avec Zustand
5. **Créer composants UI** : `features/<feature>/ui/<Composant>.tsx`
6. **Créer page** : `app/(app)/<route>/page.tsx`
7. **Tests** : Vérifier avec `npm run type-check` et `npm run lint`

### Architecture et Organisation - CRITICAL RULES

#### Backend (CRITICAL)
- **NEVER** créer fichiers dans `models/`, `routes/`, `schemas/` racine (DEPRECATED)
- **ALWAYS** utiliser structure DDD dans `domains/<nom_domaine>/`
- **ALWAYS** créer migration Alembic pour changement de schéma
- **Pattern**: Router → Service → Models (séparation des responsabilités)

#### Frontend (CRITICAL)
- **NEVER** créer composants dans `components/` racine (DEPRECATED)
- **ALWAYS** utiliser Feature-Sliced Design dans `features/` ou `shared/`
- **ALWAYS** vérifier TypeScript (`npm run type-check`) avant commit
- **Pattern**: Page → Feature UI → Store → Service API