from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, get_db
from .models import Base
from .routes import users, auth, connectors, market_data, user_preferences, ai_recommendations, claude

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

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(connectors.router)
app.include_router(market_data.router)
app.include_router(user_preferences.router)
app.include_router(ai_recommendations.router)
app.include_router(claude.router)

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