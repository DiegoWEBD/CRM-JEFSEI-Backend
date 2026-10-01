from abc import ABC, abstractmethod
from datetime import datetime

from app.dominio.auditoria.registro_auditoria import RegistroAuditoria


class RepositorioAuditoria(ABC):

    @abstractmethod
    def registrar(self, registro: RegistroAuditoria) -> None:
        pass

    @abstractmethod
    def obtener_paginados(
        self,
        categoria: str | None,
        evento: str | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        entidad_tipo: str | None,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        texto_busqueda: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[RegistroAuditoria], int]:
        pass
