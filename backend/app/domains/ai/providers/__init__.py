"""
Providers IA - Abstraction multi-providers

Contient l'interface AIProvider et les implémentations pour différents providers.
"""

from .base import AIProvider
from .anthropic import AnthropicProvider

__all__ = ["AIProvider", "AnthropicProvider"]
