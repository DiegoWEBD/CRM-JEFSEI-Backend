import pytest
from unittest.mock import MagicMock

from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from tests.factories.company_seguros_factory import crear_company_seguros_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioCompanySeguros)


@pytest.mark.unit
class TestCrearCompanyUseCase:

    def test_crear_ok(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase

        repositorio_mock.existe_por_nombre.return_value = False
        repositorio_mock.crear.return_value = crear_company_seguros_mock(id=10, nombre="Mapfre")

        uc = CrearCompanyUseCase(repositorio_mock)
        company = uc.ejecutar(nombre="Mapfre")

        assert company.id == 10
        assert company.nombre == "Mapfre"
        repositorio_mock.existe_por_nombre.assert_called_once_with("Mapfre")
        repositorio_mock.crear.assert_called_once_with("Mapfre")

    def test_crear_nombre_duplicado_lanza_recurso_ya_existe(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase

        repositorio_mock.existe_por_nombre.return_value = True

        uc = CrearCompanyUseCase(repositorio_mock)

        with pytest.raises(RecursoYaExisteException, match="Ya existe una compañía con ese nombre"):
            uc.ejecutar(nombre="Mapfre")

        repositorio_mock.crear.assert_not_called()

    def test_crear_nombre_vacio_lanza_bad_request(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase

        uc = CrearCompanyUseCase(repositorio_mock)

        with pytest.raises(BadRequestException, match="El nombre de la compañía es obligatorio"):
            uc.ejecutar(nombre="   ")

        repositorio_mock.crear.assert_not_called()

    def test_crear_normaliza_espacios(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase

        repositorio_mock.existe_por_nombre.return_value = False
        repositorio_mock.crear.return_value = crear_company_seguros_mock(nombre="Mapfre")

        uc = CrearCompanyUseCase(repositorio_mock)
        uc.ejecutar(nombre="  Mapfre  ")

        repositorio_mock.crear.assert_called_once_with("Mapfre")


@pytest.mark.unit
class TestActualizarNombreCompanyUseCase:

    def test_actualizar_ok(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import (
            ActualizarNombreCompanyUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1, nombre="Mapfre")
        repositorio_mock.existe_por_nombre.return_value = False

        uc = ActualizarNombreCompanyUseCase(repositorio_mock)
        uc.ejecutar(id=1, nombre="Mapfre Chile")

        repositorio_mock.existe_por_nombre.assert_called_once_with("Mapfre Chile", id_excluir=1)
        repositorio_mock.actualizar_nombre.assert_called_once_with(1, "Mapfre Chile")

    def test_actualizar_a_nombre_de_otra_company_lanza_recurso_ya_existe(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import (
            ActualizarNombreCompanyUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)
        repositorio_mock.existe_por_nombre.return_value = True

        uc = ActualizarNombreCompanyUseCase(repositorio_mock)

        with pytest.raises(RecursoYaExisteException, match="Ya existe una compañía con ese nombre"):
            uc.ejecutar(id=1, nombre="Zurich")

        repositorio_mock.actualizar_nombre.assert_not_called()

    def test_actualizar_company_ya_eliminada_retorna_404(self, repositorio_mock):
        """D4 (sin restaurar): una compañía eliminada no es editable, buscar() la omite."""
        from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import (
            ActualizarNombreCompanyUseCase,
        )

        repositorio_mock.buscar.return_value = None

        uc = ActualizarNombreCompanyUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Compañía no encontrada"):
            uc.ejecutar(id=1, nombre="Zurich Seguros")

        repositorio_mock.actualizar_nombre.assert_not_called()

    def test_actualizar_company_inexistente_lanza_recurso_no_encontrado(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import (
            ActualizarNombreCompanyUseCase,
        )

        repositorio_mock.buscar.return_value = None

        uc = ActualizarNombreCompanyUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Compañía no encontrada"):
            uc.ejecutar(id=999, nombre="Zurich")

        repositorio_mock.actualizar_nombre.assert_not_called()

    def test_actualizar_nombre_vacio_lanza_bad_request(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import (
            ActualizarNombreCompanyUseCase,
        )

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = ActualizarNombreCompanyUseCase(repositorio_mock)

        with pytest.raises(BadRequestException, match="El nombre de la compañía es obligatorio"):
            uc.ejecutar(id=1, nombre="  ")

        repositorio_mock.actualizar_nombre.assert_not_called()


@pytest.mark.unit
class TestEliminarCompanyUseCase:

    def test_eliminar_ok(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1, eliminado=False)

        uc = EliminarCompanyUseCase(repositorio_mock)
        uc.ejecutar(id=1)

        repositorio_mock.eliminar.assert_called_once_with(1)

    def test_eliminar_company_ya_eliminada_retorna_404(self, repositorio_mock):
        """D4 (sin restaurar): eliminar una compañía ya eliminada es 404, no idempotente."""
        from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase

        repositorio_mock.buscar.return_value = None

        uc = EliminarCompanyUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Compañía no encontrada"):
            uc.ejecutar(id=1)

        repositorio_mock.eliminar.assert_not_called()

    def test_eliminar_company_inexistente_lanza_recurso_no_encontrado(self, repositorio_mock):
        from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase

        repositorio_mock.buscar.return_value = None

        uc = EliminarCompanyUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Compañía no encontrada"):
            uc.ejecutar(id=999)

        repositorio_mock.eliminar.assert_not_called()

    def test_eliminar_company_con_cotizaciones_no_lanza_conflicto(self, repositorio_mock):
        """D3: el delete es siempre soft delete, sin verificar cotizaciones asociadas."""
        from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase

        repositorio_mock.buscar.return_value = crear_company_seguros_mock(id=1)

        uc = EliminarCompanyUseCase(repositorio_mock)
        uc.ejecutar(id=1)

        repositorio_mock.eliminar.assert_called_once_with(1)
