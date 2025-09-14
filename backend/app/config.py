from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/trading_db"
    secret_key: str = "your-secret-key-here"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()