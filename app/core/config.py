# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET_KEY: str = "test-secret-key-for-ci"
    ACCESS_TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Vida útil del refresh token. 30 días es el valor habitual de la industria
    # (Auth0, Firebase, Okta) y se renueva de forma deslizante en cada rotación.
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200
    # Ventana en la que un refresh token ya usado se considera una rotación
    # duplicada legítima y no un robo. El BFF dispara peticiones en paralelo
    # (prefetch SSR + react-query), así que sin esta gracia una sesión válida
    # se revocaría sola.
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
    CRM_ORIGENES_PERMITIDOS: str = "http://localhost:3000,http://localhost:3001"
    # Vida útil del ticket que autoriza la conexión (no es el JWT de sesión).
    CRM_WS_TICKET_TTL_SEGUNDOS: int = 60
    # El servidor emite "ping" con esta periodicidad para mantener viva la conexión
    # y detectar cortes (un envío fallido dispara la reconexión del cliente).
    CRM_WS_HEARTBEAT_SEGUNDOS: int = 30

<<<<<<< HEAD
    # Auditoría
    # Solo estos peers directos pueden fijar X-Forwarded-For / X-Real-IP; desde
    # cualquier otro origen los headers se ignoran (anti-spoofing de IP).
    CRM_PROXY_CONFIABLES: str = "127.0.0.1,::1"
    # Apaga la captura de eventos de auditoría sin tocar código.
    CRM_AUDITORIA_HABILITADA: bool = True
=======
    # --- Sistema de auditoría -------------------------------------------------
    # Interruptor maestro. En false el servicio de auditoría no escribe nada,
    # útil para levantar la API en una DB donde todavía no existe la tabla.
    AUDIT_ENABLED: bool = True
    # Sólo los eventos marcados como sensibles se consultan (§37): los GET
    # comunes no se registran salvo que este interruptor esté en true.
    AUDIT_LOG_READ_EVENTS: bool = False
    AUDIT_STORE_USER_AGENT: bool = True
    AUDIT_STORE_DEVICE_METADATA: bool = True
    # Retención configurable. No se borra nada automáticamente: la aplicación no
    # tiene DELETE sobre auditoria_evento. Sirve para el job de purga future.
    AUDIT_RETENTION_DAYS: int = 730
    # Cabecera de correlación NGINX -> Next.js -> FastAPI -> PostgreSQL.
    AUDIT_REQUEST_ID_HEADER: str = "X-Request-ID"
    # Tope del JSONB de datos_antes/datos_despues para no degradar el insert
    # con snapshots enormes. Por encima se guarda truncado y se marca en metadata.
    AUDIT_MAX_SNAPSHOT_BYTES: int = 65536
    # Lista de proxies de confianza (CSV de IPs o CIDR). Vacío = ninguno, que es
    # el caso en local: entonces se usa request.client.host y se descarta
    # X-Forwarded-For por completo. En el VPS se declara el NGINX acá.
    AUDIT_TRUSTED_PROXIES: str = ""
>>>>>>> 36f98507cb018c0391d9351dfaa77453fbbbe47b

    class Config:
        env_file = ".env"
        extra="ignore"

    @property
    def origenes_permitidos(self) -> list[str]:
        return [origen.strip() for origen in self.CRM_ORIGENES_PERMITIDOS.split(',') if origen.strip()]

    @property
<<<<<<< HEAD
    def proxies_confiables(self) -> list[str]:
        return [proxy.strip() for proxy in self.CRM_PROXY_CONFIABLES.split(',') if proxy.strip()]
=======
    def proxies_auditoria_confiables(self) -> list[str]:
        return [p.strip() for p in self.AUDIT_TRUSTED_PROXIES.split(',') if p.strip()]
>>>>>>> 36f98507cb018c0391d9351dfaa77453fbbbe47b

settings = Settings() # type: ignore
