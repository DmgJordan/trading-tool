"""
Module shared - Fonctions pures réutilisables
Contient les indicateurs techniques et utilitaires sans dépendances externes
"""

# Indicateurs RSI
from .indicators.rsi import (
    calculate_rsi,
    get_rsi_interpretation,
    get_rsi_signal
)

# Indicateurs Moving Averages
from .indicators.moving_average import (
    calculate_sma,
    calculate_multiple_sma,
    get_ma_trend,
    detect_ma_crossover
)

# Indicateurs ATR
from .indicators.atr import (
    calculate_atr,
    get_atr_interpretation,
    get_atr_signal
)

# Indicateurs Volume
from .indicators.volume import (
    analyze_volume,
    get_volume_interpretation,
    get_volume_signal,
    detect_volume_trend
)

# Indicateurs Support/Resistance
from .indicators.support_resistance import (
    PivotPoint,
    SupportResistanceLevel,
    identify_pivot_points,
    group_pivots_into_levels,
    calculate_confidence_scores,
    filter_significant_levels,
    detect_levels,
    get_nearest_levels
)

# Utilitaires de validation
from .utils.validators import (
    validate_api_key_format,
    validate_symbol_format,
    validate_timeframe
)

# Utilitaires de formatage
from .utils.formatters import (
    round_decimal,
    format_price,
    format_percentage,
    format_volume,
    format_number,
    format_timestamp,
    format_change,
    truncate_string
)

__all__ = [
    # RSI
    "calculate_rsi",
    "get_rsi_interpretation",
    "get_rsi_signal",
    # Moving Averages
    "calculate_sma",
    "calculate_multiple_sma",
    "get_ma_trend",
    "detect_ma_crossover",
    # ATR
    "calculate_atr",
    "get_atr_interpretation",
    "get_atr_signal",
    # Volume
    "analyze_volume",
    "get_volume_interpretation",
    "get_volume_signal",
    "detect_volume_trend",
    # Support/Resistance
    "PivotPoint",
    "SupportResistanceLevel",
    "identify_pivot_points",
    "group_pivots_into_levels",
    "calculate_confidence_scores",
    "filter_significant_levels",
    "detect_levels",
    "get_nearest_levels",
    # Validators
    "validate_api_key_format",
    "validate_symbol_format",
    "validate_timeframe",
    # Formatters
    "round_decimal",
    "format_price",
    "format_percentage",
    "format_volume",
    "format_number",
    "format_timestamp",
    "format_change",
    "truncate_string",
]
