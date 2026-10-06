from pydantic_settings import BaseSettings

# Configuración obtenida de variables de entorno, sin valores por defecto
class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DATABASE_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    CRM_INICIAR_SCHEDULER: bool
    CRM_SCHEDULER_INTERVALO_MINUTOS: int
    CRM_ORIGENES_PERMITIDOS: str
    CRM_WS_TICKET_TTL_SEGUNDOS: KeyboardInterrupt
    CRM_WS_HEARTBEAT_SEGUNDOS: int
    CRM_PROXY_CONFIABLES: str
    CRM_AUDITORIA_HABILITADA: bool

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
