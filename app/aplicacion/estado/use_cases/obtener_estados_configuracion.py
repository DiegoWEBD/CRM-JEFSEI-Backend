from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial


class ObtenerEstadosConfiguracionUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(self, texto_busqueda: str | None = None) -> list[EstadoInformativoProcesoComercial]:
        return self.repositorio_estados.obtener_todos(texto_busqueda)
