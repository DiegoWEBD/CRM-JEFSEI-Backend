from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerPolizasUseCase:

    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas,
        repositorio_prospectos: RepositorioProspectos
    ):
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, id_cliente: int, rut_usuario: str | None) -> list[Poliza]:
        if not self.repositorio_prospectos.buscar_cliente(id_cliente):
            raise RecursoNoEncontradoException('Cliente no encontrado')

        return self.repositorio_polizas.obtener_polizas_cliente(id_cliente)