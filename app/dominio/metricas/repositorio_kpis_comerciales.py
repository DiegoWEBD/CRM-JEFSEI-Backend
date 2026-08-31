from abc import ABC, abstractmethod

from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto


class RepositorioKpisComerciales(ABC):

    @abstractmethod
    def obtener_conversion_prospectos(self, filtros: FiltrosKpiDto) -> dict:
        pass

    @abstractmethod
    def obtener_tasa_cierre(self, filtros: FiltrosKpiDto) -> dict:
        pass

    @abstractmethod
    def obtener_prima_vs_meta(self, filtros: FiltrosKpiDto) -> list[dict]:
        pass

    @abstractmethod
    def obtener_tiempo_promedio_cierre(self, filtros: FiltrosKpiDto) -> dict:
        pass

    @abstractmethod
    def obtener_aging_pipeline(self, filtros: FiltrosKpiDto) -> dict:
        pass

    @abstractmethod
    def obtener_tasa_renovacion(self, filtros: FiltrosKpiDto) -> dict:
        pass

    @abstractmethod
    def obtener_prima_en_riesgo(self, filtros: FiltrosKpiDto, dias_ventana: int = 30) -> dict:
        pass

    @abstractmethod
    def obtener_tasa_morosidad(self, filtros: FiltrosKpiDto) -> dict:
        pass
