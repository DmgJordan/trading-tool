from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_encryption_key():
    key = settings.encryption_key.encode()
    if len(key) != 32:
        key = base64.urlsafe_b64encode(key.ljust(32)[:32])
    else:
        key = base64.urlsafe_b64encode(key)
    return key

cipher_suite = Fernet(get_encryption_key())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def encrypt_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    import logging
    logger = logging.getLogger(__name__)

    if not encrypted_api_key:
        return ""

    try:
        decrypted_bytes = cipher_suite.decrypt(encrypted_api_key.encode())
        decrypted = decrypted_bytes.decode('utf-8')

        # Verifier que le resultat est ASCII valide
        decrypted.encode('ascii')
        return decrypted

    except UnicodeDecodeError:
        # Fallback si probleme de decodage UTF-8
        decrypted_bytes = cipher_suite.decrypt(encrypted_api_key.encode())
        return decrypted_bytes.decode('utf-8', errors='ignore')

    except UnicodeEncodeError:
        # La cle contient des caracteres non-ASCII - traiter comme hex
        decrypted = cipher_suite.decrypt(encrypted_api_key.encode()).decode('utf-8')

        # Si hex pur, retourner tel quel
        if all(c in '0123456789abcdefABCDEF' for c in decrypted):
            return decrypted

        # Sinon convertir chaque caractere en hex
        hex_key = ''.join(f"{ord(char):02x}" for char in decrypted)
        logger.info(f"decrypt_api_key: Conversion Unicode->hex effectuee (longueur: {len(hex_key)})")
        return hex_key

    except Exception as e:
        logger.error(f"decrypt_api_key: Erreur dechiffrement - {type(e).__name__}: {e}")
        return ""

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    from .exceptions import UnauthorizedException

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id: int = payload.get("sub")
        token_type_from_payload: str = payload.get("type")

        if user_id is None or token_type_from_payload != token_type:
            raise UnauthorizedException("Could not validate credentials")

        return {"user_id": user_id, "exp": payload.get("exp")}
    except Exception:
        raise UnauthorizedException("Could not validate credentials")

def authenticate_user(db: Session, email: str, password: str):
    from ..models.user import User

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
