from datetime import datetime
from dateutil.relativedelta import relativedelta

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.cuota.cuota import Cuota
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario


class CrearPlanPagoUseCase:

    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas,
        repositorio_planes_pago: RepositorioPlanesPago,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_planes_pago = repositorio_planes_pago
        self.authorization_service = authorization_service

    def ejecutar(self, numero_poliza: str, fecha_primera_cuota: datetime, numero_cuotas: int, usuario: Usuario):
        
        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if not poliza:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')
        
        if not self.authorization_service.usuario_puede_ver_plan_pago(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException

        plan_pago = self.repositorio_planes_pago.buscar_plan_pago_poliza(numero_poliza)

        if plan_pago:
            raise RecursoYaExisteException(f'La póliza {numero_poliza} ya tiene un plan de pago creado')
        
        cuotas = []

        for numero_cuota in range(1, numero_cuotas + 1):
            fecha_vencimiento = fecha_primera_cuota + relativedelta(months=numero_cuota - 1)

            cuotas.append(Cuota(
                numero_cuota=numero_cuota,
                fecha_vencimiento=fecha_vencimiento,
                pagado=False,
                fecha_pago=None
            ))

        plan_pago = PlanPago(cuotas=cuotas)

        self.repositorio_planes_pago.registrar_plan_pago_poliza(
            poliza=poliza,
            plan_pago=plan_pago,
            rut_usuario=usuario.rut
        )