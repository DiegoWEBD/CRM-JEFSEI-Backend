from unittest.mock import MagicMock

import pytest

from app.aplicacion.prospecto.use_cases.actualizar_porcentaje_depreciacion_personalizado import (
    ActualizarPorcentajeDepreciacionPersonalizadoUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='12345678-9')


@pytest.fixture
def repositorio_prospectos_mock():
    return MagicMock(spec=RepositorioProspectos)


@pytest.fixture
def authorization_service_mock():
    mock = MagicMock()
    mock.usuario_puede_establecer_depreciacion_personalizada.return_value = True
    return mock


@pytest.fixture
def use_case(repositorio_prospectos_mock, authorization_service_mock):
    return ActualizarPorcentajeDepreciacionPersonalizadoUseCase(
        repositorio_prospectos=repositorio_prospectos_mock,
        authorization_service=authorization_service_mock,
    )


@pytest.mark.unit
class TestActualizarPorcentajeDepreciacionPersonalizadoUseCase:

    def test_prospecto_no_encontrado_lanza_excepcion(
        self, use_case, repositorio_prospectos_mock, usuario
    ):
        repositorio_prospectos_mock.buscar_prospecto_condominio.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id=99, porcentaje_depreciacion_personalizado=0.2, usuario=usuario)

        repositorio_prospectos_mock.actualizar_prospecto_condominio.assert_not_called()

    def test_no_autorizado_no_actualiza(
        self, use_case, repositorio_prospectos_mock, authorization_service_mock, usuario
    ):
        repositorio_prospectos_mock.buscar_prospecto_condominio.return_value = crear_prospecto_mock()
        authorization_service_mock.usuario_puede_establecer_depreciacion_personalizada.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id=1, porcentaje_depreciacion_personalizado=0.2, usuario=usuario)

        repositorio_prospectos_mock.actualizar_prospecto_condominio.assert_not_called()

    def test_autorizado_guarda_el_porcentaje(
        self, use_case, repositorio_prospectos_mock, usuario
    ):
        prospecto = crear_prospecto_mock()
        repositorio_prospectos_mock.buscar_prospecto_condominio.return_value = prospecto

        use_case.ejecutar(id=1, porcentaje_depreciacion_personalizado=0.25, usuario=usuario)

        assert prospecto.porcentaje_depreciacion_personalizado == 0.25
        repositorio_prospectos_mock.actualizar_prospecto_condominio.assert_called_once_with(prospecto)

    def test_enviar_none_quita_la_personalizacion(
        self, use_case, repositorio_prospectos_mock, usuario
    ):
        prospecto = crear_prospecto_mock()
        prospecto.porcentaje_depreciacion_personalizado = 0.25
        repositorio_prospectos_mock.buscar_prospecto_condominio.return_value = prospecto

        use_case.ejecutar(id=1, porcentaje_depreciacion_personalizado=None, usuario=usuario)

        assert prospecto.porcentaje_depreciacion_personalizado is None
        repositorio_prospectos_mock.actualizar_prospecto_condominio.assert_called_once_with(prospecto)

    def test_verifica_autorizacion_con_el_prospecto_y_el_usuario(
        self, use_case, repositorio_prospectos_mock, authorization_service_mock, usuario
    ):
        prospecto = crear_prospecto_mock()
        repositorio_prospectos_mock.buscar_prospecto_condominio.return_value = prospecto

        use_case.ejecutar(id=1, porcentaje_depreciacion_personalizado=0.2, usuario=usuario)

        authorization_service_mock.usuario_puede_establecer_depreciacion_personalizada.assert_called_once_with(
            prospecto, usuario
        )
