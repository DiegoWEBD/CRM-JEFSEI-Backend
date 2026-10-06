from pydantic_settings import BaseSettings

# Configuración obtenida de variables de entorno, sin valores por defecto
class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET_KEY: str = 'test_secret_key'
    ACCESS_TOKEN_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    DATABASE_HOST: str = 'localhost'
    DB_PORT: int = 5432
    POSTGRES_DB: str = 'test-db'
    POSTGRES_USER: str = 'test-user'
    POSTGRES_PASSWORD: str = 'test-password'

    CRM_INICIAR_SCHEDULER: bool = True
    CRM_SCHEDULER_INTERVALO_MINUTOS: int = 1
    CRM_ORIGENES_PERMITIDOS: str = 'test-origin'
    CRM_WS_TICKET_TTL_SEGUNDOS: int = 60
    CRM_WS_HEARTBEAT_SEGUNDOS: int = 30
    CRM_PROXY_CONFIABLES: str = '127.0.0.1,::1'
    CRM_AUDITORIA_HABILITADA: bool = True

    class Config:
        env_file = ".env"
        extra="ignore"

    @property
    def origenes_permitidos(self) -> list[str]:
        return [origen.strip() for origen in self.CRM_ORIGENES_PERMITIDOS.split(',') if origen.strip()]

    @property
    def proxies_confiables(self) -> list[str]:
        return [proxy.strip() for proxy in self.CRM_PROXY_CONFIABLES.split(',') if proxy.strip()]

settings = Settings() # type: ignore
