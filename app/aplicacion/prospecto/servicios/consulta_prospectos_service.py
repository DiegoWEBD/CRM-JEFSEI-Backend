from abc import ABC, abstractmethod

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen


class ConsultaProspectosService(ABC):

    @abstractmethod
    def obtener_todos(self, rut_usuario: str | None = None) -> list[ProspectoResumen]:
        pass
