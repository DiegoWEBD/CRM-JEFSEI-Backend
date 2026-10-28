from datetime import datetime, timezone

from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario
from tests.factories.linea_negocio_factory import crear_linea_negocio_mock
from tests.factories.usuario_factory import crear_usuario_mock


def crear_prospecto_mock(
    id: int = 1,
    rut_riesgo: str | None = "76543210-1",
    nombre_riesgo: str = "Condominio Los Pinos",
    ejecutivo_comercial_asignado: Usuario | None = None,
    ejecutivo_evaluacion_asignado: Usuario | None = None,
    informacion_completa: bool = True,
) -> Prospecto:
    return Prospecto(
        rut_riesgo=rut_riesgo,
        nombre_riesgo=nombre_riesgo,
        telefono_contacto=None,
        correo_contacto=None,
        direccion="Av. Principal 123",
        region="Metropolitana",
        comuna="Santiago",
        observaciones=None,
        linea_negocio=crear_linea_negocio_mock(),
        registrado_por=crear_usuario_mock(),
        ejecutivo_comercial_asignado=ejecutivo_comercial_asignado,
        ejecutivo_evaluacion_asignado=ejecutivo_evaluacion_asignado,
        informacion_completa=informacion_completa,
        id=id,
    )


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
