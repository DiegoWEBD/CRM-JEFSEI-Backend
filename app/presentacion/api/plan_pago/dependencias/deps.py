from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.plan_pago.use_cases.crear_plan_pago import CrearPlanPagoUseCase
from app.aplicacion.plan_pago.use_cases.obtener_plan_pago_poliza import ObtenerPlanPagoPolizaUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.plan_pago.repositorio_planes_pago_postgres import RepositorioPlanesPagoPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres


def get_obtener_plan_pago_poliza_use_case():
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_planes_pago = RepositorioPlanesPagoPostgres()

    return ObtenerPlanPagoPolizaUseCase(
        authorization_service=authorization_service,
        repositorio_planes_pago=repositorio_planes_pago,
        repositorio_polizas=repositorio_polizas
    )

def get_crear_plan_pago_use_case():
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_planes_pago = RepositorioPlanesPagoPostgres()

    return CrearPlanPagoUseCase(
        authorization_service=authorization_service,
        repositorio_planes_pago=repositorio_planes_pago,
        repositorio_polizas=repositorio_polizas
    )