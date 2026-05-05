from abc import ABC, abstractmethod
from typing import Optional

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen


class ConsultaProspectosService(ABC):

    @abstractmethod
    def obtener_todos(rut_usuario: Optional[str] = None) -> list[ProspectoResumen]:
        pass
