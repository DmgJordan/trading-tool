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
- **Architecture DRY** : Utils, constants et hooks centralisés pour éliminer la duplication
- **Système de notifications** : Toast notifications pour feedback utilisateur

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
│   ├── ApiKeysConfiguration.tsx  # Config clés API (refactorisé avec hook)
│   ├── ConfigurationTest.tsx     # Tests système
│   ├── CCXTTest.tsx         # Tests CCXT multi-timeframes (refactorisé)
│   ├── ui/                  # Composants UI réutilisables
│   │   ├── Toast.tsx        # Système de notifications toast
│   │   ├── RSIIndicator.tsx # Indicateur RSI réutilisable
│   │   ├── MACard.tsx       # Carte moyennes mobiles
│   │   ├── VolumeCard.tsx   # Carte volume
│   │   ├── PriceDisplay.tsx # Affichage prix avec variation
│   │   ├── StatusBadge.tsx  # Badge de statut universel
│   │   └── index.ts         # Barrel exports
│   ├── trading/             # Composants trading spécialisés
│   │   ├── TradingAssistant.tsx  # Assistant IA (refactorisé)
│   │   ├── ClaudeResponse.tsx    # Réponse Claude AI
│   │   └── TradeRecommendations.tsx  # Recommandations
│   └── preferences/         # Composants préférences spécialisés
├── hooks/
│   ├── useAuth.ts           # Hook authentification
│   ├── usePreferences.ts    # Hook préférences
│   ├── useHyperliquid.ts    # Hook Hyperliquid
│   ├── useNotifications.ts  # Hook notifications toast
│   ├── useCCXTAnalysis.ts   # Hook analyse CCXT
│   ├── useApiKeyManagement.ts  # Hook gestion clés API
│   └── index.ts             # Barrel exports
├── constants/
│   ├── trading.ts           # Constantes trading (symboles, profils, services)
│   └── index.ts             # Barrel exports
├── utils/
│   ├── ui.ts                # Helpers UI (couleurs, icônes, labels)
│   ├── formatters.ts        # Formatage nombres, prix, volumes
│   └── index.ts             # Barrel exports
├── lib/
│   ├── api/
│   │   ├── client.ts        # Instance Axios centralisée
│   │   ├── auth.ts          # Client API auth
│   │   ├── preferences.ts   # Client API préférences
│   │   └── index.ts         # Barrel exports
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

## Helpers et Utilitaires Disponibles

### `utils/ui.ts` - Fonctions UI
```typescript
// Couleurs et styles de statut
getStatusColor(status: Status): string         // Classes Tailwind pour statuts
getStatusIcon(status: Status): JSX.Element     // Icône pour chaque statut

// Trading - Indicateurs RSI
getRSIColor(rsi: number): string               // Couleur selon niveau RSI
getRSILabel(rsi: number): string               // Label (Surachat/Survente/etc)

// Trading - Directions et profils
getDirectionColors(direction: 'long'|'short')  // Couleurs long/short
getConfidenceColor(level: number): string      // Couleur niveau de confiance
getProfileLabel(profile: TradingProfile): string          // Label profil (Court/Moyen/Long terme)
getProfileDescription(profile: TradingProfile): string    // Description complète profil

// Classes CSS préconfigurées
INDICATOR_CARD_CLASSES = {
  rsi: 'bg-gradient-to-br from-purple-50...',
  ma: 'bg-gradient-to-br from-blue-50...',
  volume: 'bg-gradient-to-br from-orange-50...',
  // ... autres indicateurs
}
```

### `utils/formatters.ts` - Formatage
```typescript
formatNumber(value: number, decimals?: number): string
formatPrice(price: number, minDecimals?: number): string
formatVolume(volume: number, decimals?: number): string    // Avec K/M/B
formatPercentageChange(value: number, decimals?: number): string  // Avec +/-
formatTicker(ticker: string): string                       // Normalisation
formatTimeframe(timeframe: string): string                 // Lecture humaine
formatCurrency(amount: number, currency?: string): string
formatDate(date: Date | string): string
```

### `constants/trading.ts` - Constantes Trading
```typescript
TRADING_SYMBOLS: readonly string[]              // ['BTC/USDT', 'ETH/USDT', ...]
EXCHANGES: readonly string[]                    // ['binance', 'coinbase', ...]

TRADING_PROFILES: TradingProfileConfig[] = [
  { value: 'short', label: 'Court terme', timeframes: {...}, description: '...' },
  { value: 'medium', label: 'Moyen terme', timeframes: {...}, description: '...' },
  { value: 'long', label: 'Long terme', timeframes: {...}, description: '...' }
]

CLAUDE_MODELS = {
  HAIKU: { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku', ... },
  SONNET: { id: 'claude-sonnet-4-5-20250929', name: 'Claude Sonnet 4.5', ... },
  OPUS: { id: 'claude-opus-4-1-20250805', name: 'Claude Opus 4.1', ... }
}

API_SERVICES = {
  ANTHROPIC: { name: 'Anthropic', description: '...', required: true },
  HYPERLIQUID: { name: 'Hyperliquid', description: '...', required: true },
  COINGECKO: { name: 'CoinGecko', description: '...', required: false }
}
```

