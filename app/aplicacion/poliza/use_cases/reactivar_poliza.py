from datetime import datetime, timezone

from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class ReactivarPolizaUseCase:

    def __init__(
        self,
        repositorio_polizas: RepositorioPolizas,
        generar_alerta_renovacion: GenerarAlertaRenovacionPolizaUseCase,
    ):
        self.repositorio_polizas = repositorio_polizas
        self.generar_alerta_renovacion = generar_alerta_renovacion

    def ejecutar(self, numero_poliza: str) -> None:
        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if poliza is None:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if poliza.estado != EstadoPoliza.CANCELADA:
            raise ConflictoEnAccionException(f'La póliza {numero_poliza} no se encuentra cancelada')

        self.repositorio_polizas.actualizar_cancelada(numero_poliza, False)

        # Al reactivarla, sus alertas de renovación (eliminadas al cancelarla)
        # se re-crean al tiro si los hitos siguen aplicando, sin esperar al
        # scheduler.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = [
            notificacion.rut_usuario
            for notificacion in self.generar_alerta_renovacion.ejecutar(numero_poliza, ahora)
            if notificacion.rut_usuario
        ]

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_actualizadas'},
            )
