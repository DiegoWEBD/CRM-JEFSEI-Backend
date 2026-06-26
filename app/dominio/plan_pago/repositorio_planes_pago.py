from abc import ABC, abstractmethod

from app.dominio.plan_pago.plan_pago import PlanPago


class RepositorioPlanesPago(ABC):
    
    @abstractmethod
    def buscar_plan_pago_poliza(self, numero_poliza: str) -> PlanPago | None:
        pass