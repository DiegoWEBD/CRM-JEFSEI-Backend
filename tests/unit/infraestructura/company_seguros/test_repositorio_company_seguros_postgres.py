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


@patch(
    "app.infraestructura.company_seguros.repositorio_company_seguros_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestCrearCompanySeguros:

    def test_crear_ejecuta_insert_parametrizado(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"id": 7, "nombre": "Mapfre"})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        company = repo.crear(nombre="Mapfre")

        query = str(cursor.execute.call_args_list[0].args[0])
        params = cursor.execute.call_args_list[0].args[1]

        assert "insert into companyseguros" in query.lower()
        assert params == {"nombre": "Mapfre"}
        assert company.id == 7
        assert company.nombre == "Mapfre"
        assert company.eliminado is False

    def test_crear_sin_commit_no_falla(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"id": 1, "nombre": "Zurich"})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.crear(nombre="Zurich")

        assert conexion.commit.called


@patch(
    "app.infraestructura.company_seguros.repositorio_company_seguros_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestEliminarCompanySeguros:

    def test_eliminar_ejecuta_update_set_eliminado_true(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.eliminar(id=5)

        query = str(cursor.execute.call_args_list[0].args[0])
        params = cursor.execute.call_args_list[0].args[1]

        assert "update companyseguros" in query.lower()
        assert "set eliminado = true" in query.lower()
        assert params == {"id": 5}
        assert conexion.commit.called

    def test_eliminar_no_borra_filas_fisicamente(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.eliminar(id=5)

        query = str(cursor.execute.call_args_list[0].args[0]).lower()

        assert "delete from" not in query
        assert "update" in query


@patch(
    "app.infraestructura.company_seguros.repositorio_company_seguros_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestObtenerTodasCompanySeguros:

    def test_obtener_todas_incluye_filtro_eliminado_false(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[{"id": 1, "nombre": "Mapfre"}])
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        companies = repo.obtener_todas()

        query = str(cursor.execute.call_args_list[0].args[0])

        assert "eliminado = false" in query.lower().replace("eliminado=false", "eliminado = false")
        assert "eliminado" in query
        assert len(companies) == 1

    def test_obtener_todas_sin_resultados_retorna_lista_vacia(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[])
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()

        assert repo.obtener_todas() == []


@patch(
    "app.infraestructura.company_seguros.repositorio_company_seguros_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestExistePorNombreCompanySeguros:

    def test_existe_por_nombre_compara_unaccent_lower(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 1})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        existe = repo.existe_por_nombre(nombre="Chilena Rev. Seguros")

        query = str(cursor.execute.call_args_list[0].args[0])
        params = cursor.execute.call_args_list[0].args[1]

        assert "unaccent(lower(nombre))=unacc" in query.lower().replace(" ", "")
        assert params["nombre"] == "chilena rev. seguros"
        assert existe is True

    def test_existe_por_nombre_es_igualdad_exacta_no_parcial(self, obtener_conexion_mock):
        """'Mapfre' no debe chocar con 'Mapfre Seguros'."""
        conexion, cursor = _conexion_mock(row={"total": 0})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        existe = repo.existe_por_nombre(nombre="Mapfre")

        query = str(cursor.execute.call_args_list[0].args[0])
        params = cursor.execute.call_args_list[0].args[1]

        assert "like" not in query.lower()
        assert "%" not in params["nombre"]
        assert existe is False

    def test_existe_por_nombre_ignora_companies_eliminadas(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 0})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        existe = repo.existe_por_nombre(nombre="Mapfre")

        query = str(cursor.execute.call_args_list[0].args[0])

        assert "eliminado" in query
        assert "eliminado = false" in query.lower().replace("eliminado=false", "eliminado = false")
        assert existe is False

    def test_existe_por_nombre_con_id_excluir(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={"total": 0})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.existe_por_nombre(nombre="Mapfre", id_excluir=9)

        query = str(cursor.execute.call_args_list[0].args[0])
        params = cursor.execute.call_args_list[0].args[1]

        assert "id <> %(id_excluir)s" in query.lower().replace("  ", " ")
        assert params["id_excluir"] == 9


@patch(
    "app.infraestructura.company_seguros.repositorio_company_seguros_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestReemplazarFactoresCuotas:

    def test_elimina_previos_y_reinserta_en_transaccion(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.reemplazar_factores_cuotas(1, [(3, 1.02), (12, 1.085)])

        consultas = [str(c.args[0]) for c in cursor.execute.call_args_list]

        assert len(consultas) == 3
        assert "delete from FactorCuotasCompany" in consultas[0]
        assert "insert into FactorCuotasCompany" in consultas[1]
        assert "insert into FactorCuotasCompany" in consultas[2]
        assert conexion.commit.called

    def test_borra_previamente_por_id_company(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.reemplazar_factores_cuotas(7, [(6, 1.04)])

        delete_params = cursor.execute.call_args_list[0].args[1]
        insert_params = cursor.execute.call_args_list[1].args[1]

        assert delete_params == {"id_company": 7}
        assert insert_params == {"id_company": 7, "numero_cuotas": 6, "factor": 1.04}

    def test_lista_vacia_solo_ejecuta_el_delete(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.reemplazar_factores_cuotas(1, [])

        consultas = [str(c.args[0]) for c in cursor.execute.call_args_list]

        assert len(consultas) == 1
        assert "delete from FactorCuotasCompany" in consultas[0]
        assert conexion.commit.called

    def test_hace_un_unico_commit(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.reemplazar_factores_cuotas(1, [(3, 1.02), (6, 1.04), (12, 1.085)])

        assert conexion.commit.call_count == 1

    def test_factor_con_muchos_decimales_se_envia_sin_truncar(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioCompanySegurosPostgres()
        repo.reemplazar_factores_cuotas(1, [(12, 1.0855555555)])

        insert_params = cursor.execute.call_args_list[1].args[1]

        assert insert_params == {
            "id_company": 1,
            "numero_cuotas": 12,
            "factor": 1.0855555555,
        }
