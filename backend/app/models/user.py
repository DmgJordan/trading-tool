from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Clés API
    hyperliquid_api_key = Column(Text, nullable=True)
    hyperliquid_public_address = Column(String(66), nullable=True)
    anthropic_api_key = Column(Text, nullable=True)
    coingecko_api_key = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    trading_preferences = relationship("UserTradingPreferences", back_populates="user", uselist=False)
    ai_recommendations = relationship("AIRecommendation", back_populates="user")
