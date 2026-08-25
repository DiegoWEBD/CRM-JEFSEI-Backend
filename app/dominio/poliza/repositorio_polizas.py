from abc import ABC, abstractmethod
from datetime import datetime

from app.dominio.poliza.poliza import Poliza


class RepositorioPolizas(ABC):
    
    @abstractmethod
    def buscar(self, numero_poliza: str) -> Poliza | None:
        pass

    @abstractmethod
    def buscar_por_proceso_comercial(self, id_proceso_comercial: int) -> Poliza | None:
        pass

    @abstractmethod
    def registrar_a_proceso_comercial(self, poliza: Poliza, id_proceso_comercial: int, rut_usuario: str) -> None:
        pass

    @abstractmethod
    def obtener_polizas_cliente(self, id_cliente: int) -> list[Poliza]:
        pass

    @abstractmethod
    def polizas_gestionadas_ej_comercial_mes_actual(self, rut_ejecutivo: str) -> list[Poliza]:
        pass

    @abstractmethod
    def actualizar_cancelada(self, numero_poliza: str, cancelada: bool) -> None:
        pass

    @abstractmethod
    def actualizar(
        self,
        numero_poliza: str,
        tipo: str,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime | None,
        inicio_vigencia: datetime | None,
        fin_vigencia: datetime | None,
        id_company: int | None,
    ) -> None:
        pass
