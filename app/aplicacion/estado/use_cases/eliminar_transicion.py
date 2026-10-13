from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class EliminarTransicionUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(self, codigo_estado_origen: str, codigo_estado_destino: str) -> bool:
        transicion = self.repositorio_estados.obtener_transicion(
            codigo_estado_origen, codigo_estado_destino
        )
        if transicion is None:
            raise RecursoNoEncontradoException('La transición solicitada no existe')

        if transicion.es_principal:
            raise ConflictoEnAccionException(
                'Las transiciones principales no se pueden eliminar'
            )

        if self.repositorio_estados.contar_transiciones_salida(codigo_estado_origen) <= 1:
            raise ConflictoEnAccionException(
                'El estado debe mantener al menos una transición de salida'
            )

        return self.repositorio_estados.eliminar_transicion(
            codigo_estado_origen, codigo_estado_destino
        )
