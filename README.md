# Trading Tool

Une application de trading complète avec interface web moderne et API backend robuste, intégrant les plateformes Hyperliquid et l'API Anthropic.

## 🏗️ Architecture

**Type d'application** : Tool de trading avec interface web Next.js et API FastAPI

**Structure monorepo** :
- `frontend/` : Application Next.js 15 avec TypeScript et Tailwind CSS
- `backend/` : API FastAPI avec SQLAlchemy et PostgreSQL

### Architecture Backend
- **FastAPI** : Framework web moderne pour l'API REST
- **SQLAlchemy** : ORM avec migrations Alembic
- **PostgreSQL** : Base de données relationnelle
- **Authentification JWT** : Système d'utilisateurs sécurisé
- **Chiffrement AES** : Protection des clés API utilisateur

### Architecture Frontend
- **Next.js 15** : Framework React avec App Router
- **TypeScript** : Typage strict activé
- **Zustand** : Gestion d'état global
- **React Hook Form + Zod** : Gestion et validation des formulaires
- **Tailwind CSS** : Styling avec thème cohérent

## ✨ Fonctionnalités Disponibles

### 🔐 Système d'Authentification
- **Inscription utilisateur** avec email, nom d'utilisateur et mot de passe
- **Connexion sécurisée** avec tokens JWT (access + refresh)
- **Gestion de session** persistante
- **Déconnexion** avec invalidation des tokens
- **Protection des routes** automatique

### 👤 Gestion de Compte
- **Profil utilisateur** avec informations personnelles
- **Configuration sécurisée des clés API** :
  - Clés Hyperliquid (clés privées)
  - Clés Anthropic API
- **Chiffrement automatique** des clés en base de données
- **Affichage masqué** des clés configurées pour la sécurité

### 🔌 Connecteurs et Tests d'API
- **Validation de format** des clés API avant sauvegarde
- **Tests de connexion en temps réel** :
  - API Anthropic : vérification de validité et quotas
  - Hyperliquid DEX : test de connexion mainnet/testnet
- **Tests avec clés stockées** : test des clés déjà configurées
- **Gestion d'erreurs détaillée** avec messages utilisateur clairs

### 🏥 Monitoring et Diagnostics
- **Tests de santé système** :
  - Connexion backend FastAPI
  - Connexion base de données PostgreSQL
- **Interface de diagnostic** temps réel
- **Tests de configuration globaux**

### 🖼️ Interface Utilisateur
- **Design moderne** avec Tailwind CSS
- **Navigation responsive** avec menu mobile
- **Pages principales** :
  - Page d'accueil avec tests de configuration
  - Page de connexion/inscription
  - Page de gestion de compte
- **Composants réutilisables** :
  - Configuration des clés API
  - Tests de connecteurs
  - Barre de navigation

### 📊 Système de Base de Données
- **Modèle utilisateur complet** :
  - Informations de base (email, username, password hashé)
  - Clés API chiffrées
  - Timestamps de création/modification
- **Migrations Alembic** pour l'évolution du schéma
- **Relations et contraintes** définies

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- Node.js 16+
- PostgreSQL
- Docker (optionnel)

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
npm run dev
```

### Base de Données
```bash
cd backend
docker-compose up -d postgres  # Démarrer PostgreSQL
alembic upgrade head           # Appliquer les migrations
```

## 📋 Configuration

### Variables d'Environnement Backend
Créer un fichier `backend/.env` :
```env
DATABASE_URL=postgresql://user:password@localhost/trading_tool
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-32-char-encryption-key
```

### Variables d'Environnement Frontend
Créer un fichier `frontend/.env.local` :
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎯 État Actuel et Limitations

### ✅ Fonctionnalités Opérationnelles
- Système d'authentification complet
- Gestion sécurisée des clés API
- Tests de connecteurs Anthropic et Hyperliquid
- Interface utilisateur moderne et responsive
- Configuration et diagnostics système

### ⏳ Fonctionnalités à Développer
- **Dashboard de trading** (non implémenté)
- **Module de trading actif** (non implémenté)
- **Historique des transactions** (non implémenté)
- **Algorithmes de trading automatisé** (non implémenté)
- **Graphiques et analytics** (non implémenté)

### 🔧 API Endpoints Disponibles

#### Authentification (`/auth`)
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion
- `POST /auth/refresh` - Rafraîchissement token
- `GET /auth/me` - Profil utilisateur
- `POST /auth/logout` - Déconnexion

#### Utilisateurs (`/users`)
- `GET /users/me` - Informations utilisateur
- `PUT /users/me` - Mise à jour profil
- `PUT /users/me/api-keys` - Configuration clés API

#### Connecteurs (`/connectors`)
- `POST /connectors/test-anthropic` - Test API Anthropic
- `POST /connectors/test-hyperliquid` - Test API Hyperliquid
- `POST /connectors/test-anthropic-stored` - Test clé Anthropic stockée
- `POST /connectors/test-hyperliquid-stored` - Test clé Hyperliquid stockée
- `POST /connectors/validate-key-format` - Validation format clé
- `GET /connectors/supported-services` - Services supportés

#### Santé Système
- `GET /health` - Santé backend
- `GET /db-health` - Santé base de données

## 🛠️ Commandes de Développement

### Backend
```bash
cd backend
uvicorn app.main:app --reload     # Développement
alembic revision --autogenerate -m "message"  # Nouvelle migration
alembic upgrade head              # Appliquer migrations
```

### Frontend
```bash
cd frontend
npm run dev          # Développement
npm run build        # Build production
npm run lint         # Vérification ESLint
npm run type-check   # Vérification TypeScript
```

## 🔒 Sécurité

- **Mots de passe** : Hashage bcrypt
- **Tokens JWT** : Expiration configurée
- **Clés API** : Chiffrement AES-256 en base
- **CORS** : Configuration sécurisée
- **Validation** : Schémas Pydantic/Zod stricts

---

Cette application constitue une base solide pour un outil de trading, avec l'infrastructure d'authentification, de gestion des comptes et de connecteurs prête pour l'intégration de fonctionnalités de trading avancées.
