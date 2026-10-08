from datetime import datetime, timezone

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.notificacion.use_cases.generar_alerta_cierre_estimado import (
    GenerarAlertaCierreEstimadoUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import (
    ROL_EJECUTIVO_COMERCIAL,
    TIPOS_ALERTA_FECHA,
    TIPO_ASIGNACION,
    TIPO_DESASIGNACION,
)
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
        servicio_alertas: ServicioAlertasProceso,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_procesos = repositorio_procesos
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alerta_cierre = generar_alerta_cierre
        self.servicio_alertas = servicio_alertas

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

        if rut_anterior != rut_ej_comercial:
            # Las alertas SLA no leídas del prospecto cuyo estado siguiente sea
            # del EJECUTIVO_COMERCIAL cambian de destinatario.
            self._reasignar_alertas_sla(id_prospecto, rut_ej_comercial)

            # Con cambio de ejecutivo, las alertas de cierre del anterior dejan de
            # ser relevantes: se marcan leídas y se genera la del nuevo responsable
            # (creada en este momento, no transferida). En desasignación no se crea
            # nada (sin destinatario), pero las previas quedan leídas.
            self._refrescar_alertas_de_cierre(id_prospecto)

        # Notificaciones de asignación/desasignación: en cada invocación con RUT
        # destino (asignación) y solo al cambiar de RUT (desasignación).
        if rut_ej_comercial is not None:
            self.repositorio_notificaciones.registrar(
                self._notificacion_asignacion(
                    rut_asignado=rut_ej_comercial,
                    detalle_asignacion='gestión comercial',
                    entidad_tipo='PROSPECTO',
                    entidad_id=prospecto.id,
                    nombre_entidad=prospecto.nombre_riesgo or f'#{prospecto.id}',
                    id_prospecto=prospecto.id,
                )
            )

        if rut_anterior and rut_anterior != rut_ej_comercial:
            self.repositorio_notificaciones.registrar(
                self._notificacion_desasignacion(
                    rut_desasignado=rut_anterior,
                    detalle_asignacion='gestión comercial',
                    entidad_tipo='PROSPECTO',
                    entidad_id=prospecto.id,
                    nombre_entidad=prospecto.nombre_riesgo or f'#{prospecto.id}',
                    id_prospecto=prospecto.id,
                )
            )

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

    def _reasignar_alertas_sla(self, id_prospecto: int, nuevo_rut: str | None) -> None:
        """Cambia el destinatario de las alertas SLA no leídas del prospecto.

        Solo se tocan las alertas cuyo destinatario actual difiera del nuevo.
        Publica (previos | nuevos) con motivo 'destinatarios_reasignados'.
        """
        previos: set[str] = set()
        hubo_cambios = False

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_sla_por_rol(
            id_prospecto, ROL_EJECUTIVO_COMERCIAL
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

    def _refrescar_alertas_de_cierre(self, id_prospecto: int) -> None:
        ahora = datetime.now(tz=timezone.utc)
        destinatarios: list[str] = []

        procesos = self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=id_prospecto,
            abiertos=True,
        )

        for proceso in procesos:
            destinatarios.extend(
                self.servicio_alertas.marcar_leidas(proceso.id, TIPOS_ALERTA_FECHA, ahora)
            )

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

    @staticmethod
    def _notificacion_asignacion(
        *,
        rut_asignado: str,
        detalle_asignacion: str,
        entidad_tipo: str,
        entidad_id: int,
        nombre_entidad: str,
        id_prospecto: int | None,
    ) -> Notificacion:
        ahora = datetime.now(tz=timezone.utc)

        return Notificacion(
            id=None,
            rut_usuario=rut_asignado,
            codigo_tipo=TIPO_ASIGNACION,
            nivel='INFO',
            titulo=f'Asignación de {detalle_asignacion}',
            mensaje=f'Se le ha asignado la {detalle_asignacion} del {entidad_tipo.lower()} {nombre_entidad}.',
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            id_prospecto=id_prospecto,
            dedupe_key=f'{TIPO_ASIGNACION}:{entidad_tipo}:{entidad_id}:{detalle_asignacion}:{ahora.isoformat()}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
            leible=True,
        )

    @staticmethod
    def _notificacion_desasignacion(
        *,
        rut_desasignado: str,
        detalle_asignacion: str,
        entidad_tipo: str,
        entidad_id: int,
        nombre_entidad: str,
        id_prospecto: int | None,
    ) -> Notificacion:
        ahora = datetime.now(tz=timezone.utc)

        return Notificacion(
            id=None,
            rut_usuario=rut_desasignado,
            codigo_tipo=TIPO_DESASIGNACION,
            nivel='INFO',
            titulo=f'Desasignación de {detalle_asignacion}',
            mensaje=f'Se le ha desasignado la {detalle_asignacion} del {entidad_tipo.lower()} {nombre_entidad}.',
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            id_prospecto=id_prospecto,
            dedupe_key=f'{TIPO_DESASIGNACION}:{entidad_tipo}:{entidad_id}:{detalle_asignacion}:{ahora.isoformat()}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
            leible=True,
        )
