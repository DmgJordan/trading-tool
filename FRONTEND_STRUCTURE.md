# Structure Frontend - Trading Tool

## Vue d'ensemble

Application Next.js 15 avec TypeScript, organisée selon une architecture modulaire DRY avec séparation claire des responsabilités.

## Arborescence complète

```
frontend/src/
│
├── app/                                    # Pages Next.js (App Router)
│   ├── layout.tsx                          # Layout racine avec AuthProvider
│   ├── page.tsx                            # Page d'accueil (configuration)
│   ├── login/
│   │   └── page.tsx                        # Authentification
│   ├── account/
│   │   └── page.tsx                        # Gestion compte utilisateur
│   ├── preferences/
│   │   └── page.tsx                        # Configuration préférences trading
│   ├── trading/
│   │   └── page.tsx                        # Interface trading principale
│   └── dashboard/
│       └── page.tsx                        # Dashboard analytics
│
├── components/                             # Composants React
│   │
│   ├── # Composants racine
│   ├── AuthProvider.tsx                    # Provider authentification
│   ├── RouteGuard.tsx                      # Protection routes (anti-flash)
│   ├── Navbar.tsx                          # Navigation principale
│   ├── LoadingScreen.tsx                   # Écrans de chargement
│   ├── ApiKeysConfiguration.tsx            # Config clés API (refactorisé)
│   ├── ConfigurationTest.tsx               # Tests système
│   ├── CCXTTest.tsx                        # Tests CCXT multi-timeframes
│   │
│   ├── ui/                                 # Composants UI réutilisables
│   │   ├── index.ts                        # Barrel export
│   │   ├── Toast.tsx                       # Notifications toast
│   │   ├── RSIIndicator.tsx                # Indicateur RSI
│   │   ├── MACard.tsx                      # Carte moyennes mobiles
│   │   ├── VolumeCard.tsx                  # Carte volume
│   │   ├── PriceDisplay.tsx                # Affichage prix
│   │   └── StatusBadge.tsx                 # Badge statut
│   │
│   ├── preferences/                        # Composants préférences
│   │   ├── RangeSlider.tsx                 # Slider avec validation
│   │   ├── RadioCardGroup.tsx              # Groupe radio cards
│   │   ├── ToggleSwitch.tsx                # Toggle switch
│   │   └── MultiSelect.tsx                 # Sélection multiple
│   │
│   └── trading/                            # Composants trading
│       ├── TradingAssistant.tsx            # Assistant IA principal
│       ├── ClaudeResponse.tsx              # Affichage réponse Claude
│       ├── TradeRecommendations.tsx        # Recommandations
│       ├── TradeCard.tsx                   # Carte recommandation
│       ├── ExecuteTradeModal.tsx           # Modal exécution trade
│       ├── ModelSelector.tsx               # Sélecteur modèle Claude
│       ├── HyperliquidSection.tsx          # Section Hyperliquid
│       ├── PortfolioOverview.tsx           # Vue portefeuille
│       ├── PositionsView.tsx               # Vue positions
│       ├── PositionCard.tsx                # Carte position
│       ├── OrdersView.tsx                  # Vue ordres
│       ├── MetricsHeader.tsx               # Header métriques
│       ├── PnlChart.tsx                    # Graphique P&L
│       ├── QuickActions.tsx                # Actions rapides
│       └── TradingTabs.tsx                 # Tabs navigation
│
├── hooks/                                  # Custom React Hooks
│   ├── index.ts                            # Barrel export
│   ├── useAuth.ts                          # Authentification
│   ├── usePreferences.ts                   # Préférences trading
│   ├── useHyperliquid.ts                   # Hyperliquid DEX
│   ├── useNotifications.ts                 # Système notifications
│   ├── useCCXTAnalysis.ts                  # Analyse CCXT
│   └── useApiKeyManagement.ts              # Gestion clés API
│
├── lib/                                    # Bibliothèques core
│   │
│   ├── api/                                # Clients API
│   │   ├── index.ts                        # Barrel export + types
│   │   ├── client.ts                       # Instance Axios centralisée
│   │   ├── auth.ts                         # API authentification
│   │   ├── preferences.ts                  # API préférences
│   │   ├── claude.ts                       # API Claude
│   │   ├── ohlcv.ts                        # API OHLCV/CCXT
│   │   └── hyperliquid-trading.ts          # API Hyperliquid
│   │
│   ├── types/                              # Types TypeScript centralisés
│   │   ├── index.ts                        # Barrel export global
│   │   ├── auth.ts                         # Types authentification
│   │   ├── preferences.ts                  # Types préférences
│   │   ├── hyperliquid.ts                  # Types Hyperliquid
│   │   ├── connectors.ts                   # Types connecteurs
│   │   ├── trading.ts                      # Types trading
│   │   │
│   │   ├── api/                            # Types API (source unique)
│   │   │   ├── index.ts                    # Barrel export
│   │   │   ├── ohlcv.ts                    # Types OHLCV (source)
│   │   │   └── claude.ts                   # Types Claude (réutilise ohlcv)
│   │   │
│   │   └── components/                     # Types composants
│   │       ├── index.ts                    # Barrel export
│   │       ├── ui.ts                       # Props composants UI
│   │       └── preferences.ts              # Props composants prefs
│   │
│   ├── validation/                         # Schémas Zod
│   │   ├── auth.ts                         # Validation auth
│   │   └── preferences.ts                  # Validation préférences
│   │
│   └── index.ts                            # Barrel export lib/
│
├── store/                                  # État global Zustand
│   ├── authStore.ts                        # Store authentification
│   ├── preferencesStore.ts                 # Store préférences
│   └── hyperliquidStore.ts                 # Store Hyperliquid
│
├── constants/                              # Constantes application
│   ├── index.ts                            # Barrel export
│   ├── routes.ts                           # Routes protégées
│   ├── preferences.ts                      # Configs préférences
│   └── trading.ts                          # Constantes trading
│       # - TRADING_SYMBOLS
│       # - EXCHANGES
│       # - TRADING_PROFILES
│       # - CLAUDE_MODELS
│       # - API_SERVICES
│
├── utils/                                  # Fonctions utilitaires
│   ├── index.ts                            # Barrel export
│   ├── ui.ts                               # Helpers UI (couleurs, icônes)
│   ├── formatters.ts                       # Formatage (prix, volumes, dates)
│   ├── validators.ts                       # Validateurs custom
│   └── api.ts                              # Helpers API
│
└── middleware.ts                           # Middleware Next.js (protection SSR)
```