### Hooks Métier Disponibles

#### `useNotifications()` - Système de notifications
```typescript
const { notifications, success, error, warning, info, remove } = useNotifications();

success('Opération réussie !');
error('Une erreur est survenue');
warning('Attention !');
info('Information');
```

#### `useApiKeyManagement()` - Gestion clés API
```typescript
const {
  user,                    // Utilisateur actuel
  testResults,             // Résultats des tests API
  isSaving,                // États de sauvegarde par service
  showKeys,                // Visibilité des clés par service
  register,                // React Hook Form register
  loadMaskedKeys,          // Charger les clés masquées
  toggleKeyVisibility,     // Toggle visibilité d'une clé
  saveApiKey,              // Sauvegarder une clé API
  testApiConnection,       // Tester une connexion API
} = useApiKeyManagement();
```

#### `useCCXTAnalysis()` - Analyse multi-timeframes
```typescript
const {
  analysisState,           // État complet de l'analyse
  selectedExchange,        // Exchange sélectionné
  selectedSymbol,          // Symbole sélectionné
  selectedProfile,         // Profil trading sélectionné
  isAnalyzing,            // Indicateur de chargement
  setSelectedExchange,
  setSelectedSymbol,
  setSelectedProfile,
  runAnalysis,            // Lancer l'analyse
  resetAnalysis,          // Reset de l'analyse
} = useCCXTAnalysis();
```

### Composants UI Réutilisables

#### `<RSIIndicator />` - Affichage RSI
```typescript
<RSIIndicator
  value={72.5}
  size="sm" | "md" | "lg"
  showLabel={true}
  className="custom-class"
/>
```

#### `<MACard />` - Moyennes mobiles
```typescript
<MACard
  indicators={{ ma20: 50000, ma50: 48000, ma200: 45000 }}
  timeframe="1h"
  className="custom-class"
/>
```

#### `<VolumeCard />` - Volume
```typescript
<VolumeCard
  indicators={{
    volume_24h: 1500000000,
    volume_ratio: 1.25,
    volume_avg_14d: 1200000000
  }}
  timeframe="1h"
/>
```

#### `<PriceDisplay />` - Prix avec variation
```typescript
<PriceDisplay
  symbol="BTC/USDT"
  price={50000}
  change={2.5}
  change24h={-1.2}
/>
```

#### `<StatusBadge />` - Badge de statut
```typescript
<StatusBadge
  status="success" | "error" | "warning" | "info" | "testing"
  label="Connexion réussie"
  size="sm" | "md" | "lg"
/>
```

## Refactorisation et Optimisation

### Résultats des Refactorisations Majeures

#### CCXTTest.tsx
- **Avant** : 572 lignes
- **Après** : 244 lignes (-57%)
- **Améliorations** :
  - Logique métier extraite dans `useCCXTAnalysis` hook
  - Fonctions dupliquées remplacées par utils (`getRSIColor`, `formatNumber`, etc.)
  - Composants UI réutilisables (`RSIIndicator`, `MACard`, `VolumeCard`)
  - Constantes centralisées (`TRADING_SYMBOLS`)

#### ApiKeysConfiguration.tsx
- **Avant** : 631 lignes
- **Après** : 173 lignes (-73%)
- **Améliorations** :
  - Logique complète extraite dans `useApiKeyManagement` hook
  - Pattern `renderApiKeySection` pour éliminer triplication
  - Utilisation des constantes `API_SERVICES`
  - Intégration du système de notifications

#### TradingAssistant.tsx
- **Améliorations** :
  - Fonction `getProfileDescription` inline supprimée
  - Utilisation des utils `getProfileLabel` et `getProfileDescription`
  - Code plus maintenable et cohérent

#### ConfigurationTest.tsx
- **Améliorations** :
  - Fonctions `getStatusColor` et `getStatusIcon` inline supprimées
  - Utilisation des utils centralisés
  - Réduction de la duplication

### Principes de Refactorisation Appliqués

1. **Extraction de la logique métier** : Hooks personnalisés pour toute logique complexe
2. **Centralisation des utils** : Aucune fonction dupliquée, tout dans `utils/`
3. **Constantes partagées** : Configuration centralisée dans `constants/`
4. **Composants réutilisables** : Pattern de composition avec composants UI
5. **Barrel exports** : Imports propres via `index.ts`
6. **Notifications unifiées** : Système toast au lieu de `alert()` et `console.log`