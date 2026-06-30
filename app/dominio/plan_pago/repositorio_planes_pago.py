from abc import ABC, abstractmethod

from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza


class RepositorioPlanesPago(ABC):
    
    @abstractmethod
    def buscar_plan_pago_poliza(self, numero_poliza: str) -> PlanPago | None:
        pass

    @abstractmethod
    def registrar_plan_pago_poliza(self, poliza: Poliza, plan_pago: PlanPago, rut_usuario: str) -> None:
        pass