from datetime import datetime

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.dominio.notificacion.tipos_alerta import tipos_resueltos_por
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


class ReevaluarAlertasRenovacionDescarteUseCase:
    """Re-evalúa las alertas de renovación tras descartar una oportunidad de
    renovación.

    Al iniciar la renovación sus alertas quedaron resueltas (marcadas leídas),
    y una fila con la misma dedupe_key, aunque esté leída, bloquearía la
    re-creación. Por eso primero se eliminan las alertas de renovación de la
    póliza base y recién ahí se re-evalúa: los hitos que sigan aplicando
    (p. ej. la póliza vencida sin renovación) vuelven a crearse de inmediato,
    sin esperar al scheduler.

    Escalonamiento: igual que en el barrido del scheduler, los hitos
    alcanzados dejan obsoletos a los anteriores, por lo que las alertas de
    nivel inferior recién creadas se marcan leídas (queda sin leer solo la
    más crítica, como antes de iniciar la renovación).

    No publica en el hub: devuelve los RUTs afectados para que el caso de uso
    llamante, que conoce el conjunto completo de destinatarios, publique el
    refresco correspondiente. Es no-op si el proceso no es de renovación.
    """

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        servicio_alertas: ServicioAlertasProceso,
        generar_alerta_renovacion: GenerarAlertaRenovacionPolizaUseCase,
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.servicio_alertas = servicio_alertas
        self.generar_alerta_renovacion = generar_alerta_renovacion

    def ejecutar(self, id_proceso_comercial: int, ahora: datetime) -> list[str]:
        """Destinatarios afectados (alertas eliminadas, recreadas o marcadas
        leídas por escalonamiento), sin repetidos.

        Debe invocarse una vez persistido el descarte del proceso: la
        re-evaluación considera que la oportunidad ya no está activa.
        """
        numero_poliza = self.repositorio_procesos_comerciales.obtener_poliza_base_renovacion(
            id_proceso_comercial
        )

        if numero_poliza is None:
            return []

        destinatarios = self.servicio_alertas.eliminar_renovacion(numero_poliza)
        creadas = self.generar_alerta_renovacion.ejecutar(numero_poliza, ahora)

        for notificacion in creadas:
            if notificacion.rut_usuario:
                destinatarios.append(notificacion.rut_usuario)

        tipos_a_resolver = tipos_resueltos_por({notificacion.codigo_tipo for notificacion in creadas})

        if tipos_a_resolver:
            destinatarios.extend(
                self.servicio_alertas.marcar_leidas_renovacion(
                    numero_poliza, ahora, tipos=tipos_a_resolver
                )
            )

        return list(dict.fromkeys(destinatarios))
