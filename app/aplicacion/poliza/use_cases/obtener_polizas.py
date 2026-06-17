from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class ObtenerPolizasUseCase:

    def __init__(self, repositorio_polizas: RepositorioPolizas):
        self.repositorio_polizas = repositorio_polizas

    def ejecutar(self, id_cliente: int, rut_usuario: str | None) -> list[Poliza]:
        return self.repositorio_polizas.obtener_polizas_cliente(id_cliente, rut_usuario)