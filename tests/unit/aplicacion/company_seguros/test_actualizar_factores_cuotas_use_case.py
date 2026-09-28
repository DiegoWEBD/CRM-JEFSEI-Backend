import pytest
from unittest.mock import MagicMock, call

from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from tests.factories.company_seguros_factory import crear_company_seguros_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioCompanySeguros)


@pytest.mark.unit
class TestActualizarFactoresCuotasUseCase:

    def test_reemplazar_factores_ok(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)
        uc.ejecutar(
            id_company=1,
            factores=[{"numero_cuotas": 3, "factor": 1.02}, {"numero_cuotas": 12, "factor": 1.085}],
        )

        repositorio_mock.reemplazar_factores_cuotas.assert_called_once()
        argumentos = repositorio_mock.reemplazar_factores_cuotas.call_args.args
        assert argumentos[0] == 1
        assert argumentos[1] == [(3, 1.02), (12, 1.085)]

    def test_factores_duplicados_lanza_bad_request(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)

        with pytest.raises(BadRequestException, match="Número de cuotas duplicado"):
            uc.ejecutar(
                id_company=1,
                factores=[{"numero_cuotas": 3, "factor": 1.02}, {"numero_cuotas": 3, "factor": 1.05}],
            )

        repositorio_mock.reemplazar_factores_cuotas.assert_not_called()

    def test_factor_negativo_o_cero_lanza_bad_request(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)

        with pytest.raises(BadRequestException, match="El factor debe ser mayor a 0"):
            uc.ejecutar(id_company=1, factores=[{"numero_cuotas": 3, "factor": 0}])

    def test_numero_cuotas_invalido_lanza_bad_request(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)

        with pytest.raises(BadRequestException, match="El número de cuotas debe ser un entero mayor a 0"):
            uc.ejecutar(id_company=1, factores=[{"numero_cuotas": 0, "factor": 1.02}])

    def test_lista_vacia_elimina_todos_los_factores(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)
        uc.ejecutar(id_company=1, factores=[])

        repositorio_mock.reemplazar_factores_cuotas.assert_called_once_with(1, [])

    def test_company_inexistente_lanza_recurso_no_encontrado(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = None

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Compañía no encontrada"):
            uc.ejecutar(id_company=999, factores=[])

        repositorio_mock.reemplazar_factores_cuotas.assert_not_called()

    def test_factor_sin_limite_de_decimales(self, repositorio_mock):
        """El factor no tiene restricción de decimales: llega completo al repo."""
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)
        uc.ejecutar(
            id_company=1,
            factores=[{"numero_cuotas": 12, "factor": 1.0855555555}],
        )

        repositorio_mock.reemplazar_factores_cuotas.assert_called_once_with(
            1, [(12, 1.0855555555)]
        )

    def test_factor_con_un_decimal_sigue_siendo_invalido_si_es_cero(
        self, repositorio_mock
    ):
        """La única regla sobre el factor es que sea mayor a 0."""
        from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import (
            ActualizarFactoresCuotasUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarFactoresCuotasUseCase(repositorio_mock)

        with pytest.raises(BadRequestException, match="El factor debe ser mayor a 0"):
            uc.ejecutar(id_company=1, factores=[{"numero_cuotas": 12, "factor": 0.0}])
