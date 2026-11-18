from pydantic import field_validator
from pydantic_settings import BaseSettings

# La configuración de la aplicación se obtiene de variables de entorno, con valores por defecto para pruebas locales.
class Settings(BaseSettings):
    # Clave de firma JWT: REQUERIDA y sin valor por defecto. Si la variable de
    # entorno falta, la aplicación no arranca (fail-fast): evita que se firmen
    # tokens con una clave débil o conocida por error de configuración.
    # Generar una nueva con: openssl rand -base64 48 (ver .env.example).
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5

    # Refresh token
    REFRESH_TOKEN_EXPIRE_DIAS: int = 30
    REFRESH_TOKEN_REUSE_GRACE_SEGUNDOS: int = 30

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
    CRM_PROXY_CONFIABLES: str = "127.0.0.1,::1,172.17.0.0/16,172.19.0.0/16"
    # Apaga la captura de eventos de auditoría sin tocar código.
    CRM_AUDITORIA_HABILITADA: bool = True

    @field_validator('ACCESS_TOKEN_SECRET_KEY')
    @classmethod
    def _validar_secreto_jwt(cls, v: str) -> str:
        secreto = v.strip()
        if not secreto:
            raise ValueError('ACCESS_TOKEN_SECRET_KEY no puede estar vacía')
        # Valor que fue el default en versiones anteriores: quedó registrado en el
        # repositorio y se considera público. Jamás debe usarse en ningún entorno.
        if secreto == 'test-secret-key-for-ci':
            raise ValueError(
                'ACCESS_TOKEN_SECRET_KEY no puede usar el valor de prueba conocido '
                "'test-secret-key-for-ci'; genere uno con: openssl rand -base64 48"
            )
        return secreto

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
