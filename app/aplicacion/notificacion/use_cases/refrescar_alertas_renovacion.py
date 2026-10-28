from datetime import datetime, timezone

from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_RENOVACION


class RefrescarAlertasRenovacionUseCase:
    """Refresca las alertas de renovación del cliente tras cambiar sus
    responsables (ejecutivo / asistente de renovación).

    Elimina las alertas no leídas de quienes ya no son destinatarios y
    re-evalúa en el mismo momento para crear las de los nuevos (creadas ahora,
    no transferidas). Sigue el patrón de _refrescar_alertas_de_cierre pero
    eliminando en vez de marcando leídas: la dedupe_key de renovación es
    estable e incluye el RUT, por lo que una fila marcada leída bloquearía la
    re-creación si el mismo usuario vuelve a ser asignado.

    Quien sigue siendo destinatario (p. ej. el asistente al cambiar el
    ejecutivo) no se toca: su alerta conserva su antigüedad y la dedupe_key
    existente evita duplicados al re-evaluar.
    """

    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alerta_renovacion: GenerarAlertaRenovacionPolizaUseCase,
    ) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_renovacion = generar_alerta_renovacion

    def ejecutar(self, id_cliente: int, ahora: datetime | None = None) -> None:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        destinatarios: set[str] = set()

        polizas = self.repositorio_notificaciones.obtener_polizas_alertables_renovacion(
            id_cliente=id_cliente
        )

        for poliza in polizas:
            actuales = set(self.generar_alerta_renovacion.resolver_destinatarios(poliza))
            destinatarios |= self._eliminar_obsoletas(poliza.numero_poliza, actuales)

            for notificacion in self.generar_alerta_renovacion.evaluar(poliza, ahora):
                if self.repositorio_notificaciones.registrar(notificacion):
                    if notificacion.rut_usuario:
                        destinatarios.add(notificacion.rut_usuario)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_actualizadas'},
            )

    def _eliminar_obsoletas(self, numero_poliza: str, actuales: set[str]) -> set[str]:
        """Elimina las alertas de renovación no leídas de la póliza cuyo
        destinatario ya no corresponde. Devuelve los RUTs eliminados."""
        eliminados: set[str] = set()

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_por_poliza(
            numero_poliza
        ):
            if notificacion.codigo_tipo not in TIPOS_ALERTA_RENOVACION:
                continue

            if notificacion.leida:
                continue

            if notificacion.rut_usuario in actuales:
                continue

            self.repositorio_notificaciones.eliminar(notificacion)

            if notificacion.rut_usuario:
                eliminados.add(notificacion.rut_usuario)

        return eliminados
