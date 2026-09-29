from datetime import datetime, timedelta, timezone

from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla


# Instante de referencia para que los tests sean deterministas.
AHORA_REF = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)


def crear_notificacion_mock(
    id: int | None = 1,
    rut_usuario: str = "12345678-9",
    codigo_tipo: str = "SLA_POR_VENCER",
    nivel: str = "AVISO",
    titulo: str = "Oportunidad próximo al límite",
    mensaje: str = "La oportunidad está por alcanzar el límite del estado",
    entidad_tipo: str | None = "PROCESO_COMERCIAL",
    entidad_id: int | None = 1,
    url_destino: str | None = "/oportunidades?id=1",
    dedupe_key: str = "SLA_POR_VENCER:1:CONTACTO_INICIAL",
    leida: bool = False,
    fecha_leida: datetime | None = None,
    created_at: datetime | None = None,
) -> Notificacion:
    return Notificacion(
        id=id,
        rut_usuario=rut_usuario,
        codigo_tipo=codigo_tipo,
        nivel=nivel,
        titulo=titulo,
        mensaje=mensaje,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
        url_destino=url_destino,
        dedupe_key=dedupe_key,
        leida=leida,
        fecha_leida=fecha_leida,
        created_at=created_at or AHORA_REF,
    )


def crear_proceso_alertable_sla_mock(
    id_proceso_comercial: int = 1,
    codigo_estado: str = "CONTACTO_INICIAL",
    nombre_estado: str = "Contacto Inicial",
    nombre_etapa: str = "Prospección",
    nombre_prospecto: str | None = "Cliente Test",
    dias_transcurridos: int = 7,
    dias_limite: int | None = 10,
    dias_limite_etapa: int | None = 10,
    rol_responsable: str | None = "EJECUTIVO_COMERCIAL",
    rut_ej_comercial: str | None = "11111111-1",
    rut_ej_evaluacion: str | None = "22222222-2",
    cerrado: bool = False,
    ahora: datetime | None = None,
) -> ProcesoAlertableSla:
    if ahora is None:
        ahora = AHORA_REF

    return ProcesoAlertableSla(
        id_proceso_comercial=id_proceso_comercial,
        codigo_estado=codigo_estado,
        nombre_estado=nombre_estado,
        nombre_etapa=nombre_etapa,
        nombre_prospecto=nombre_prospecto,
        fecha_ingreso_estado=ahora - timedelta(days=dias_transcurridos),
        dias_limite=dias_limite,
        dias_limite_etapa=dias_limite_etapa,
        rol_responsable=rol_responsable,
        rut_ej_comercial=rut_ej_comercial,
        rut_ej_evaluacion=rut_ej_evaluacion,
        cerrado=cerrado,
    )
