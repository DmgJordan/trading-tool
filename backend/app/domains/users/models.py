"""
Modèles pour le domaine users - Profils utilisateurs et préférences
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey,
    CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ...core import Base


# ========== Enums pour UserTradingPreferences ==========

class RiskTolerance(str, Enum):
    """Tolérance au risque de l'utilisateur"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InvestmentHorizon(str, Enum):
    """Horizon d'investissement de l'utilisateur"""
    SHORT_TERM = "SHORT_TERM"  # < 1 mois
    MEDIUM_TERM = "MEDIUM_TERM"  # 1-12 mois
    LONG_TERM = "LONG_TERM"  # > 1 an


class TradingStyle(str, Enum):
    """Style de trading de l'utilisateur"""
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"


# ========== Modèles ==========

class UserProfile(Base):
    """
    Profil utilisateur avec clés API chiffrées

    ✅ OPTIMISATION : Séparation des préoccupations
    - auth/User : Authentification uniquement
    - users/UserProfile : Profil et clés API
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Clés API (chiffrées avec Fernet)
    hyperliquid_api_key = Column(Text, nullable=True)
    hyperliquid_public_address = Column(String(66), nullable=True)
    anthropic_api_key = Column(Text, nullable=True)
    coingecko_api_key = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id})>"


class UserTradingPreferences(Base):
    """
    Préférences de trading de l'utilisateur

    Migré depuis app/models/user_preferences.py
    """
    __tablename__ = "user_trading_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Préférences de risque et style
    risk_tolerance = Column(
        SQLEnum(RiskTolerance),
        nullable=False,
        default=RiskTolerance.MEDIUM,
        comment="Tolérance au risque de l'utilisateur"
    )

    investment_horizon = Column(
        SQLEnum(InvestmentHorizon),
        nullable=False,
        default=InvestmentHorizon.MEDIUM_TERM,
        comment="Horizon d'investissement préféré"
    )

    trading_style = Column(
        SQLEnum(TradingStyle),
        nullable=False,
        default=TradingStyle.BALANCED,
        comment="Style de trading de l'utilisateur"
    )

    # Paramètres de gestion de position
    max_position_size = Column(
        Float,
        nullable=False,
        default=10.0,
        comment="Taille maximum d'une position en % du portefeuille"
    )

    stop_loss_percentage = Column(
        Float,
        nullable=False,
        default=5.0,
        comment="Pourcentage de stop-loss par défaut"
    )

    take_profit_ratio = Column(
        Float,
        nullable=False,
        default=2.0,
        comment="Ratio risk/reward pour take-profit"
    )

    # Préférences d'actifs et indicateurs (JSON)
    preferred_assets = Column(
        Text,
        nullable=True,
        default='["BTC", "ETH"]',
        comment="Liste JSON des actifs préférés"
    )

    technical_indicators = Column(
        Text,
        nullable=True,
        default='["RSI", "MACD", "SMA"]',
        comment="Liste JSON des indicateurs techniques préférés"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relation avec User (dans auth/)
    user = relationship("User", backref="trading_preferences")

    # Contraintes de validation
    __table_args__ = (
        CheckConstraint(
            'max_position_size > 0 AND max_position_size <= 100',
            name='check_max_position_size_range'
        ),
        CheckConstraint(
            'stop_loss_percentage > 0 AND stop_loss_percentage <= 50',
            name='check_stop_loss_percentage_range'
        ),
        CheckConstraint(
            'take_profit_ratio > 0 AND take_profit_ratio <= 10',
            name='check_take_profit_ratio_range'
        ),
    )

    def __repr__(self):
        return f"<UserTradingPreferences(user_id={self.user_id}, risk_tolerance={self.risk_tolerance})>"
