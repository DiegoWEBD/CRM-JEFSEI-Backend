from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class ObtenerTransicionesAdminUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        estado = self.repositorio_estados.obtener_por_codigo(codigo_estado)
        if estado is None:
            raise RecursoNoEncontradoException('El estado solicitado no existe')

        return self.repositorio_estados.obtener_transiciones(codigo_estado)
