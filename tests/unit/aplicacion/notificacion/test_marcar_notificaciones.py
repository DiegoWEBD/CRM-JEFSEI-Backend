import pytest
from unittest.mock import MagicMock

from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.mark.unit
class TestMarcarNotificacionLeida:

    def test_marca_la_notificacion_del_usuario(self, repositorio_mock):
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        repositorio_mock.marcar_leida.assert_called_once_with(
            id_notificacion=5, rut_usuario="12345678-9"
        )

    def test_notificacion_inexistente_propaga_404(self, repositorio_mock):
        repositorio_mock.marcar_leida.side_effect = RecursoNoEncontradoException(
            "Notificación no encontrada"
        )
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_notificacion=999, rut_usuario="12345678-9")

    def test_notificacion_de_otro_usuario_propaga_404(self, repositorio_mock):
        # El repositorio valida que la notificación pertenezca al usuario
        repositorio_mock.marcar_leida.side_effect = RecursoNoEncontradoException(
            "Notificación no encontrada"
        )
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_notificacion=1, rut_usuario="99999999-9")


@pytest.mark.unit
class TestMarcarNotificacionesLeidas:

    def test_marca_todas_del_usuario_y_retorna_total(self, repositorio_mock):
        repositorio_mock.marcar_todas_leidas.return_value = 4
        uc = MarcarNotificacionesLeidasUseCase(repositorio_mock)

        total = uc.ejecutar(rut_usuario="12345678-9")

        assert total == 4
        repositorio_mock.marcar_todas_leidas.assert_called_once_with(
            rut_usuario="12345678-9"
        )

    def test_sin_no_leidas_retorna_cero(self, repositorio_mock):
        repositorio_mock.marcar_todas_leidas.return_value = 0
        uc = MarcarNotificacionesLeidasUseCase(repositorio_mock)

        assert uc.ejecutar(rut_usuario="12345678-9") == 0
