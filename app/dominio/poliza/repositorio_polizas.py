from abc import ABC, abstractmethod
from app.dominio.poliza.poliza import Poliza


class RepositorioPolizas(ABC):
    
    @abstractmethod
    def registrar(self, poliza: Poliza) -> None:
        pass

    @abstractmethod
    def buscar(self, id_cliente: int, rut_usuario: str | None) -> list[Poliza]:
        pass

    @abstractmethod
    def polizas_gestionadas_ej_comercial_mes_actual(self, rut_ejecutivo: str) -> list[Poliza]:
        pass