import psycopg

from psycopg import Connection
from psycopg.rows import dict_row, DictRow
from app.core.config import settings


def obtener_conexion() -> Connection[DictRow]:
    return psycopg.connect(  # type: ignore[arg-type]
        host=settings.DATABASE_HOST,
        port=settings.DB_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        row_factory=dict_row # type: ignore
    )