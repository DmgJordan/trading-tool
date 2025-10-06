"""
Modèles pour le domaine auth - Authentification uniquement
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...core import Base


class User(Base):
    """
    Modèle User - Authentification uniquement

    Ce modèle contient uniquement les informations nécessaires à l'authentification.
    Les informations de profil (clés API, préférences) sont dans users/models.py
    """
    __tablename__ = "users"

    # Identité
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)

    # Authentification
    hashed_password = Column(String, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations (définie ici, mais les modèles cibles sont dans users/ et ai_profile/)
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ai_profile = relationship("AIProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
