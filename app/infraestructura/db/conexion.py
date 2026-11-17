import atexit
import threading
from contextlib import AbstractContextManager

from psycopg import Connection
from psycopg.rows import dict_row, DictRow
from psycopg_pool import ConnectionPool
from app.core.config import settings

# Pool de conexiones compartido por la aplicación: reemplaza el
# `psycopg.connect` por consulta (handshake TCP + auth en cada llamada).
# Se crea de forma perezosa en el primer uso para no exigir la base de
# datos al importar el módulo (tests unitarios, arranques parciales).
_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()


def _obtener_pool() -> ConnectionPool:
    global _pool

    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ConnectionPool(
                    conninfo='',
                    kwargs={
                        'host': settings.DATABASE_HOST,
                        'port': settings.DB_PORT,
                        'dbname': settings.POSTGRES_DB,
                        'user': settings.POSTGRES_USER,
                        'password': settings.POSTGRES_PASSWORD,
                        'row_factory': dict_row,  # type: ignore[arg-type]
                    },
                    min_size=1,
                    max_size=10,
                )

    return _pool


# Cierra el pool si el intérprete termina sin pasar por el lifespan de la
# aplicación (scripts, REPL). En la app el cierre lo hace `cerrar_pool()`.
atexit.register(lambda: cerrar_pool())


def obtener_conexion() -> AbstractContextManager[Connection[DictRow]]:
    """Context manager con una conexión reutilizable del pool.

    Mantiene la semántica histórica de `with obtener_conexion() as conn:`
    (commit / rollback al salir del bloque, según `Connection.__exit__`),
    pero la conexión vuelve al pool en vez de abrirse y cerrarse en cada
    consulta.
    """
    return _obtener_pool().connection()


def cerrar_pool() -> None:
    """Cierra el pool (al apagar la aplicación). No-op si nunca se usó."""
    global _pool

    with _pool_lock:
        if _pool is not None:
            _pool.close()
            _pool = None
