from abc import ABC, abstractmethod
from app.dominio.poliza.poliza import Poliza


class RepositorioPolizas(ABC):
    
    @abstractmethod
    def buscar(self, numero_poliza: str) -> Poliza | None:
        pass

    @abstractmethod
    def registrar_a_proceso_comercial(self, poliza: Poliza, id_proceso_comercial: int) -> None:
        pass

    @abstractmethod
    def obtener_polizas_cliente(self, id_cliente: int, rut_usuario: str | None) -> list[Poliza]:
        pass

    @abstractmethod
    def polizas_gestionadas_ej_comercial_mes_actual(self, rut_ejecutivo: str) -> list[Poliza]:
        pass