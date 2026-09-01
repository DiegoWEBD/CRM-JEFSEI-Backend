from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings


def crear_token_mock(
    rut: str = "12345678-9",
    nombre: str = "Juan Pérez",
    codigo_roles: list[str] | None = None,
    nombre_roles: list[str] | None = None,
    codigo_permisos: list[str] | None = None,
    exp_minutes: int = 60,
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
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM,
    )


def headers_auth(token: str) -> dict:
    return {"Cookie": f"token={token}"}
