from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class MarcarNotificacionLeidaUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, id_notificacion: int, rut_usuario: str) -> None:
        notificacion = self.repositorio_notificaciones.buscar(
            id_notificacion=id_notificacion,
        )

        if notificacion is None:
            raise RecursoNoEncontradoException('Notificación no encontrada')

        if not notificacion.leible:
            raise ConflictoEnAccionException('La notificación no es leíble')

        if notificacion.leida:
            return

        self.repositorio_notificaciones.marcar_leida(
            id_notificacion=id_notificacion,
            rut_usuario=rut_usuario,
        )

        hub.publicar_desde_hilo(
            [rut_usuario],
            {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'marcadas_leidas'},
        )
