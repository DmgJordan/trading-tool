from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.sql import func
from ..core import Base

class MarketData(Base):
    """Modèle pour stocker l'historique des données de marché"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)

    # Informations du symbole
    symbol = Column(String(50), nullable=False, index=True)  # ex: "BTC", "ETH"
    name = Column(String(200), nullable=True)  # ex: "Bitcoin", "Ethereum"

    # Données de prix
    price_usd = Column(Float, nullable=False)
    price_change_24h = Column(Float, nullable=True)  # Changement en %
    price_change_24h_abs = Column(Float, nullable=True)  # Changement absolu

    # Données de volume et market cap
    volume_24h_usd = Column(Float, nullable=True)
    market_cap_usd = Column(Float, nullable=True)

    # Source des données
    source = Column(String(50), nullable=False)  # "coingecko", "hyperliquid"
    source_id = Column(String(100), nullable=True)  # ID source spécifique (ex: coin_id CoinGecko)

    # Métadonnées
    raw_data = Column(Text, nullable=True)  # JSON des données brutes pour debug

    # Timestamps
    data_timestamp = Column(DateTime(timezone=True), nullable=False)  # Timestamp des données
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Index composé pour optimiser les requêtes par symbole et timestamp
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'data_timestamp'),
        Index('idx_source_timestamp', 'source', 'data_timestamp'),
        Index('idx_symbol_source', 'symbol', 'source'),
    )