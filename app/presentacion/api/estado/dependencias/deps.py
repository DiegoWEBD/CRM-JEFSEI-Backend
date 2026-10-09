from app.aplicacion.estado.use_cases.obtener_transiciones_manuales import ObtenerTransicionesManualesUseCase
from app.infraestructura.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial_postgres import RepositorioEstadosProcesoComercialPostgres


def get_obtener_transiciones_manuales_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return ObtenerTransicionesManualesUseCase(
        repositorio_estados=repositorio_estados,
    )
