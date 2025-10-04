"""Adapters pour les sources de données de marché externes"""

from .ccxt import CCXTAdapter
from .coingecko import CoinGeckoAdapter

__all__ = ["CCXTAdapter", "CoinGeckoAdapter"]
