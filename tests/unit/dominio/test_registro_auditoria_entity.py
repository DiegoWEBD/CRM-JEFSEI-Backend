import time
from datetime import datetime, timezone

import pytest

from app.dominio.auditoria.eventos_auditoria import CategoriaAuditoria, EventoAuditoria, ResultadoAuditoria
from app.dominio.auditoria.registro_auditoria import RegistroAuditoria


def _crear_registro(**kwargs) -> RegistroAuditoria:
    defaults = dict(
        categoria=CategoriaAuditoria.ACCION_NEGOCIO,
        evento=EventoAuditoria.CREAR,
        resultado=ResultadoAuditoria.EXITO,
        ip_origen="200.10.20.30",
    )
    defaults.update(kwargs)
    return RegistroAuditoria(**defaults)


@pytest.mark.unit
class TestRegistroAuditoriaEntity:

    def test_fecha_registro_es_el_momento_de_creacion(self):
        antes = datetime.now(tz=timezone.utc)

        registro = _crear_registro()

        despues = datetime.now(tz=timezone.utc)
        assert antes <= registro.fecha_registro <= despues

    def test_fecha_registro_no_se_comparte_entre_instancias(self):
        registro_1 = _crear_registro()
        time.sleep(0.01)
        registro_2 = _crear_registro()

        assert registro_2.fecha_registro > registro_1.fecha_registro

    def test_fecha_registro_explicita_se_respeta(self):
        fecha_esperada = datetime(2026, 9, 30, 9, 45, tzinfo=timezone.utc)

        registro = _crear_registro(fecha_registro=fecha_esperada)

        assert registro.fecha_registro == fecha_esperada

    def test_fecha_registro_no_es_el_momento_de_importacion(self):
        # Regresión del bug: el default evaluado al importar el módulo dejaba
        # todos los eventos con la misma marca de tiempo.
        marca_importacion = datetime.now(tz=timezone.utc)

        time.sleep(0.01)

        registro = _crear_registro()

        assert registro.fecha_registro > marca_importacion
