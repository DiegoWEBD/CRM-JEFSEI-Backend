import pytest
from unittest.mock import MagicMock

from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from tests.factories.company_seguros_factory import crear_company_seguros_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioCompanySeguros)


@pytest.mark.unit
class TestObtenerCompaniesSegurosPaginadasUseCase:

    def test_delega_parametros_al_repositorio_y_retorna_tuple(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.obtener_companies_paginadas import (
            ObtenerCompaniesSegurosPaginadasUseCase,
        )

        companies = [crear_company_seguros_mock(id=1), crear_company_seguros_mock(id=2)]
        repositorio_mock.obtener_paginadas.return_value = (companies, 42)

        uc = ObtenerCompaniesSegurosPaginadasUseCase(repositorio_mock)
        resultado, total = uc.ejecutar(
            texto_busqueda="chilena",
            pagina=3,
            tamano_pagina=10,
        )

        assert len(resultado) == 2
        assert total == 42
        repositorio_mock.obtener_paginadas.assert_called_once_with(
            texto_busqueda="chilena",
            pagina=3,
            tamano_pagina=10,
        )

    def test_defaults_pagina_1_y_tamano_15(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.obtener_companies_paginadas import (
            ObtenerCompaniesSegurosPaginadasUseCase,
        )

        repositorio_mock.obtener_paginadas.return_value = ([], 0)

        uc = ObtenerCompaniesSegurosPaginadasUseCase(repositorio_mock)
        uc.ejecutar()

        repositorio_mock.obtener_paginadas.assert_called_once_with(
            texto_busqueda=None,
            pagina=1,
            tamano_pagina=15,
        )

    def test_retorna_vacia_y_total_0_sin_resultados(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.obtener_companies_paginadas import (
            ObtenerCompaniesSegurosPaginadasUseCase,
        )

        repositorio_mock.obtener_paginadas.return_value = ([], 0)

        uc = ObtenerCompaniesSegurosPaginadasUseCase(repositorio_mock)
        resultado, total = uc.ejecutar(texto_busqueda="no-existe")

        assert resultado == []
        assert total == 0
