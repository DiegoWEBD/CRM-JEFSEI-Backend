from abc import ABC, abstractmethod

from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial


class RepositorioEstadosProcesoComercial(ABC):

    @abstractmethod
    def obtener_transiciones_manuales(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        """Transiciones manuales disponibles desde el estado dado."""
        pass

    @abstractmethod
    def obtener_todos(self, texto_busqueda: str | None = None) -> list[EstadoInformativoProcesoComercial]:
        """Todos los estados del proceso comercial con su configuración."""
        pass

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> EstadoInformativoProcesoComercial | None:
        pass

    @abstractmethod
    def actualizar_configuracion(
        self, codigo: str, dias_limite: int | None, probabilidad_cierre: float
    ) -> bool:
        pass

    @abstractmethod
    def obtener_transiciones(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        """Todas las transiciones (principales y secundarias) desde el estado dado."""
        pass

    @abstractmethod
    def obtener_transicion(
        self, codigo_estado_origen: str, codigo_estado_destino: str
    ) -> TransicionEstadoProcesoComercial | None:
        pass

    @abstractmethod
    def contar_transiciones_salida(self, codigo_estado_origen: str) -> int:
        pass

    @abstractmethod
    def existe_transicion(self, codigo_estado_origen: str, codigo_estado_destino: str) -> bool:
        pass

    @abstractmethod
    def crear_transicion(self, transicion: TransicionEstadoProcesoComercial) -> bool:
        pass

    @abstractmethod
    def actualizar_transicion(self, transicion: TransicionEstadoProcesoComercial) -> bool:
        pass

    @abstractmethod
    def eliminar_transicion(self, codigo_estado_origen: str, codigo_estado_destino: str) -> bool:
        pass
