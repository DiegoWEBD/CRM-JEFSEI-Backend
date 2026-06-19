from abc import ABC, abstractmethod
from datetime import date


class RepositorioMetricasDashboard(ABC):

    @abstractmethod
    def obtener_prima_neta_mes(self, year: int, mes: int) -> float:
        pass

    @abstractmethod
    def obtener_prima_neta_rango(
        self, desde: date, hasta: date
    ) -> float:
        pass

    @abstractmethod
    def obtener_tendencia_12_meses(self) -> list[dict]:
        pass

    @abstractmethod
    def obtener_prima_por_compania(
        self, year: int, mes: int
    ) -> list[dict]:
        pass

    @abstractmethod
    def obtener_prima_por_ejecutivo(
        self, year: int, mes: int
    ) -> list[dict]:
        pass

    @abstractmethod
    def obtener_prima_por_producto(
        self, year: int, mes: int
    ) -> list[dict]:
        pass

    @abstractmethod
    def obtener_actividades_comerciales(
        self, year: int, mes: int
    ) -> list[dict]:
        pass

    @abstractmethod
    def obtener_resumen_actividades(
        self, year: int, mes: int
    ) -> dict:
        pass

    @abstractmethod
    def obtener_polizas_por_comuna(self) -> list[dict]:
        pass

    @abstractmethod
    def obtener_polizas_por_producto(self) -> list[dict]:
        pass

    @abstractmethod
    def obtener_kpis_evaluacion(self) -> dict:
        pass

    @abstractmethod
    def obtener_evaluacion_por_compania(self) -> list[dict]:
        pass

    @abstractmethod
    def obtener_evaluacion_por_producto(self) -> list[dict]:
        pass
