from datetime import datetime, timedelta, timezone
from jose import jwt

# jti por defecto. get_current_user exige que el token apunte a una sesión viva,
# así que el token de test tiene que llevar uno.
JTI_MOCK = "11111111-2222-3333-4444-555555555555"


def crear_token_mock(
    rut: str = "12345678-9",
    nombre: str = "Juan Pérez",
    codigo_roles: list[str] | None = None,
    nombre_roles: list[str] | None = None,
    codigo_permisos: list[str] | None = None,
    exp_minutes: int = 60,
    secret_key: str = "test-secret-key-for-mocks",
    algorithm: str = "HS256",
    jti: str | None = JTI_MOCK,
) -> str:
    if codigo_roles is None:
        codigo_roles = ["ADMIN"]
    if nombre_roles is None:
        nombre_roles = ["Administrador"]
    if codigo_permisos is None:
        codigo_permisos = [
            "VER_USUARIOS",
            "REGISTRAR_USUARIOS",
            "ADMINISTRAR_USUARIOS",
            "VER_METRICAS_GERENCIA",
            "VER_METRICAS_EJECUTIVO",
        ]

    payload = {
        "rut": rut,
        "nombre": nombre,
        "codigo_roles": codigo_roles,
        "nombre_roles": nombre_roles,
        "codigo_permisos": codigo_permisos,
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=exp_minutes),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def headers_auth(token: str) -> dict:
    return {"Cookie": f"token={token}"}


def sesion_viva(id_sesion: str = JTI_MOCK, rut_usuario: str = "12345678-9"):
    """Sesión en estado válido, con expiración lejana."""
    from app.dominio.auditoria.sesion import Sesion

    return Sesion(
        id=id_sesion,
        rut_usuario=rut_usuario,
        fecha_creacion=datetime.now(timezone.utc),
        fecha_expiracion=datetime.now(timezone.utc) + timedelta(days=30),
    )
