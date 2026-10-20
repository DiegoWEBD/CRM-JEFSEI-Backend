from abc import ABC, abstractmethod

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


class RepositorioUnidadesAlicuotas(ABC):

    @abstractmethod
    def listar_por_solicitud(self, id_solicitud: int) -> list[UnidadAlicuota]:
        pass
