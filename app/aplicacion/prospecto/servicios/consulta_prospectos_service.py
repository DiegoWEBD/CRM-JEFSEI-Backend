from abc import ABC, abstractmethod

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen


class ConsultaProspectosService(ABC):

    @abstractmethod
    def obtener_todos(
        self,
        rut_usuario: str | None = None,
        filtro: str | None = None,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 25,
        region: str | None = None,
        comuna: str | None = None,
    ) -> dict:
        pass

    @abstractmethod
    def obtener_por_administrador(
        self, id_administrador: int, rut_usuario: str | None = None
    ) -> list[ProspectoResumen]:
        pass
