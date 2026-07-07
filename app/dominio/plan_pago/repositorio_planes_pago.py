from abc import ABC, abstractmethod
from datetime import datetime

from app.dominio.cuota.cuota import Cuota
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza


class RepositorioPlanesPago(ABC):
    
    @abstractmethod
    def buscar_plan_pago_poliza(self, numero_poliza: str) -> PlanPago | None:
        pass

    @abstractmethod
    def buscar_cuota_por_id(self, id_cuota: int) -> Cuota | None:
        pass

    @abstractmethod
    def registrar_plan_pago_poliza(self, poliza: Poliza, plan_pago: PlanPago, rut_usuario: str) -> None:
        pass

    @abstractmethod
    def actualizar_cuota(self, id_cuota: int, pagado: bool, fecha_pago: datetime | None) -> None:
        pass