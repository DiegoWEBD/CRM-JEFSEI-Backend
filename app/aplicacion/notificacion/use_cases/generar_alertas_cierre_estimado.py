from datetime import datetime, timezone

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_cierre_estimado import (
    GenerarAlertaCierreEstimadoUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import tipos_resueltos_por
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


class GenerarAlertasCierreEstimadoUseCase:
    """Barrido periódico (scheduler) de alertas de cierre estimado.

    Evalúa TODOS los procesos comerciales abiertos vía
    GenerarAlertaCierreEstimadoUseCase (dueño de la lógica de evaluación) y
    registra las alertas que falten. La guarda `existe_alerta_proceso` evita
    duplicados entre corridas: como la dedupe_key incluye timestamp, sin ella
    cada corrida crearía una alerta nueva.

    Escalonamiento: al vencer la fecha de cierre, el aviso de "cierre próximo"
    deja de aplicar y se marca leído, incluso si la alerta vencida ya existía
    (así se auto-sanan los pares pendientes heredados).
    """

    def __init__(
        self,
        repositorio_procesos: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alerta_cierre: GenerarAlertaCierreEstimadoUseCase,
        servicio_alertas: ServicioAlertasProceso,
    ) -> None:
        self.repositorio_procesos = repositorio_procesos
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_cierre = generar_alerta_cierre
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, ahora: datetime | None = None) -> list[Notificacion]:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        creadas: list[Notificacion] = []
        resueltas: list[str] = []

        for proceso in self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=None,
            abiertos=True,
        ):
            notificacion = self.generar_alerta_cierre.evaluar(proceso, ahora)

            if notificacion is None:
                continue

            # Escalonamiento: la alerta aplicable deja obsoletas a las de
            # nivel inferior (al vencer la fecha, el aviso de "cierre próximo"
            # ya no aplica). Corre ANTES de la guarda de existencia para que
            # también resuelva alertas creadas en corridas anteriores.
            tipos_a_resolver = tipos_resueltos_por({notificacion.codigo_tipo})

            if tipos_a_resolver:
                resueltas.extend(
                    self.servicio_alertas.marcar_leidas(
                        proceso.id, tipos_a_resolver, ahora
                    )
                )

            if self.repositorio_notificaciones.existe_alerta_proceso(
                notificacion.codigo_tipo,
                proceso.id,
                notificacion.rut_usuario,
            ):
                continue

            if self.repositorio_notificaciones.registrar(notificacion):
                creadas.append(notificacion)

        if creadas:
            hub.publicar_desde_hilo(
                (alerta.rut_usuario for alerta in creadas),
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
            )

        if resueltas:
            hub.publicar_desde_hilo(
                resueltas,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_fecha_cierre_actualizadas'},
            )

        return creadas
