from app.aplicacion.gestion_comercial.use_cases.obtener_gestiones_comerciales import ObtenerGestionesComercialesUseCase
from app.aplicacion.gestion_comercial.use_cases.obtener_ultima_gestion_comercial import ObtenerUltimaGestionComercialUseCase
from app.aplicacion.gestion_comercial.use_cases.registrar_gestion_comercial import RegistrarGestionComercialUseCase
from app.infraestructura.gestion_comercial.repositorio_gestiones_comerciales_postgres import RepositorioGestionesComercialesPostgres
from app.infraestructura.recordatorio.repositorio_recordatorios_postgres import RepositorioRecordatoriosPostgres


def get_registrar_gestion_comercial_use_case() -> RegistrarGestionComercialUseCase:
    repositorio = RepositorioGestionesComercialesPostgres()
    repositorio_recordatorios = RepositorioRecordatoriosPostgres()
    return RegistrarGestionComercialUseCase(repositorio, repositorio_recordatorios)


def get_obtener_gestiones_comerciales_use_case() -> ObtenerGestionesComercialesUseCase:
    repositorio = RepositorioGestionesComercialesPostgres()
    return ObtenerGestionesComercialesUseCase(repositorio)


def get_obtener_ultima_gestion_comercial_use_case() -> ObtenerUltimaGestionComercialUseCase:
    repositorio = RepositorioGestionesComercialesPostgres()
    return ObtenerUltimaGestionComercialUseCase(repositorio)
