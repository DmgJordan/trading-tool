from typing import Generator
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import SessionLocal
from .security import verify_token
from .exceptions import UnauthorizedException, NotFoundException

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dépendance pour obtenir l'utilisateur actuellement authentifié"""
    from ..models.user import User

    token = credentials.credentials
    token_data = verify_token(token, "access")

    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None:
        raise NotFoundException("User not found")

    return user
