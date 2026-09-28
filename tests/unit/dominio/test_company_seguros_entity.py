import pytest

from tests.factories.company_seguros_factory import (
    crear_company_seguros_mock,
    crear_factor_cuotas_mock,
)


@pytest.mark.unit
class TestCompanySegurosSoftDelete:

    def test_company_seguros_se_crea_no_eliminada_por_defecto(self):
        from app.dominio.company_seguros.company_seguros import CompanySeguros

        company = CompanySeguros(id=1, nombre="Chilena Rev. Seguros")

        assert company.eliminado is False

    def test_marcar_eliminada_cambia_flag(self):
        company = crear_company_seguros_mock()

        assert company.esta_eliminada() is False

        company.marcar_eliminada()

        assert company.esta_eliminada() is True
        assert company.eliminado is True

    def test_marcar_eliminada_es_idempotente(self):
        company = crear_company_seguros_mock()

        company.marcar_eliminada()
        company.marcar_eliminada()

        assert company.esta_eliminada() is True


@pytest.mark.unit
class TestCompanySegurosConstructor:

    def test_constructor_acepta_factores_de_cuotas(self):
        factores = [
            crear_factor_cuotas_mock(numero_cuotas=3, factor=1.02),
            crear_factor_cuotas_mock(numero_cuotas=12, factor=1.085),
        ]

        company = crear_company_seguros_mock(factores_cuotas=factores)

        assert company.factores_cuotas == factores
        assert company.nombre == "Chilena Rev. Seguros"
