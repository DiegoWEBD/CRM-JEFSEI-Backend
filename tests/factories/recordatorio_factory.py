from datetime import datetime, timezone

from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario
from app.dominio.recordatorio.recordatorio_renovacion_poliza.recordatorio_renovacion_poliza import RecordatorioRenovacionPoliza
from app.dominio.recordatorio.recordatorio_cobranza_cuota_poliza.recordatorio_cobranza_cuota_poliza import RecordatorioCobranzaCuotaPoliza


def crear_recordatorio_usuario_mock(
    id: int = 1,
    id_prospecto: int | None = 1,
    nombre_prospecto: str | None = "Prospecto Test",
    titulo: str = "Recordatorio Usuario",
    detalle: str | None = "Detalle test",
    completado: bool = False,
    tipo_gestion: str = "llamada",
    prioridad: str = "alta",
    fecha_recordatorio: datetime | None = None,
) -> RecordatorioUsuario:
    if fecha_recordatorio is None:
        fecha_recordatorio = datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
    return RecordatorioUsuario(
        id=id,
        id_prospecto=id_prospecto,
        nombre_prospecto=nombre_prospecto,
        titulo=titulo,
        detalle=detalle,
        completado=completado,
        tipo_gestion=tipo_gestion,
        prioridad=prioridad,
        fecha_recordatorio=fecha_recordatorio,
    )


def crear_recordatorio_renovacion_mock(
    id: int = 2,
    numero_poliza: str = "POL-001",
    titulo: str = "Recordatorio Renovacion",
    detalle: str | None = "Detalle renovacion",
    completado: bool = False,
    tipo_gestion: str = "correo",
    prioridad: str = "media",
    fecha_recordatorio: datetime | None = None,
) -> RecordatorioRenovacionPoliza:
    if fecha_recordatorio is None:
        fecha_recordatorio = datetime(2026, 9, 1, 11, 0, 0, tzinfo=timezone.utc)
    return RecordatorioRenovacionPoliza(
        id=id,
        numero_poliza=numero_poliza,
        titulo=titulo,
        detalle=detalle,
        completado=completado,
        tipo_gestion=tipo_gestion,
        prioridad=prioridad,
        fecha_recordatorio=fecha_recordatorio,
    )


def crear_recordatorio_cobranza_mock(
    id: int = 3,
    id_prospecto: int | None = 2,
    nombre_prospecto: str | None = "Prospecto Cobranza",
    numero_poliza: str = "POL-002",
    titulo: str = "Recordatorio Cobranza",
    detalle: str | None = "Detalle cobranza",
    completado: bool = False,
    tipo_gestion: str = "mensaje",
    prioridad: str = "baja",
    fecha_recordatorio: datetime | None = None,
) -> RecordatorioCobranzaCuotaPoliza:
    if fecha_recordatorio is None:
        fecha_recordatorio = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    return RecordatorioCobranzaCuotaPoliza(
        id=id,
        id_prospecto=id_prospecto,
        nombre_prospecto=nombre_prospecto,
        numero_poliza=numero_poliza,
        titulo=titulo,
        detalle=detalle,
        completado=completado,
        tipo_gestion=tipo_gestion,
        prioridad=prioridad,
        fecha_recordatorio=fecha_recordatorio,
    )
