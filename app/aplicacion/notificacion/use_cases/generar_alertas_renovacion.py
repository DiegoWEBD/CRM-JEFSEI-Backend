from datetime import datetime, timezone

from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class GenerarAlertasRenovacionUseCase:
    """Barrido periódico (scheduler) de alertas de renovación de pólizas.

    Evalúa TODAS las pólizas con fin de vigencia a 2 meses o menos vía
    GenerarAlertaRenovacionPolizaUseCase (dueño de la lógica de evaluación) y
    registra las alertas que falten. La dedupe_key es estable (sin
    timestamp), por lo que el `on conflict do nothing` del repositorio evita
    duplicados entre corridas sin necesidad de guardas adicionales.
    """

    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alerta_renovacion: GenerarAlertaRenovacionPolizaUseCase,
    ) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_renovacion = generar_alerta_renovacion

    def ejecutar(self, ahora: datetime | None = None) -> list[Notificacion]:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        creadas: list[Notificacion] = []

        for poliza in self.repositorio_notificaciones.obtener_polizas_alertables_renovacion():
            for notificacion in self.generar_alerta_renovacion.evaluar(poliza, ahora):
                if self.repositorio_notificaciones.registrar(notificacion):
                    creadas.append(notificacion)

        if creadas:
            hub.publicar_desde_hilo(
                (alerta.rut_usuario for alerta in creadas),
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
            )

        return creadas
