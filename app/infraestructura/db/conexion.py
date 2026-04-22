import psycopg
from psycopg.rows import dict_row
from app.core.config import settings

def obtener_conexion():
    return psycopg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DB_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        row_factory=dict_row
    )