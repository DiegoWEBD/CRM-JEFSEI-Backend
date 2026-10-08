from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.use_cases.generar_alerta_cierre_estimado import (
    GenerarAlertaCierreEstimadoUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class ActualizarFechaEstimadaCierreUseCase:

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alerta_cierre: GenerarAlertaCierreEstimadoUseCase,
    ):
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_cierre = generar_alerta_cierre

    def ejecutar(self, id: int, fecha_estimada_cierre: datetime | None, usuario: Usuario):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')

        if not self.authorization_service.usuario_puede_actualizar_fecha_estimada_cierre(
            rut_usuario=usuario.rut,
            id_proceso_comercial=id,
        ):
            raise UsuarioNoAutorizadoException('No autorizado para actualizar la fecha estimada de cierre')

        if proceso.cerrado:
            raise ConflictoEnAccionException('La oportunidad está cerrada')

        self.repositorio_procesos_comerciales.actualizar_fecha_estimada_cierre(
            id=id,
            fecha=fecha_estimada_cierre,
        )

        # El flujo de alertas solo aplica cuando la fecha cambió: no se marca
        # nada ni se re-evalúa por un guardado sin cambios (no refresca alertas
        # ya leídas).
        if proceso.fecha_estimada_cierre == fecha_estimada_cierre:
            return

        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self._marcar_alertas_de_cierre_leidas(id, ahora)

        notificacion_creada = self.generar_alerta_cierre.ejecutar(
            id_proceso_comercial=id,
            ahora=ahora,
        )
        if notificacion_creada is not None and notificacion_creada.rut_usuario:
            destinatarios.append(notificacion_creada.rut_usuario)

        if len(destinatarios) > 0:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_fecha_cierre_actualizadas'},
            )

    def _marcar_alertas_de_cierre_leidas(self, id_proceso_comercial: int, ahora: datetime) -> list[str]:
        """Marca leídas las alertas de cierre no leídas del proceso.

        Con la nueva fecha, las alertas previas (próximo / vencida) dejan de
        ser relevantes. Devuelve los RUTs afectados para refrescarlos por socket.
        """
        destinatarios: list[str] = []

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_proceso_comercial(
            id_proceso_comercial
        ):
            if notificacion.codigo_tipo not in TIPOS_ALERTA_FECHA:
                continue

            if notificacion.leida:
                continue

            notificacion.leida = True
            notificacion.fecha_leida = ahora
            self.repositorio_notificaciones.actualizar(notificacion)

            if notificacion.rut_usuario:
                destinatarios.append(notificacion.rut_usuario)

        return destinatarios
