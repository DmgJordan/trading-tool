"""
Fonctions de validation pour les clés API et autres données
"""

from typing import Dict, Any


def validate_api_key_format(key: str, api_type: str) -> Dict[str, Any]:
    """
    Valide le format d'une clé API sans tester la connexion

    Args:
        key: Clé API à valider
        api_type: Type d'API (anthropic, openai, coingecko, hyperliquid)

    Returns:
        Dictionnaire avec le résultat de la validation
        {
            "is_valid": bool,
            "message": str,
            "api_type": str
        }

    Examples:
        >>> validate_api_key_format("sk-ant-123456789", "anthropic")
        {"is_valid": True, "message": "Format valide", "api_type": "anthropic"}

        >>> validate_api_key_format("invalid", "anthropic")
        {"is_valid": False, "message": "Clé doit commencer par 'sk-ant-'", ...}
    """
    api_type_lower = api_type.lower()

    # Configuration des règles de validation par type d'API
    validation_rules = {
        "anthropic": {
            "prefix": "sk-ant-",
            "min_length": 20,
            "name": "Anthropic"
        },
        "openai": {
            "prefix": "sk-",
            "min_length": 20,
            "name": "OpenAI"
        },
        "coingecko": {
            "prefix": "CG-",
            "min_length": 10,
            "name": "CoinGecko"
        },
        "hyperliquid": {
            "prefix": "0x",
            "min_length": 42,  # Ethereum address length
            "name": "Hyperliquid"
        }
    }

    # Vérifier si le type d'API est supporté
    if api_type_lower not in validation_rules:
        return {
            "is_valid": False,
            "message": f"Type d'API non supporté: {api_type}. Types supportés: {', '.join(validation_rules.keys())}",
            "api_type": api_type
        }

    rules = validation_rules[api_type_lower]

    # Validation du préfixe
    if not key.startswith(rules["prefix"]):
        return {
            "is_valid": False,
            "message": f"Clé API {rules['name']} doit commencer par '{rules['prefix']}'",
            "api_type": api_type
        }

    # Validation de la longueur
    if len(key) < rules["min_length"]:
        return {
            "is_valid": False,
            "message": f"Clé API {rules['name']} trop courte (minimum {rules['min_length']} caractères)",
            "api_type": api_type
        }

    # Validation réussie
    return {
        "is_valid": True,
        "message": f"Format de clé API {rules['name']} valide",
        "api_type": api_type
    }


def validate_symbol_format(symbol: str) -> Dict[str, Any]:
    """
    Valide le format d'un symbole de trading

    Args:
        symbol: Symbole à valider (ex: "BTC/USDT", "BTC-USDT", "BTCUSDT")

    Returns:
        Dictionnaire avec le résultat de la validation

    Examples:
        >>> validate_symbol_format("BTC/USDT")
        {"is_valid": True, "message": "Format valide", "normalized": "BTC/USDT"}

        >>> validate_symbol_format("")
        {"is_valid": False, "message": "Symbole vide", "normalized": None}
    """
    if not symbol or len(symbol.strip()) == 0:
        return {
            "is_valid": False,
            "message": "Symbole vide",
            "normalized": None
        }

    # Nettoyer le symbole
    symbol_clean = symbol.strip().upper()

    # Vérifier longueur minimale
    if len(symbol_clean) < 3:
        return {
            "is_valid": False,
            "message": "Symbole trop court (minimum 3 caractères)",
            "normalized": None
        }

    # Vérifier caractères autorisés (lettres, chiffres, /, -)
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-")
    if not all(c in allowed_chars for c in symbol_clean):
        return {
            "is_valid": False,
            "message": "Symbole contient des caractères non autorisés",
            "normalized": None
        }

    # Normaliser le format (préférer "/" comme séparateur)
    if "-" in symbol_clean and "/" not in symbol_clean:
        normalized = symbol_clean.replace("-", "/")
    else:
        normalized = symbol_clean

    return {
        "is_valid": True,
        "message": "Format de symbole valide",
        "normalized": normalized
    }


def validate_timeframe(timeframe: str) -> Dict[str, Any]:
    """
    Valide un timeframe de trading

    Args:
        timeframe: Timeframe à valider (ex: "1m", "5m", "1h", "1d")

    Returns:
        Dictionnaire avec le résultat de la validation

    Examples:
        >>> validate_timeframe("1h")
        {"is_valid": True, "message": "Timeframe valide", "normalized": "1h"}

        >>> validate_timeframe("99z")
        {"is_valid": False, "message": "Format invalide", "normalized": None}
    """
    if not timeframe:
        return {
            "is_valid": False,
            "message": "Timeframe vide",
            "normalized": None
        }

    # Timeframes standards supportés
    valid_timeframes = {
        "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "8h", "12h",
        "1d", "3d", "1w", "1M"
    }

    timeframe_clean = timeframe.strip()

    if timeframe_clean in valid_timeframes:
        return {
            "is_valid": True,
            "message": "Timeframe valide",
            "normalized": timeframe_clean
        }
    else:
        return {
            "is_valid": False,
            "message": f"Timeframe non supporté. Timeframes valides: {', '.join(sorted(valid_timeframes))}",
            "normalized": None
        }
