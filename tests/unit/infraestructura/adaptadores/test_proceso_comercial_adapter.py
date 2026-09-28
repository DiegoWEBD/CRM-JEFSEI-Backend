from datetime import datetime, timezone

import pytest

from app.infraestructura.proceso_comercial.adaptadores.dictrow_proceso_comercial_adapter import DictRowProcesoComercialAdapter


def _make_row(
    fecha_estimada_cierre=None,
    probabilidad_cierre_ejecutivo=None,
    probabilidad_cierre=0.05,
) -> dict:
    return {
        "id": 1,
        "id_prospecto": 10,
        "nombre_cliente": "Cliente Demo",
        "codigo_estado": "ESTADO_1",
        "nombre_estado": "En gestión",
        "fecha_registro_estado": datetime(2026, 9, 1, 10, 0, 0),
        "codigo_etapa": "ETAPA_1",
        "nombre_etapa": "Prospecto",
        "dias_limite_etapa": 30,
        "cerrado": False,
        "rut_ej_comercial": "12345678-9",
        "nombre_ej_comercial": "Juan Pérez",
        "rut_ej_evaluacion": None,
        "nombre_ej_evaluacion": None,
        "id_producto": 1,
        "codigo_producto": "VIDA-001",
        "nombre_producto": "Seguro de Vida",
        "fecha_estimada_cierre": fecha_estimada_cierre,
        "probabilidad_cierre_ejecutivo": probabilidad_cierre_ejecutivo,
        "probabilidad_cierre": probabilidad_cierre,
    }


@pytest.mark.unit
class TestDictRowProcesoComercialAdapter:

    def test_adapter_mapea_fecha_estimada_cierre(self):
        fecha = datetime(2026, 10, 15, 0, 0, 0, tzinfo=timezone.utc)
        proceso = DictRowProcesoComercialAdapter(_make_row(fecha)).to_proceso_comercial()

        assert proceso.fecha_estimada_cierre == fecha

    def test_adapter_mapea_fecha_estimada_cierre_null(self):
        proceso = DictRowProcesoComercialAdapter(
            _make_row(fecha_estimada_cierre=None)
        ).to_proceso_comercial()

        assert proceso.fecha_estimada_cierre is None

    def test_adapter_mapea_probabilidad_cierre_del_estado(self):
        proceso = DictRowProcesoComercialAdapter(
            _make_row(probabilidad_cierre=0.45)
        ).to_proceso_comercial()

        assert proceso.estado_actual.probabilidad_cierre == 0.45

    def test_adapter_mapea_probabilidad_cierre_ejecutivo(self):
        proceso = DictRowProcesoComercialAdapter(
            _make_row(probabilidad_cierre_ejecutivo=0.75)
        ).to_proceso_comercial()

        assert proceso.probabilidad_cierre_ejecutivo == 0.75

    def test_adapter_mapea_probabilidad_cierre_ejecutivo_null(self):
        proceso = DictRowProcesoComercialAdapter(
            _make_row(probabilidad_cierre_ejecutivo=None)
        ).to_proceso_comercial()

        assert proceso.probabilidad_cierre_ejecutivo is None
