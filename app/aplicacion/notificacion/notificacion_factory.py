from datetime import datetime, timezone

from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.tipos_alerta import TIPO_ASIGNACION, TIPO_DESASIGNACION


class NotificacionFactory:
    """Construye las notificaciones del sistema.

    Única dueña del formato de títulos, mensajes y dedupe_key de cada tipo:
    los casos de uso deciden qué crear y cuándo; esta fábrica sabe cómo.
    """

    @staticmethod
    def crear_notificacion_asignacion(
        *,
        rut_asignado: str | None,
        detalle_asignacion: str,
        entidad_tipo: str,
        entidad_id: int,
        nombre_entidad: str,
        id_prospecto: int,
        ahora: datetime | None = None,
    ) -> Notificacion:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        tipo_entidad = f'{entidad_tipo.lower()} ' if entidad_tipo else ''

        return Notificacion(
            id=None,
            rut_usuario=rut_asignado,
            codigo_tipo=TIPO_ASIGNACION,
            nivel='INFO',
            titulo=f'Asignación de {detalle_asignacion}',
            mensaje=f'Se le ha asignado la {detalle_asignacion} del {tipo_entidad}{nombre_entidad}.',
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
    def crear_notificacion_desasignacion(
        *,
        rut_desasignado: str | None,
        detalle_asignacion: str,
        entidad_tipo: str,
        entidad_id: int,
        nombre_entidad: str,
        id_prospecto: int,
        ahora: datetime | None = None,
    ) -> Notificacion:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        tipo_entidad = f'{entidad_tipo.lower()} ' if entidad_tipo else ''

        return Notificacion(
            id=None,
            rut_usuario=rut_desasignado,
            codigo_tipo=TIPO_DESASIGNACION,
            nivel='INFO',
            titulo=f'Desasignación de {detalle_asignacion}',
            mensaje=f'Se le ha desasignado la {detalle_asignacion} del {tipo_entidad}{nombre_entidad}.',
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            id_prospecto=id_prospecto,
            dedupe_key=f'{TIPO_DESASIGNACION}:{entidad_tipo}:{entidad_id}:{detalle_asignacion}:{ahora.isoformat()}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
            leible=True,
        )

    @staticmethod
    def crear_alerta_sla(
        *,
        rut_usuario: str | None,
        codigo_tipo: str,
        nivel: str,
        titulo: str,
        mensaje: str,
        id_proceso_comercial: int,
        id_prospecto: int,
        codigo_estado: str,
        ahora: datetime | None = None,
    ) -> Notificacion:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        return Notificacion(
            id=None,
            rut_usuario=rut_usuario,
            codigo_tipo=codigo_tipo,
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            entidad_tipo='PROCESO_COMERCIAL',
            entidad_id=id_proceso_comercial,
            id_prospecto=id_prospecto,
            # Dedupe estable (sin timestamp): el on conflict del repositorio
            # evita duplicados entre corridas del scheduler.
            dedupe_key=f'{codigo_tipo}:{id_proceso_comercial}:{codigo_estado}:{rut_usuario}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
            leible=False,
        )

    @staticmethod
    def crear_alerta_cierre(
        *,
        rut_usuario: str | None,
        codigo_tipo: str,
        nivel: str,
        titulo: str,
        mensaje: str,
        id_proceso_comercial: int,
        id_prospecto: int,
        ahora: datetime | None = None,
    ) -> Notificacion:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        return Notificacion(
            id=None,
            rut_usuario=rut_usuario,
            codigo_tipo=codigo_tipo,
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            entidad_tipo='PROCESO_COMERCIAL',
            entidad_id=id_proceso_comercial,
            id_prospecto=id_prospecto,
            dedupe_key=f'{codigo_tipo}:{id_proceso_comercial}:{rut_usuario}:{ahora.isoformat()}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
            leible=False,
        )
