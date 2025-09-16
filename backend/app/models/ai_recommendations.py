from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..database import Base

class ActionType(Enum):
    """Types d'actions de trading"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class RiskLevel(Enum):
    """Niveaux de risque des recommandations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AIRecommendation(Base):
    """Modèle pour stocker les recommandations d'IA de trading"""
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Recommandation principale
    action = Column(String(10), nullable=False)  # buy, sell, hold
    symbol = Column(String(50), nullable=False, index=True)  # ex: "BTC", "ETH"
    confidence = Column(Integer, nullable=False)  # 0-100

    # Paramètres de position
    size_percentage = Column(Float, nullable=False)  # % du portefeuille
    entry_price = Column(Float, nullable=True)  # Prix d'entrée suggéré

    # Gestion du risque
    stop_loss = Column(Float, nullable=True)  # Prix stop-loss
    take_profit1 = Column(Float, nullable=True)  # Premier niveau de profit
    take_profit2 = Column(Float, nullable=True)  # Deuxième niveau de profit
    take_profit3 = Column(Float, nullable=True)  # Troisième niveau de profit

    # Métadonnées
    reasoning = Column(Text, nullable=True)  # Explication de l'IA
    risk_level = Column(String(10), nullable=False)  # low, medium, high

    # Contexte de génération
    market_data_timestamp = Column(DateTime(timezone=True), nullable=True)  # Timestamp des données utilisées
    prompt_hash = Column(String(64), nullable=True)  # Hash du prompt pour éviter les doublons
    model_used = Column(String(100), nullable=True)  # Modèle Claude utilisé

    # Suivi de performance (à implémenter plus tard)
    actual_outcome = Column(String(50), nullable=True)  # "profit", "loss", "neutral"
    actual_return = Column(Float, nullable=True)  # Rendement réel en %

    # Relations
    user = relationship("User", back_populates="ai_recommendations")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Index composés pour optimiser les requêtes
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_symbol_created', 'symbol', 'created_at'),
        Index('idx_user_symbol', 'user_id', 'symbol'),
        Index('idx_action_created', 'action', 'created_at'),
    )

    def __repr__(self):
        return f"<AIRecommendation(user_id={self.user_id}, action={self.action.value}, symbol={self.symbol}, confidence={self.confidence})>"