## Organisation par domaine

### 🎨 UI & Présentation
- **`components/ui/`** : Composants réutilisables (RSI, MA, Volume, Toast)
- **`utils/ui.ts`** : Helpers couleurs, icônes, labels
- **`utils/formatters.ts`** : Formatage prix, volumes, pourcentages

### 🔐 Authentification & Sécurité
- **`hooks/useAuth.ts`** : Logique authentification
- **`store/authStore.ts`** : État global auth
- **`lib/api/auth.ts`** : Client API auth
- **`lib/types/auth.ts`** : Types auth
- **`lib/validation/auth.ts`** : Schémas Zod
- **`middleware.ts`** : Protection SSR
- **`components/RouteGuard.tsx`** : Protection client

### 📊 Trading & Analyse
- **`components/trading/`** : Composants trading
- **`hooks/useCCXTAnalysis.ts`** : Logique analyse CCXT
- **`lib/api/claude.ts`** : Client API Claude
- **`lib/api/ohlcv.ts`** : Client API OHLCV
- **`lib/types/api/`** : Types API (source unique)
- **`constants/trading.ts`** : Constantes trading

### ⚙️ Préférences
- **`components/preferences/`** : Composants préférences
- **`hooks/usePreferences.ts`** : Logique préférences
- **`store/preferencesStore.ts`** : État global prefs
- **`lib/api/preferences.ts`** : Client API prefs
- **`lib/types/preferences.ts`** : Types prefs
- **`constants/preferences.ts`** : Configs prefs

### 🔑 Gestion Clés API
- **`hooks/useApiKeyManagement.ts`** : Logique complète
- **`components/ApiKeysConfiguration.tsx`** : UI (173 lignes)

### 🔔 Notifications
- **`hooks/useNotifications.ts`** : Logique notifications
- **`components/ui/Toast.tsx`** : Composant toast

