from datetime import datetime, timezone

from app.aplicacion.notificacion.notificacion_factory import NotificacionFactory
from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
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
        generar_alertas_sla: GenerarAlertasSlaUseCase,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alertas_sla = generar_alertas_sla

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
            # de la EVALUACIÓN se eliminan y se re-evalúan al tiro: el nuevo
            # responsable la recibe creada ahora, no transferida.
            self._refrescar_alertas_sla(id_prospecto, rut_ej_evaluacion)

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

    def _refrescar_alertas_sla(self, id_prospecto: int, nuevo_rut: str | None) -> None:
        """Elimina las alertas SLA no leídas del rol que ya no corresponden y las
        re-evalúa al tiro.

        No se reasignan (transferir la fila con su antigüedad confundía al nuevo
        responsable con alertas "creadas hace días" y dejaba la dedupe_key con el
        RUT anterior, con lo que el scheduler duplicaba la alerta después). Al
        eliminar y recrear, el nuevo destinatario la ve creada ahora y las de
        quienes siguen siendo responsables no se tocan. En desasignación no se
        crea nada (sin destinatario), pero las previas quedan eliminadas.
        """
        ahora = datetime.now(tz=timezone.utc)
        destinatarios: set[str] = set()

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_sla_por_rol(
            id_prospecto, ROL_EJECUTIVO_EVALUACION_PROYECTOS
        ):
            # Las ya dirigidas al nuevo destinatario siguen vigentes.
            if nuevo_rut is not None and notificacion.rut_usuario == nuevo_rut:
                continue

            if notificacion.rut_usuario:
                destinatarios.add(notificacion.rut_usuario)

            self.repositorio_notificaciones.eliminar(notificacion)

        # Re-evaluación inmediata: crea la alerta del nuevo responsable con
        # created_at actual (idempotente: las de otros responsables ya existen).
        self.generar_alertas_sla.ejecutar(ahora=ahora)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'sla_reevaluado'},
            )