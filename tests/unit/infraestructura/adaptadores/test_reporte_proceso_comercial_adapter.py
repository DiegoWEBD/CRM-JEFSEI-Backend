from datetime import datetime, timezone

import pytest

from app.infraestructura.proceso_comercial.adaptadores.dictrow_reporte_proceso_comercial_adapter import (
    DictRowReporteProcesoComercialAdapter,
)
from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial import ReportesProcesoComercialDTO
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import (
    ReportesProcesoComercialCerradoDTO,
)


def _make_row(
    cerrado=False,
    dias_limite_transicion=10,
    fecha_ingreso_estado=datetime(2026, 9, 25, 10, 0, 0, tzinfo=timezone.utc),
    dias_transcurridos=6,
    porcentaje_sla_consumido=0.6,
    estado_semaforo="VERDE",
    dias_restantes=4,
    dias_atraso=-4,
    mensaje_semaforo="Dentro del plazo (6 de 10 días)",
) -> dict:
    return {
        "id": 1,
        "id_prospecto": 10,
        "nombre_cliente": "Cliente Demo",
        "codigo_estado": "ESTUDIO_DISPONIBLE",
        "nombre_estado": "Estudio disponible",
        "fecha_registro_estado": datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc),
        "codigo_etapa": "ETAPA_1",
        "nombre_etapa": "Evaluación",
        "cerrado": cerrado,
        "descartado": False,
        "rut_ej_comercial": "12345678-9",
        "nombre_ej_comercial": "Juan Pérez",
        "rut_ej_evaluacion": None,
        "nombre_ej_evaluacion": None,
        "id_producto": 1,
        "codigo_producto": "VIDA-001",
        "nombre_producto": "Seguro de Vida",
        "renovacion": False,
        "fecha_ingreso_estado": fecha_ingreso_estado,
        "dias_transcurridos": dias_transcurridos,
        "porcentaje_sla_consumido": porcentaje_sla_consumido,
        "estado_semaforo": estado_semaforo,
        "dias_limite_transicion": dias_limite_transicion,
        "dias_restantes": dias_restantes,
        "dias_atraso": dias_atraso,
        "mensaje_semaforo": mensaje_semaforo,
    }


@pytest.mark.unit
class TestDictRowReporteProcesoComercialAdapter:

    def test_mapea_fecha_ingreso_estado_y_dias_limite_de_la_transicion(self):
        reporte = DictRowReporteProcesoComercialAdapter(_make_row()).to_reporte()

        assert isinstance(reporte, ReportesProcesoComercialDTO)
        assert reporte.fecha_ingreso_estado == "2026-09-25T10:00:00+00:00"
        assert reporte.dias_limite == 10
        assert reporte.dias_transcurridos == 6
        assert reporte.estado_semaforo == EstadoSemaforo.VERDE

    def test_mapea_dias_limite_null_cuando_no_hay_transicion_principal(self):
        reporte = DictRowReporteProcesoComercialAdapter(
            _make_row(dias_limite_transicion=None)
        ).to_reporte()

        assert reporte.dias_limite is None

    def test_proceso_cerrado_devuelve_reporte_cerrado(self):
        reporte = DictRowReporteProcesoComercialAdapter(_make_row(cerrado=True)).to_reporte()

        assert isinstance(reporte, ReportesProcesoComercialCerradoDTO)
        assert reporte.estado_semaforo == EstadoSemaforo.NO_APLICA

    def test_proceso_abierto_sin_sla_devuelve_campos_null(self):
        """Estado sin transición principal con límite -> NO_APLICA con campos en None.

        Regresión: el adaptador hacía float(None) y lanzaba TypeError.
        """
        reporte = DictRowReporteProcesoComercialAdapter(
            _make_row(
                estado_semaforo="NO_APLICA",
                fecha_ingreso_estado=None,
                dias_transcurridos=None,
                porcentaje_sla_consumido=None,
                dias_limite_transicion=None,
                dias_restantes=None,
                dias_atraso=None,
                mensaje_semaforo=None,
            )
        ).to_reporte()

        assert isinstance(reporte, ReportesProcesoComercialDTO)
        assert reporte.estado_semaforo == EstadoSemaforo.NO_APLICA
        assert reporte.fecha_ingreso_estado is None
        assert reporte.dias_transcurridos is None
        assert reporte.porentaje_sla_consumido is None
        assert reporte.dias_limite is None
        assert reporte.dias_restantes is None
        assert reporte.dias_atraso is None
        assert reporte.mensaje_semaforo is None
