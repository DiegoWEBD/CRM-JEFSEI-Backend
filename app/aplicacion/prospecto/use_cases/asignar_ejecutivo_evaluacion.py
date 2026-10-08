from app.aplicacion.notificacion.notificacion_factory import NotificacionFactory
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import ROL_EJECUTIVO_EVALUACION_PROYECTOS
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoEvaluacionUseCase:
    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_notificaciones: RepositorioNotificaciones,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, id_prospecto: int, rut_ej_evaluacion: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto or not prospecto.id:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        rut_anterior = prospecto.ejecutivo_evaluacion_asignado.rut if prospecto.ejecutivo_evaluacion_asignado else None

        if rut_ej_evaluacion is not None:
            usuario = self.repositorio_usuarios.buscar(rut_ej_evaluacion)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.ejecutivo_evaluacion_asignado = usuario
        else:
            prospecto.ejecutivo_evaluacion_asignado = None

        self.repositorio_prospectos.asignar_ejecutivo_evaluacion_proyectos(prospecto, asignado_por)

        if rut_anterior != rut_ej_evaluacion:
            # Las alertas SLA no leídas del prospecto cuyo estado siguiente sea
            # de la EVALUACIÓN cambian de destinatario.
            self._reasignar_alertas_sla(id_prospecto, rut_ej_evaluacion)

        # Notificaciones de asignación/desasignación: en cada invocación con RUT
        # destino (asignación) y solo al cambiar de RUT (desasignación).
        if rut_ej_evaluacion is not None:
            self.repositorio_notificaciones.registrar(
                NotificacionFactory.crear_notificacion_asignacion(
                    rut_asignado=rut_ej_evaluacion,
                    detalle_asignacion='evaluación técnica',
                    entidad_tipo='PROSPECTO',
                    entidad_id=prospecto.id,
                    nombre_entidad=prospecto.nombre_riesgo or f'#{prospecto.id}',
                    id_prospecto=prospecto.id,
                )
            )

        if rut_anterior and rut_anterior != rut_ej_evaluacion:
            self.repositorio_notificaciones.registrar(
                NotificacionFactory.crear_notificacion_desasignacion(
                    rut_desasignado=rut_anterior,
                    detalle_asignacion='evaluación técnica',
                    entidad_tipo='PROSPECTO',
                    entidad_id=prospecto.id,
                    nombre_entidad=prospecto.nombre_riesgo or f'#{prospecto.id}',
                    id_prospecto=prospecto.id,
                )
            )

        if rut_ej_evaluacion is not None:
            hub.publicar_desde_hilo(
                [rut_ej_evaluacion],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'asignacion_ejecutivo'},
            )

        if rut_anterior and rut_anterior != rut_ej_evaluacion:
            hub.publicar_desde_hilo(
                [rut_anterior],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'desasignacion_ejecutivo'},
            )

    def _reasignar_alertas_sla(self, id_prospecto: int, nuevo_rut: str | None) -> None:
        """Cambia el destinatario de las alertas SLA no leídas del prospecto.

        Solo se tocan las alertas cuyo destinatario actual difiera del nuevo.
        Publica (previos | nuevos) con motivo 'destinatarios_reasignados'.
        """
        previos: set[str] = set()
        hubo_cambios = False

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_sla_por_rol(
            id_prospecto, ROL_EJECUTIVO_EVALUACION_PROYECTOS
        ):
            if notificacion.rut_usuario == nuevo_rut:
                continue

            if notificacion.rut_usuario:
                previos.add(notificacion.rut_usuario)

            notificacion.rut_usuario = nuevo_rut
            self.repositorio_notificaciones.actualizar(notificacion)
            hubo_cambios = True

        nuevos = {nuevo_rut} if (hubo_cambios and nuevo_rut) else set()

        if previos | nuevos:
            hub.publicar_desde_hilo(
                previos | nuevos,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'destinatarios_reasignados'},
            )