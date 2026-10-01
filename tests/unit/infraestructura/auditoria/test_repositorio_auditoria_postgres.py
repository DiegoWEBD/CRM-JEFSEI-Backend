from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.auditoria.repositorio_auditoria_postgres import (
    RepositorioAuditoriaPostgres,
)
from tests.factories.auditoria_factory import (
    crear_fila_registro_auditoria_mock,
    crear_registro_auditoria_mock,
)


def _conexion_mock(rows=None, row=None):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    if rows is not None:
        cursor.fetchall.return_value = rows
    if row is not None:
        cursor.fetchone.return_value = row
    return conexion, cursor


@patch(
    "app.infraestructura.auditoria.repositorio_auditoria_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestRegistrarRegistroAuditoria:

    def test_registrar_ejecuta_insert_parametrizado(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        registro = crear_registro_auditoria_mock()
        repo = RepositorioAuditoriaPostgres()
        repo.registrar(registro)

        query = str(cursor.execute.call_args_list[0].args[0])
        params = cursor.execute.call_args_list[0].args[1]

        assert "insert into registroauditoria" in query.lower()
        assert params["categoria"] == registro.categoria
        assert params["evento"] == registro.evento
        assert params["resultado"] == registro.resultado
        assert params["ip_origen"] == registro.ip_origen
        assert params["rut_usuario"] == registro.rut_usuario
        assert params["metodo"] == registro.metodo

    def test_registrar_no_incluye_id_generado_por_db(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioAuditoriaPostgres()
        repo.registrar(crear_registro_auditoria_mock())

        query = str(cursor.execute.call_args_list[0].args[0]).lower()

        assert "delete" not in query
        assert "update" not in query


@patch(
    "app.infraestructura.auditoria.repositorio_auditoria_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestObtenerRegistrosAuditoriaPaginados:

    def test_obtener_paginados_ejecuta_count_y_select(self, obtener_conexion_mock):
        fila = crear_fila_registro_auditoria_mock(
            categoria="AUTENTICACION",
            evento="LOGIN_EXITOSO",
        )
        conexion, cursor = _conexion_mock(rows=[fila], row={"total": 25})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioAuditoriaPostgres()
        registros, total = repo.obtener_paginados(
            categoria="AUTENTICACION",
            evento="LOGIN_EXITOSO",
            rut_usuario=None,
            ip_origen=None,
            entidad_tipo=None,
            fecha_desde=None,
            fecha_hasta=None,
            texto_busqueda=None,
            pagina=2,
            tamano_pagina=15,
        )

        assert total == 25
        assert len(registros) == 1
        assert registros[0].categoria == "AUTENTICACION"
        assert registros[0].evento == "LOGIN_EXITOSO"
        assert registros[0].id == 1

        queries = [str(call.args[0]).lower() for call in cursor.execute.call_args_list]
        assert "count(*)" in queries[0]
        assert "limit %(tamano_pagina)s offset %(offset)s" in queries[1]

        params_select = cursor.execute.call_args_list[1].args[1]
        assert params_select["offset"] == 15
        assert params_select["tamano_pagina"] == 15

    def test_obtener_paginados_filtra_por_fecha_e_ip(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[], row={"total": 0})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioAuditoriaPostgres()
        fecha_desde = datetime(2026, 9, 1)
        fecha_hasta = datetime(2026, 9, 30)

        repo.obtener_paginados(
            categoria=None,
            evento=None,
            rut_usuario=None,
            ip_origen="200.10",
            entidad_tipo=None,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            texto_busqueda=None,
            pagina=1,
            tamano_pagina=15,
        )

        query = str(cursor.execute.call_args_list[0].args[0]).lower()
        params = cursor.execute.call_args_list[0].args[1]

        assert "ra.fecha_registro >= %(fecha_desde)s" in query
        assert "ra.fecha_registro <= %(fecha_hasta)s" in query
        assert "ra.ip_origen like %(ip_origen)s" in query
        assert params["fecha_desde"] == fecha_desde
        assert params["fecha_hasta"] == fecha_hasta
        assert params["ip_origen"] == "%200.10%"

    def test_obtener_paginados_con_texto_busqueda(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[], row={"total": 0})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioAuditoriaPostgres()
        repo.obtener_paginados(
            categoria=None,
            evento=None,
            rut_usuario=None,
            ip_origen=None,
            entidad_tipo=None,
            fecha_desde=None,
            fecha_hasta=None,
            texto_busqueda="juan",
            pagina=1,
            tamano_pagina=15,
        )

        query = str(cursor.execute.call_args_list[0].args[0]).lower()
        params = cursor.execute.call_args_list[0].args[1]

        assert "unaccent(lower(ra.rut_usuario))" in query
        assert "unaccent(lower(ra.nombre_usuario))" in query
        assert params["texto_busqueda"] == "%juan%"

    def test_obtener_paginados_sin_filtros_no_agrega_where(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[], row={"total": 0})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioAuditoriaPostgres()
        repo.obtener_paginados(
            categoria=None,
            evento=None,
            rut_usuario=None,
            ip_origen=None,
            entidad_tipo=None,
            fecha_desde=None,
            fecha_hasta=None,
            texto_busqueda=None,
            pagina=1,
            tamano_pagina=15,
        )

        query = str(cursor.execute.call_args_list[0].args[0]).lower()

        assert " where " not in query
