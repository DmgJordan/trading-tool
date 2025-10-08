from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import logging
import sys
import time
from .core import engine, get_db, Base
from .domains import auth_router, users_router
from .domains.market import router as market_router
from .domains.trading import router as trading_router
from .domains import ai, ai_profile
# DÉPRÉCIÉ - from .routes import connectors  # Migré vers domains/users/
# DÉPRÉCIÉ - from .routes import ai_recommendations, claude  # Migrés vers domains/ai/

# Configuration du logging pour afficher dans le terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Afficher dans le terminal
    ]
)

# Logger pour l'application principale
logger = logging.getLogger(__name__)

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trading Tool API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.21:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nouveaux routers depuis domains/ (architecture DDD)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(market_router)
app.include_router(trading_router)
app.include_router(ai.router)  # Nouveau : Infrastructure IA multi-providers
app.include_router(ai_profile.router)  # Nouveau : Configuration IA utilisateur

# Routers existants depuis routes/ (à migrer/déprécier progressivement)
# app.include_router(connectors.router)  # DÉPRÉCIÉ : migré vers domains/users/
# app.include_router(ai_recommendations.router)  # DÉPRÉCIÉ : migré vers domains/ai/
# app.include_router(claude.router)  # DÉPRÉCIÉ : migré vers domains/ai/

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Trading Tool"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-health")
async def db_health_check():
    try:
        db = next(get_db())
        # Test simple de connexion à la base de données
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}