### 💱 Hyperliquid
- **`hooks/useHyperliquid.ts`** : Logique Hyperliquid
- **`store/hyperliquidStore.ts`** : État global
- **`lib/api/hyperliquid-trading.ts`** : Client API
- **`lib/types/hyperliquid.ts`** : Types
- **`components/trading/HyperliquidSection.tsx`** : UI

## Patterns et principes appliqués

### 📦 Barrel Exports
Tous les modules ont un `index.ts` pour des imports propres :
```typescript
// ❌ Avant
import { useAuth } from '@/hooks/useAuth';
import { usePreferences } from '@/hooks/usePreferences';

// ✅ Après
import { useAuth, usePreferences } from '@/hooks';
```

### 🎯 Single Source of Truth
- **Types communs** : `lib/types/api/ohlcv.ts` (MAIndicators, VolumeIndicators, etc.)
- **Helpers UI** : `utils/ui.ts` (getRSIColor, getStatusColor, etc.)
- **Formatters** : `utils/formatters.ts` (formatPrice, formatVolume, etc.)
- **Constantes** : `constants/trading.ts` (TRADING_SYMBOLS, API_SERVICES, etc.)

### 🔄 Séparation des responsabilités

#### Composants
- **Présentation pure** : Reçoivent props, affichent UI
- **Pas de logique métier** : Déléguée aux hooks

#### Hooks
- **Logique métier** : État, API calls, transformations
- **Réutilisables** : Indépendants des composants
- **Testables** : Logique isolée

#### Types
- **Centralisés** : `lib/types/`
- **Organisés par domaine** : `api/`, `components/`
- **Ré-exports** : Pour compatibilité (`trading.ts` → `api/claude.ts`)

### 🛡️ Protection des routes
1. **SSR** : `middleware.ts` (Next.js middleware)
2. **Client** : `RouteGuard.tsx` (anti-flash)
3. **État** : `authStore.isInitialized` (race condition résolue)

### 🎨 Styling
- **Tailwind uniquement** : Pas de CSS custom
- **Classes préconfigurées** : `INDICATOR_CARD_CLASSES` dans `utils/ui.ts`
- **Thème cohérent** : Noir/blanc avec accents

## Métriques de refactorisation

### Réduction de code
- **CCXTTest.tsx** : 572 → 244 lignes (-57%)
- **ApiKeysConfiguration.tsx** : 631 → 173 lignes (-73%)
- **Duplication éliminée** : ~90% des fonctions dupliquées centralisées

### Nouveaux modules créés
- **6 composants UI** réutilisables
- **7 hooks métier** personnalisés
- **3 fichiers constants** centralisés
- **2 fichiers utils** (ui, formatters)
- **Types organisés** en 3 catégories (api, components, core)

### Amélioration maintenabilité
- **Imports propres** : Barrel exports partout
- **Types centralisés** : Source unique pour types API
- **Logique extraite** : Hooks séparés des composants
- **Constantes partagées** : Configuration centralisée

## Points d'entrée principaux

### Pages
- `/` → Configuration et tests système
- `/login` → Authentification
- `/account` → Gestion compte et clés API
- `/preferences` → Configuration trading
- `/trading` → Interface trading IA
- `/dashboard` → Analytics et métriques

### Hooks métier
```typescript
useAuth()              // Authentification
usePreferences()       // Préférences trading
useHyperliquid()       // Hyperliquid DEX
useNotifications()     // Système notifications
useCCXTAnalysis()      // Analyse multi-timeframes
useApiKeyManagement()  // Gestion clés API
```

### API Clients
```typescript
authApi               // Authentification
preferencesApi        // Préférences
claudeApi             // Claude AI
ohlcvApi              // OHLCV/CCXT
hyperliquidTradingApi // Hyperliquid
```

## Technologies utilisées

- **Framework** : Next.js 15 (App Router)
- **Langage** : TypeScript (strict mode)
- **État global** : Zustand avec persistence
- **Formulaires** : React Hook Form + Zod
- **HTTP** : Axios (client centralisé)
- **Styling** : Tailwind CSS
- **Validation** : Zod schemas
