# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET_KEY: str = "test-secret-key-for-ci"
    ACCESS_TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_HOST: str = "localhost"
    DB_PORT: int = 5432
    POSTGRES_DB: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"

    CRM_INICIAR_SCHEDULER: bool = True
    CRM_SCHEDULER_INTERVALO_MINUTOS: int = 360

    class Config:
        env_file = ".env"
        extra="ignore"

settings = Settings() # type: ignore