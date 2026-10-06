from pydantic_settings import BaseSettings

# La configuración de la aplicación se obtiene de variables de entorno, con valores por defecto para pruebas locales.
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
    CRM_SCHEDULER_INTERVALO_MINUTOS: int = 5

    # WebSocket de notificaciones
    # Los navegadores NO aplican CORS al handshake de un WebSocket: el origen se
    # valida manualmente contra esta lista (ver ws_router).
    CRM_ORIGENES_PERMITIDOS: str = "http://localhost:3000"
    # Vida útil del ticket que autoriza la conexión (no es el JWT de sesión).
    CRM_WS_TICKET_TTL_SEGUNDOS: int = 60
    # El servidor emite "ping" con esta periodicidad para mantener viva la conexión
    # y detectar cortes (un envío fallido dispara la reconexión del cliente).
    CRM_WS_HEARTBEAT_SEGUNDOS: int = 30

    # Auditoría
    # Solo estos peers directos pueden fijar X-Forwarded-For / X-Real-IP; desde
    # cualquier otro origen los headers se ignoran (anti-spoofing de IP).
    CRM_PROXY_CONFIABLES: str = "127.0.0.1,::1"
    # Apaga la captura de eventos de auditoría sin tocar código.
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
