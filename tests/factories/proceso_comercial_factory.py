from datetime import datetime

from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from tests.factories.producto_factory import crear_producto_mock


def crear_proceso_comercial_mock(
    id: int = 1,
    id_prospecto: int = 1,
    nombre_cliente: str = "Cliente Demo",
    cerrado: bool = False,
    ejecutivo_comercial=None,
    ejecutivo_evaluacion=None,
    fecha_estimada_cierre: datetime | None = None,
) -> ProcesoComercial:
    etapa = EtapaProcesoComercial(
        codigo="ETAPA_1",
        nombre="Prospecto",
        sigiuente_etapa=None,
        dias_limite=30,
    )
    estado = EstadoInformativoProcesoComercial(
        codigo="ESTADO_1",
        etapa=etapa,
        nombre="En gestión",
        fecha_registro=datetime(2026, 9, 1, 10, 0, 0),
    )
    return ProcesoComercial(
        id=id,
        ejecutivo_comercial=ejecutivo_comercial,
        ejecutivo_evaluacion=ejecutivo_evaluacion,
        id_prospecto=id_prospecto,
        nombre_cliente=nombre_cliente,
        producto=crear_producto_mock(),
        estado_actual=estado,
        cerrado=cerrado,
        fecha_estimada_cierre=fecha_estimada_cierre,
    )
