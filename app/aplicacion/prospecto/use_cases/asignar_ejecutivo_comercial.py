from datetime import datetime, timezone

from app.aplicacion.notificacion.use_cases.generar_alerta_cierre_estimado import (
    GenerarAlertaCierreEstimadoUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoComercialUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos, 
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_procesos: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alerta_cierre: GenerarAlertaCierreEstimadoUseCase,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_procesos = repositorio_procesos
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_cierre = generar_alerta_cierre

    def ejecutar(self, id_prospecto: int, rut_ej_comercial: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        rut_anterior = prospecto.ejecutivo_comercial_asignado.rut if prospecto.ejecutivo_comercial_asignado else None

        if rut_ej_comercial is not None:
            usuario = self.repositorio_usuarios.buscar(rut_ej_comercial)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.ejecutivo_comercial_asignado = usuario
        else:
            prospecto.ejecutivo_comercial_asignado = None

        self.repositorio_prospectos.asignar_ejecutivo_comercial(prospecto, asignado_por)

        # Con cambio de ejecutivo, las alertas de cierre del anterior dejan de
        # ser relevantes: se marcan leídas y se genera la del nuevo responsable
        # (creada en este momento, no transferida). En desasignación no se crea
        # nada (sin destinatario), pero las previas quedan leídas.
        if rut_anterior != rut_ej_comercial:
            self._refrescar_alertas_de_cierre(id_prospecto)

        if rut_ej_comercial is not None:
            hub.publicar_desde_hilo(
                [rut_ej_comercial],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'asignacion_ejecutivo'},
            )

        if rut_anterior and rut_anterior != rut_ej_comercial:
            hub.publicar_desde_hilo(
                [rut_anterior],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'desasignacion_ejecutivo'},
            )

    def _refrescar_alertas_de_cierre(self, id_prospecto: int) -> None:
        ahora = datetime.now(tz=timezone.utc)
        destinatarios: list[str] = []

        procesos = self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=id_prospecto,
            abiertos=True,
        )

        for proceso in procesos:
            for notificacion in self.repositorio_notificaciones.buscar_notificaciones_proceso_comercial(
                proceso.id
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

            notificacion_creada = self.generar_alerta_cierre.ejecutar(
                id_proceso_comercial=proceso.id,
                ahora=ahora,
            )
            if notificacion_creada is not None and notificacion_creada.rut_usuario:
                destinatarios.append(notificacion_creada.rut_usuario)

        if len(destinatarios) > 0:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_fecha_cierre_actualizadas'},
            )
