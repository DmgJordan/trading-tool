# Modèles migrés vers domains/ (architecture DDD)
from ..domains.auth.models import User
from ..domains.users.models import UserProfile, UserTradingPreferences

# Modèles restants dans models/
from .market_data import MarketData
from .ai_recommendations import AIRecommendation
from ..core import Base