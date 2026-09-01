from datetime import datetime, timedelta, timezone
from jose import jwt


def crear_token_mock(
    rut: str = "12345678-9",
    nombre: str = "Juan Pérez",
    codigo_roles: list[str] | None = None,
    nombre_roles: list[str] | None = None,
    codigo_permisos: list[str] | None = None,
    exp_minutes: int = 60,
    secret_key: str = "test-secret-key-for-mocks",
    algorithm: str = "HS256",
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
        "exp": datetime.now(timezone.utc) + timedelta(minutes=exp_minutes),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def headers_auth(token: str) -> dict:
    return {"Cookie": f"token={token}"}
