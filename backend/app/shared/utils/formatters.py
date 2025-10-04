"""
Fonctions de formatage réutilisables pour l'affichage de données financières et techniques
"""

from typing import Union
from datetime import datetime


def round_decimal(value: Union[float, None], decimals: int = 2) -> Union[float, None]:
    """
    Arrondit un nombre décimal avec cohérence

    Args:
        value: Valeur à arrondir (peut être None)
        decimals: Nombre de décimales (défaut: 2)

    Returns:
        Valeur arrondie ou None si value est None

    Examples:
        >>> round_decimal(3.14159, 2)
        3.14
        >>> round_decimal(None, 2)
        None
    """
    if value is None:
        return None
    return round(value, decimals)


def format_price(price: float, currency: str = "USD", decimals: int = 2) -> str:
    """
    Formate un prix avec symbole monétaire et séparateurs

    Args:
        price: Prix à formater
        currency: Code de devise (USD, EUR, etc.)
        decimals: Nombre de décimales

    Returns:
        Prix formaté avec symbole

    Examples:
        >>> format_price(1234.56, "USD", 2)
        "$1,234.56"
        >>> format_price(1234.56, "EUR", 2)
        "€1,234.56"
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "BTC": "₿",
        "ETH": "Ξ"
    }

    symbol = symbols.get(currency, currency)
    formatted_number = format_number(price, decimals, thousands_sep=True)

    return f"{symbol}{formatted_number}"


def format_percentage(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """
    Formate un pourcentage avec signe optionnel

    Args:
        value: Valeur du pourcentage (5.25 pour 5.25%)
        decimals: Nombre de décimales
        show_sign: Afficher le signe + pour les valeurs positives

    Returns:
        Pourcentage formaté

    Examples:
        >>> format_percentage(2.5, 2, True)
        "+2.50%"
        >>> format_percentage(-1.25, 2, True)
        "-1.25%"
        >>> format_percentage(0, 2, False)
        "0.00%"
    """
    rounded = round_decimal(value, decimals)

    if show_sign and rounded > 0:
        return f"+{rounded:.{decimals}f}%"
    else:
        return f"{rounded:.{decimals}f}%"


def format_volume(volume: float, short_format: bool = True) -> str:
    """
    Formate un volume (grand nombre) avec abréviations optionnelles

    Args:
        volume: Volume à formater
        short_format: Utiliser abréviations (K, M, B)

    Returns:
        Volume formaté

    Examples:
        >>> format_volume(1500000, True)
        "1.5M"
        >>> format_volume(234500, True)
        "234.5K"
        >>> format_volume(1234567, False)
        "1,234,567"
    """
    if not short_format:
        return format_number(volume, decimals=0, thousands_sep=True)

    # Formats courts avec abréviations
    if volume >= 1_000_000_000:
        return f"{round_decimal(volume / 1_000_000_000, 1)}B"
    elif volume >= 1_000_000:
        return f"{round_decimal(volume / 1_000_000, 1)}M"
    elif volume >= 1_000:
        return f"{round_decimal(volume / 1_000, 1)}K"
    else:
        return f"{round_decimal(volume, 0)}"


def format_number(value: float, decimals: int = 2, thousands_sep: bool = True) -> str:
    """
    Formate un nombre avec séparateurs de milliers optionnels

    Args:
        value: Nombre à formater
        decimals: Nombre de décimales
        thousands_sep: Utiliser séparateurs de milliers

    Returns:
        Nombre formaté

    Examples:
        >>> format_number(1234.56, 2, True)
        "1,234.56"
        >>> format_number(1234.56, 2, False)
        "1234.56"
        >>> format_number(1234, 0, True)
        "1,234"
    """
    if thousands_sep:
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:.{decimals}f}"


def format_timestamp(timestamp: datetime, format_type: str = "iso") -> str:
    """
    Formate un timestamp selon différents formats

    Args:
        timestamp: Timestamp à formater
        format_type: Type de format ("iso", "human", "short")

    Returns:
        Timestamp formaté

    Examples:
        >>> dt = datetime(2024, 1, 15, 10, 30, 0)
        >>> format_timestamp(dt, "iso")
        "2024-01-15T10:30:00"
        >>> format_timestamp(dt, "human")
        "15 Jan 2024 10:30"
        >>> format_timestamp(dt, "short")
        "15/01/24"
    """
    format_map = {
        "iso": "%Y-%m-%dT%H:%M:%S",
        "human": "%d %b %Y %H:%M",
        "short": "%d/%m/%y",
        "date": "%Y-%m-%d",
        "time": "%H:%M:%S"
    }

    format_string = format_map.get(format_type, "%Y-%m-%dT%H:%M:%S")
    return timestamp.strftime(format_string)


def format_change(current: float, previous: float, as_percentage: bool = True, decimals: int = 2) -> str:
    """
    Calcule et formate un changement de valeur

    Args:
        current: Valeur actuelle
        previous: Valeur précédente
        as_percentage: Formater en pourcentage
        decimals: Nombre de décimales

    Returns:
        Changement formaté avec signe

    Examples:
        >>> format_change(105, 100, True, 2)
        "+5.00%"
        >>> format_change(95, 100, True, 2)
        "-5.00%"
        >>> format_change(105, 100, False, 2)
        "+5.00"
    """
    if previous == 0:
        return "N/A"

    if as_percentage:
        change_percent = ((current - previous) / previous) * 100
        return format_percentage(change_percent, decimals, show_sign=True)
    else:
        change_abs = current - previous
        rounded = round_decimal(change_abs, decimals)

        if rounded > 0:
            return f"+{rounded:.{decimals}f}"
        else:
            return f"{rounded:.{decimals}f}"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Tronque une chaîne avec ellipse si trop longue

    Args:
        text: Texte à tronquer
        max_length: Longueur maximale (incluant suffix)
        suffix: Suffixe à ajouter (défaut: "...")

    Returns:
        Texte tronqué si nécessaire

    Examples:
        >>> truncate_string("This is a very long text", 10, "...")
        "This is..."
        >>> truncate_string("Short", 10, "...")
        "Short"
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
