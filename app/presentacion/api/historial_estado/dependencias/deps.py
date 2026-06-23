from app.aplicacion.historial_estado.use_cases.obtener_historial_estados_proceso_comercial import ObtenerHistorialEstadosProcesoComercialUseCase
from app.infraestructura.historial_estado.repositorio_historial_estado_postgres import RepositorioHistorialEstadoPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres


def get_obtener_historial_estados_proceso_comercial_use_case():
    repositorio_procesos = RepositorioProcesosComercialesPostgres()
    repositorio_historial = RepositorioHistorialEstadoPostgres()

    return ObtenerHistorialEstadosProcesoComercialUseCase(
        repositorio_procesos_comerciales=repositorio_procesos,
        repositorio_historial_estado=repositorio_historial
    )