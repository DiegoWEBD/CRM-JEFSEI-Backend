from abc import ABC, abstractmethod

from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial


class RepositorioEstadosProcesoComercial(ABC):

    @abstractmethod
    def obtener_transiciones_manuales(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        """Transiciones manuales disponibles desde el estado dado."""
        pass
