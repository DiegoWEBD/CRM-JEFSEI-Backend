from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial


class ObtenerTransicionesManualesUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        return self.repositorio_estados.obtener_transiciones_manuales(codigo_estado)
