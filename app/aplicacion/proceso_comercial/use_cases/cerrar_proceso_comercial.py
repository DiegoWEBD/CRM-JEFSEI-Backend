from datetime import datetime, timezone

from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA, TIPOS_ALERTA_SLA
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class CerrarProcesoComercialUseCase:

    def __init__(
        self, 
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_planes_pago: RepositorioPlanesPago,
        repositorio_polizas: RepositorioPolizas,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso
    ):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_planes_pago = repositorio_planes_pago
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, id: int, ganado: bool, observacion: str | None, usuario: Usuario):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')
        
        if proceso.cerrado:
            raise RecursoYaExisteException('La oportunidad ya se encuentra cerrada')
        
        if ganado:
            poliza = self.repositorio_polizas.buscar_por_proceso_comercial(id)

            if not poliza:
                raise ConflictoEnAccionException('La oportunidad debe tener una póliza y un plan de pago para poder cerrarse')

            if not self.repositorio_planes_pago.buscar_plan_pago_poliza(poliza.numero_poliza):
                raise ConflictoEnAccionException('La oportunidad debe tener una póliza y un plan de pago para poder cerrarse')

        self.repositorio_procesos_comerciales.cerrar(
            id=id,
            ganado=ganado,
            observacion=observacion,
            rut_usuario=usuario.rut
        )

        # Al cerrar, las alertas SLA y de fecha de cierre dejan de ser
        # relevantes: se marcan leídas con la misma fecha del cierre.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(
            id, TIPOS_ALERTA_SLA + TIPOS_ALERTA_FECHA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )