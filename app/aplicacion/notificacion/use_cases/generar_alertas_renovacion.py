from datetime import datetime, timezone

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import tipos_resueltos_por


class GenerarAlertasRenovacionUseCase:
    """Barrido periódico (scheduler) de alertas de renovación de pólizas.

    Evalúa TODAS las pólizas con fin de vigencia a 2 meses o menos vía
    GenerarAlertaRenovacionPolizaUseCase (dueño de la lógica de evaluación) y
    registra las alertas que falten. La dedupe_key es estable (sin
    timestamp), por lo que el `on conflict do nothing` del repositorio evita
    duplicados entre corridas sin necesidad de guardas adicionales.

    Escalonamiento: los hitos alcanzados dejan obsoletos a los anteriores
    (al gestionar la renovación, el aviso de iniciar cotización ya no aplica),
    por lo que se marcan como leídas las alertas de nivel inferior de la
    misma póliza.
    """

    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alerta_renovacion: GenerarAlertaRenovacionPolizaUseCase,
        servicio_alertas: ServicioAlertasProceso,
    ) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_renovacion = generar_alerta_renovacion
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, ahora: datetime | None = None) -> list[Notificacion]:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        creadas: list[Notificacion] = []
        resueltas: list[str] = []

        for poliza in self.repositorio_notificaciones.obtener_polizas_alertables_renovacion():
            alertas = self.generar_alerta_renovacion.evaluar(poliza, ahora)

            for notificacion in alertas:
                if self.repositorio_notificaciones.registrar(notificacion):
                    creadas.append(notificacion)

            tipos_a_resolver = tipos_resueltos_por(
                {notificacion.codigo_tipo for notificacion in alertas}
            )

            if tipos_a_resolver:
                resueltas.extend(
                    self.servicio_alertas.marcar_leidas_renovacion(
                        poliza.numero_poliza, ahora, tipos=tipos_a_resolver
                    )
                )

        if creadas:
            hub.publicar_desde_hilo(
                (alerta.rut_usuario for alerta in creadas),
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
            )

        if resueltas:
            hub.publicar_desde_hilo(
                resueltas,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_resueltas'},
            )

        return creadas
