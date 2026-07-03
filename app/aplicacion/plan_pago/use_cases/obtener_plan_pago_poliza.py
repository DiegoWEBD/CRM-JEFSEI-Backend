from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario


class ObtenerPlanPagoPolizaUseCase:

    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas,
        repositorio_planes_pago: RepositorioPlanesPago,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_planes_pago = repositorio_planes_pago
        self.authorization_service = authorization_service

    def ejecutar(self, numero_poliza: str, usuario: Usuario) -> PlanPago | None:
        
        if not self.repositorio_polizas.buscar(numero_poliza):
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')
        
        if not self.authorization_service.usuario_puede_ver_plan_pago(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException

        return self.repositorio_planes_pago.buscar_plan_pago_poliza(numero_poliza)