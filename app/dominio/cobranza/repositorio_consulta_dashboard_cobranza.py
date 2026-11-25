from abc import ABC, abstractmethod
from datetime import date


class RepositorioConsultaDashboardCobranza(ABC):

    @abstractmethod
    def obtener_cuotas_dashboard(self, rut_usuario: str | None) -> list[dict]:
        """Con rut_usuario=None se devuelven las cuotas de todos los cobradores."""
        pass

    @abstractmethod
    def obtener_polizas_sin_plan_pago(self, rut_usuario: str | None) -> list[dict]:
        pass

    @abstractmethod
    def obtener_recordatorios_cobranza(self, rut_usuario: str | None, fecha_hasta: date) -> list[dict]:
        pass
