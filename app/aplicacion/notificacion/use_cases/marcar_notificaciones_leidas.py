from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class MarcarNotificacionesLeidasUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, rut_usuario: str) -> int:
        total = self.repositorio_notificaciones.marcar_todas_leidas(
            rut_usuario=rut_usuario
        )

        # Solo avisa si algo cambió: el resto de pestañas invalidaría sus
        # queries (contador, campana y grupos del home) para nada.
        if total > 0:
            hub.publicar_desde_hilo(
                [rut_usuario],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'marcadas_leidas'},
            )

        return total
