from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.cuota.cuota import Cuota
from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA, TIPOS_ALERTA_SLA
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class CrearPlanPagoUseCase:

    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas,
        repositorio_planes_pago: RepositorioPlanesPago,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_historial_estado: RepositorioHistorialEstadoProcesosComerciales,
        servicio_alertas: ServicioAlertasProceso
    ) -> None:
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_planes_pago = repositorio_planes_pago
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.servicio_alertas = servicio_alertas
        self.repositorio_historial_estado = repositorio_historial_estado

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
            plan_pago=plan_pago
        )

        proceso_comercial = self.repositorio_procesos_comerciales.buscar(poliza.id_proceso_comercial)

        if not proceso_comercial:
            raise RecursoNoEncontradoException('No se pudo cerrar la oportunidad')

        historial = HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso_comercial.id,
            codigo_estado='PLAN_PAGO_CREADO',
            rut_registrado_por=usuario.rut,
            fecha=datetime.now(tz=timezone.utc)
        )

        self.repositorio_historial_estado.registrar(historial)

        fecha_cierre = datetime.now(tz=timezone.utc)

        proceso_comercial.cerrado = True
        proceso_comercial.fecha_cierre = fecha_cierre
        proceso_comercial.estado_actual = EstadoInformativoProcesoComercial(
            codigo='GANADO',
            nombre=''
        )

        self.repositorio_procesos_comerciales.guardar(proceso_comercial, es_nuevo=False)

        historial = HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso_comercial.id,
            codigo_estado='GANADO',
            rut_registrado_por=usuario.rut,
            fecha=fecha_cierre
        )

        self.repositorio_historial_estado.registrar(historial)

        # Tras las dos transiciones (plan de pago y cierre ganado), las alertas
        # SLA y de fecha de cierre dejan de ser relevantes: una sola pasada.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(
            poliza.id_proceso_comercial, TIPOS_ALERTA_SLA + TIPOS_ALERTA_FECHA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )