from datetime import datetime, timezone


def crear_prospecto_dict(
    id: int = 1,
    nombre: str = "Condominio Los Pinos",
    rut: str = "12345678-9",
    id_comuna: int = 1,
    direccion: str = "Av. Principal 123",
    id_estado: str = "PENDIENTE",
    id_ejecutivo_comercial: str | None = None,
    id_ejecutivo_evaluacion: str | None = None,
    id_ejecutivo_cobranza: str | None = None,
    id_administrador: int | None = None,
    fecha_registro: datetime | None = None,
) -> dict:
    if fecha_registro is None:
        fecha_registro = datetime.now(tz=timezone.utc)
    return {
        "id": id,
        "nombre": nombre,
        "rut": rut,
        "id_comuna": id_comuna,
        "direccion": direccion,
        "id_estado": id_estado,
        "id_ejecutivo_comercial": id_ejecutivo_comercial,
        "id_ejecutivo_evaluacion": id_ejecutivo_evaluacion,
        "id_ejecutivo_cobranza": id_ejecutivo_cobranza,
        "id_administrador": id_administrador,
        "fecha_registro": fecha_registro,
    }
