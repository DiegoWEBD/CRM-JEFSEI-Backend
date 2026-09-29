from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import (
    RepositorioCompanySegurosPostgres,
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


def _consulta(cursor, indice: int) -> str:
    return str(cursor.execute.call_args_list[indice].args[0])


def _params(cursor, indice: int) -> dict:
    return cursor.execute.call_args_list[indice].args[1]


@patch(
    "app.infraestructura.company_seguros.repositorio_company_seguros_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestObtenerPaginadasCompanySeguros:

    def test_ejecuta_count_y_select_con_limit_offset(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 42})
        cursor.fetchall.side_effect = [
            [{"id": 1, "nombre": "Chilena"}, {"id": 2, "nombre": "Mapfre"}],
            [],
        ]
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        companies, total = repo.obtener_paginadas(pagina=3, tamano_pagina=10)

        assert total == 42
        assert len(companies) == 2

        count_query = _consulta(cursor, 0)
        data_query = _consulta(cursor, 1)

        assert "count(*)" in count_query.lower()
        assert "limit" in data_query.lower()
        assert "offset" in data_query.lower()
        assert _params(cursor, 1)["tamano_pagina"] == 10
        assert _params(cursor, 1)["offset"] == 20

    def test_where_incluye_eliminado_false(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.obtener_paginadas()

        for indice in (0, 1):
            query = _consulta(cursor, indice)
            assert "eliminado" in query
            assert "eliminado = false" in query.lower().replace("eliminado=false", "eliminado = false")

    def test_texto_busqueda_genera_unaccent_lower_like_sobre_nombre(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 1})
        cursor.fetchall.side_effect = [[{"id": 1, "nombre": "Chilena"}], []]
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.obtener_paginadas(texto_busqueda="Chilena")

        query = _consulta(cursor, 0).lower().replace(" ", "")

        assert "unaccent(lower(nombre))likeunaccent(lower(%(texto_busqueda)s))" in query
        assert _params(cursor, 0)["texto_busqueda"] == "%chilena%"

    def test_sin_texto_busqueda_no_agrega_condicion_like(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.obtener_paginadas(texto_busqueda=None)

        query = _consulta(cursor, 0).lower()

        assert "like" not in query
        assert "texto_busqueda" not in _params(cursor, 0)

    def test_offset_es_pagina_menos_1_multiplicado_por_tamano(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 100})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.obtener_paginadas(pagina=5, tamano_pagina=15)

        assert _params(cursor, 1)["offset"] == 60

    def test_trae_factores_de_la_pagina_con_any_de_ids(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 2})
        cursor.fetchall.side_effect = [
            [{"id": 1, "nombre": "Chilena"}, {"id": 2, "nombre": "Mapfre"}],
            [],
        ]
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        companies = repo.obtener_paginadas()[0]

        assert len(cursor.execute.call_args_list) == 3

        factores_query = _consulta(cursor, 2)
        factores_params = _params(cursor, 2)

        assert "factorcuotascompany" in factores_query.lower()
        assert "= any" in factores_query.lower()
        assert factores_params["ids"] == [1, 2]

        assert len(companies[0].factores_cuotas) == 0

    def test_asigna_factores_a_cada_company(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 2})
        cursor.fetchall.side_effect = [
            [{"id": 1, "nombre": "Chilena"}, {"id": 2, "nombre": "Mapfre"}],
            [
                {"id_company": 1, "numero_cuotas": 3, "factor": 1.02},
                {"id_company": 1, "numero_cuotas": 12, "factor": 1.085},
            ],
        ]
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        companies = repo.obtener_paginadas()[0]

        assert len(companies) == 2
        assert companies[0].nombre == "Chilena"
        assert len(companies[0].factores_cuotas) == 2
        assert companies[0].factores_cuotas[0].numero_cuotas == 3
        assert companies[1].factores_cuotas == []

    def test_sin_resultados_no_consulta_factores(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        companies, total = repo.obtener_paginadas(texto_busqueda="no-existe")

        assert companies == []
        assert total == 0
        assert len(cursor.execute.call_args_list) == 2
