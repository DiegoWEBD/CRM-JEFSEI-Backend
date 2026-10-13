from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class ActualizarTransicionUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(
        self,
        codigo_estado_origen: str,
        codigo_estado_destino: str,
        es_manual: bool,
        accion_requerida: str | None,
    ) -> bool:
        transicion = self.repositorio_estados.obtener_transicion(
            codigo_estado_origen, codigo_estado_destino
        )
        if transicion is None:
            raise RecursoNoEncontradoException('La transición solicitada no existe')

        if transicion.es_principal:
            raise ConflictoEnAccionException(
                'Las transiciones principales no se pueden editar'
            )

        if es_manual is False and transicion.accion_requerida:
            accion_requerida = None

        transicion.es_manual = es_manual
        transicion.accion_requerida = (
            accion_requerida.strip() if accion_requerida else None
        )

        return self.repositorio_estados.actualizar_transicion(transicion)
