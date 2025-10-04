# Modèles migrés vers domains/ (architecture DDD)
from ..domains.auth.models import User
from ..domains.users.models import UserProfile, UserTradingPreferences
from ..domains.market.models import MarketData

# Modèles restants dans models/
from .ai_recommendations import AIRecommendation
from ..core import Base