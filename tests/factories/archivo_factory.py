from datetime import datetime, timezone

from app.dominio.archivo.archivo import Archivo


def crear_archivo_mock(
    id: int | None = 1,
    id_prospecto: int = 7,
    nombre_almacenado: str = "prospecto_7_abc123.pdf",
    nombre_original: str = "documento.pdf",
    tipo_contenido: str = "application/pdf",
    tamano_bytes: int = 1024,
    rut_subido_por: str = "11111111-1",
    created_at: datetime | None = None,
) -> Archivo:
    if created_at is None:
        created_at = datetime(2026, 11, 24, 10, 0, 0, tzinfo=timezone.utc)
    return Archivo(
        id=id,
        id_prospecto=id_prospecto,
        nombre_almacenado=nombre_almacenado,
        nombre_original=nombre_original,
        tipo_contenido=tipo_contenido,
        tamano_bytes=tamano_bytes,
        rut_subido_por=rut_subido_por,
        created_at=created_at,
    )
