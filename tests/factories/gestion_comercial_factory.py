from datetime import datetime, timezone

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial


def crear_gestion_comercial_mock(
    id: int = 1,
    tipo: str = 'llamada',
    rut_usuario: str = '11111111-1',
    nombre_ejecutivo: str | None = 'Ejecutivo Test',
    id_prospecto: int = 7,
    nombre_cliente: str | None = 'Cliente Test',
    titulo: str = 'Gestion de prueba',
    estado_contacto: str | None = None,
    observacion: str | None = 'Observacion de prueba',
    created_at: datetime | None = None,
    fecha_gestion: datetime | None = None,
) -> GestionComercial:
    if created_at is None:
        created_at = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
    if fecha_gestion is None:
        fecha_gestion = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
    return GestionComercial(
        id=id,
        tipo=tipo,
        rut_usuario=rut_usuario,
        nombre_ejecutivo=nombre_ejecutivo,
        id_prospecto=id_prospecto,
        nombre_cliente=nombre_cliente,
        titulo=titulo,
        estado_contacto=estado_contacto,
        observacion=observacion,
        created_at=created_at,
        fecha_gestion=fecha_gestion,
    )
