from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class ReactivarPolizaUseCase:

    def __init__(self, repositorio_polizas: RepositorioPolizas):
        self.repositorio_polizas = repositorio_polizas

    def ejecutar(self, numero_poliza: str) -> None:
        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if poliza is None:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if poliza.estado != EstadoPoliza.CANCELADA:
            raise ConflictoEnAccionException(f'La póliza {numero_poliza} no se encuentra cancelada')

        self.repositorio_polizas.actualizar_cancelada(numero_poliza, False)
