# app/infraestructura/db/unit_of_work.py
"""Unit of Work: agrupa varios repositorios en una sola transacción.

Por qué NO es un UoW por request: los exception handlers de ``main.py``
(RecursoNoEncontrado, UsuarioNoAutorizado, ConflictosEnAccion y el catch-all)
devuelven un ``JSONResponse``, con lo cual la excepción deja de propagarse. Un
UoW abierto a nivel de request commitearía al cerrarse y confirmaría
operaciones de negocio que en realidad fallaron con 403/404/500.

Por eso el alcance es el use case: se abre justo donde está el
``UPDATE``/``DELETE`` y se cierra al terminar, con la excepción todavía viva.

Uso:

    with UnitOfWork() as uow:
        repo.buscar(id, conn=uow.connection)
        repo.actualizar(entidad, conn=uow.connection)
        auditoria.registrar(evento, conn=uow.connection)

Si algo lanza, se hace rollback y no queda un SUCCESS de auditoría por un
cambio que nunca se confirmó.
"""

from typing import Callable, Optional

from psycopg import Connection
from psycopg.rows import DictRow

from app.infraestructura.db.conexion import obtener_conexion


class UnitOfWorkClosedError(RuntimeError):
    """Se intentó usar el UoW fuera del ``with`` o después de cerrarlo."""


class UnitOfWork:
    def __init__(
        self,
        connection_factory: Callable[[], Connection[DictRow]] = obtener_conexion,
    ) -> None:
        self._connection_factory = connection_factory
        self._connection: Optional[Connection[DictRow]] = None

    @property
    def connection(self) -> Connection[DictRow]:
        if self._connection is None:
            raise UnitOfWorkClosedError(
                'La conexión solo existe dentro del bloque "with UnitOfWork() as uow"'
            )
        return self._connection

    @property
    def esta_activo(self) -> bool:
        return self._connection is not None

    def cursor(self):
        """Cursor sobre la conexión del UoW. El caller hace ``with``."""
        return self.connection.cursor()

    def __enter__(self) -> 'UnitOfWork':
        if self._connection is not None:
            raise RuntimeError('Este UnitOfWork ya está activo')
        self._connection = self._connection_factory()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self._connection is None:
            return False
        conexion, self._connection = self._connection, None
        try:
            if exc_type is None:
                conexion.commit()
            else:
                conexion.rollback()
        finally:
            conexion.close()
        return False

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()
