from app.aplicacion.cobranza.use_cases.obtener_dashboard_cobranza import (
    ObtenerDashboardCobranzaUseCase,
)
from app.infraestructura.cobranza.repositorio_consulta_dashboard_cobranza_postgres import (
    RepositorioConsultaDashboardCobranzaPostgres,
)


def get_obtener_dashboard_cobranza_use_case() -> ObtenerDashboardCobranzaUseCase:
    repositorio = RepositorioConsultaDashboardCobranzaPostgres()
    return ObtenerDashboardCobranzaUseCase(repositorio)
