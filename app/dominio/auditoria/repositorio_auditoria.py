from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from psycopg import Connection
from psycopg.rows import DictRow

from app.dominio.auditoria.auditoria_evento import AuditoriaEvento
from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento


class RepositorioAuditoria(ABC):
    """Puerto de escritura y consulta de auditoría.

    ``registrar`` acepta una conexión externa para poder enlistarse en la misma
    transacción que la operación de negocio que audita (§21). Sin conexión, el
    repositorio abre la suya propia.
    """

    @abstractmethod
    def registrar(
        self,
        evento: AuditoriaEvento,
        conn: Optional[Connection[DictRow]] = None,
    ) -> AuditoriaEvento:
        pass

    @abstractmethod
    def obtener_por_id(self, id_evento: int) -> AuditoriaEvento | None:
        pass

    @abstractmethod
    def obtener_paginado(
        self,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        tipo_evento: TipoEvento | None,
        categoria: Categoria | None,
        resultado: Resultado | None,
        recurso_tipo: str | None,
        recurso_id: str | None,
        request_id: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[AuditoriaEvento], int]:
        """Devuelve (eventos, total). El total respeta los mismos filtros."""
        pass

    @abstractmethod
    def obtener_por_recurso(
        self,
        recurso_tipo: str,
        recurso_id: str,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[AuditoriaEvento], int]:
        pass
