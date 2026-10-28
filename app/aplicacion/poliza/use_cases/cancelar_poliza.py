from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class CancelarPolizaUseCase:

    def __init__(
        self,
        repositorio_polizas: RepositorioPolizas,
        servicio_alertas: ServicioAlertasProceso,
    ):
        self.repositorio_polizas = repositorio_polizas
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, numero_poliza: str) -> None:
        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if poliza is None:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if poliza.estado == EstadoPoliza.CANCELADA:
            raise ConflictoEnAccionException(f'La póliza {numero_poliza} ya se encuentra cancelada')

        self.repositorio_polizas.actualizar_cancelada(numero_poliza, True)

        # Una póliza cancelada no genera alertas de renovación: se eliminan las
        # pendientes para que no queden huérfanas. Al reactivarla se re-evalúan
        # y se recrean las que correspondan.
        destinatarios = self.servicio_alertas.eliminar_renovacion(numero_poliza)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_actualizadas'},
            )
