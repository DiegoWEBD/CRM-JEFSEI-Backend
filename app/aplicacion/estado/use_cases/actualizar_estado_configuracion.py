from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class ActualizarEstadoConfiguracionUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(
        self,
        codigo: str,
        dias_limite: int | None,
        probabilidad_cierre: float,
    ) -> bool:
        estado = self.repositorio_estados.obtener_por_codigo(codigo)
        if estado is None:
            raise RecursoNoEncontradoException('El estado solicitado no existe')

        if probabilidad_cierre is None or not (0 <= probabilidad_cierre <= 1):
            raise ConflictoEnAccionException('La probabilidad de cierre debe estar entre 0 y 1')

        if dias_limite is not None and dias_limite < 0:
            raise ConflictoEnAccionException('Los días límite no pueden ser negativos')

        return self.repositorio_estados.actualizar_configuracion(
            codigo=codigo,
            dias_limite=dias_limite,
            probabilidad_cierre=probabilidad_cierre,
        )
