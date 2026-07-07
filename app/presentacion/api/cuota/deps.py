from app.aplicacion.plan_pago.use_cases.marcar_pago_cuota import MarcarPagoCuotaUseCase
from app.infraestructura.plan_pago.repositorio_planes_pago_postgres import RepositorioPlanesPagoPostgres


def get_marcar_pago_cuota_use_case():
    repositorio_planes_pago = RepositorioPlanesPagoPostgres()

    return MarcarPagoCuotaUseCase(
        repositorio_planes_pago=repositorio_planes_pago
    )
