from abc import ABC, abstractmethod
from datetime import date


class RepositorioConsultaDashboardCobranza(ABC):

    @abstractmethod
    def obtener_cuotas_dashboard(self, rut_usuario: str) -> list[dict]:
        pass

    @abstractmethod
    def obtener_polizas_sin_plan_pago(self, rut_usuario: str) -> list[dict]:
        pass

    @abstractmethod
    def obtener_recordatorios_cobranza(self, rut_usuario: str, fecha_hasta: date) -> list[dict]:
        pass
