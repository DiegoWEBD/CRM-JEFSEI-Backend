from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.aplicacion.auditoria.use_cases.obtener_registros_auditoria import (
    ObtenerRegistrosAuditoriaUseCase,
)
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria
from tests.factories.auditoria_factory import crear_registro_auditoria_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioAuditoria)


@pytest.fixture
def use_case(repositorio_mock):
    return ObtenerRegistrosAuditoriaUseCase(repositorio_mock)


@pytest.mark.unit
class TestObtenerRegistrosAuditoriaUseCase:

    def test_ejecutar_paginado_delega_en_repositorio(self, use_case, repositorio_mock):
        registros = [crear_registro_auditoria_mock()]
        repositorio_mock.obtener_paginados.return_value = (registros, 1)
        fecha_desde = datetime(2026, 9, 1)
        fecha_hasta = datetime(2026, 9, 30)

        datos, total = use_case.ejecutar_paginado(
            categoria="AUTENTICACION",
            evento="LOGIN_EXITOSO",
            rut_usuario="12345678-9",
            ip_origen="200.10.20.30",
            entidad_tipo="prospectos",
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            texto_busqueda="juan",
            pagina=2,
            tamano_pagina=15,
        )

        assert datos == registros
        assert total == 1
        kwargs = repositorio_mock.obtener_paginados.call_args.kwargs
        assert kwargs["categoria"] == "AUTENTICACION"
        assert kwargs["evento"] == "LOGIN_EXITOSO"
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["ip_origen"] == "200.10.20.30"
        assert kwargs["entidad_tipo"] == "prospectos"
        assert kwargs["fecha_desde"] == fecha_desde
        assert kwargs["fecha_hasta"] == fecha_hasta
        assert kwargs["texto_busqueda"] == "juan"
        assert kwargs["pagina"] == 2
        assert kwargs["tamano_pagina"] == 15

    def test_ejecutar_exportacion_limita_resultados(self, use_case, repositorio_mock):
        registros = [crear_registro_auditoria_mock()]
        repositorio_mock.obtener_paginados.return_value = (registros, 1)

        datos = use_case.ejecutar_exportacion(
            categoria=None,
            evento=None,
            rut_usuario=None,
            ip_origen=None,
            entidad_tipo=None,
            fecha_desde=None,
            fecha_hasta=None,
            texto_busqueda=None,
            limite=500,
        )

        assert datos == registros
        kwargs = repositorio_mock.obtener_paginados.call_args.kwargs
        assert kwargs["pagina"] == 1
        assert kwargs["tamano_pagina"] == 500
