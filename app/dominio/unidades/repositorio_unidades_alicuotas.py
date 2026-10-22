from abc import ABC, abstractmethod

from app.dominio.unidades.unidad_alicuota import UnidadAlicuota


class RepositorioUnidadesAlicuotas(ABC):

    @abstractmethod
    def listar_por_oportunidad(self, id_proceso_comercial: int) -> list[UnidadAlicuota]:
        pass

    @abstractmethod
    def obtener_nombre_excel(self, id_proceso_comercial: int) -> str | None:
        pass

    @abstractmethod
    def guardar_o_reemplazar(
        self,
        id_proceso_comercial: int,
        nombre_excel: str,
        unidades: list[UnidadAlicuota],
    ) -> None:
        pass
