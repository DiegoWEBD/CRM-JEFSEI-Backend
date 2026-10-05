import pytest
from unittest.mock import MagicMock, patch

from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import crear_notificacion_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.mark.unit
class TestMarcarNotificacionLeida:

    def test_busca_la_notificacion_antes_de_marcar(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, leible=True, leida=False)
        repositorio_mock.buscar.return_value = notif

        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)
        uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        repositorio_mock.buscar.assert_called_once_with(id_notificacion=5)
        repositorio_mock.marcar_leida.assert_called_once_with(
            id_notificacion=5, rut_usuario="12345678-9"
        )

    def test_notificacion_inexistente_lanza_404(self, repositorio_mock):
        repositorio_mock.buscar.return_value = None
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_notificacion=999, rut_usuario="12345678-9")

        repositorio_mock.marcar_leida.assert_not_called()

    def test_notificacion_no_leible_lanza_409(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, nivel="AVISO", leible=False, leida=False)
        repositorio_mock.buscar.return_value = notif
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        repositorio_mock.marcar_leida.assert_not_called()

    def test_notificacion_ya_leida_no_marca_nuevamente(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, leible=True, leida=True)
        repositorio_mock.buscar.return_value = notif
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        repositorio_mock.marcar_leida.assert_not_called()

    def test_marca_notificacion_leible_y_no_leida(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, nivel="INFO", leible=True, leida=False)
        repositorio_mock.buscar.return_value = notif
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        repositorio_mock.marcar_leida.assert_called_once_with(
            id_notificacion=5, rut_usuario="12345678-9"
        )

    def test_publica_en_hub_despues_de_marcar(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, leible=True, leida=False)
        repositorio_mock.buscar.return_value = notif
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        publicar.assert_called_once_with(["12345678-9"], {
            'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
            'motivo': 'marcadas_leidas',
        })

    def test_no_publica_si_no_existe(self, repositorio_mock):
        repositorio_mock.buscar.return_value = None
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            with pytest.raises(RecursoNoEncontradoException):
                uc.ejecutar(id_notificacion=999, rut_usuario="12345678-9")

        publicar.assert_not_called()

    def test_no_publica_si_no_leible(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, nivel="CRITICO", leible=False, leida=False)
        repositorio_mock.buscar.return_value = notif
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            with pytest.raises(ConflictoEnAccionException):
                uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        publicar.assert_not_called()

    def test_no_publica_si_ya_leida(self, repositorio_mock):
        notif = crear_notificacion_mock(id=5, leible=True, leida=True)
        repositorio_mock.buscar.return_value = notif
        uc = MarcarNotificacionLeidaUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(id_notificacion=5, rut_usuario="12345678-9")

        publicar.assert_not_called()


@pytest.mark.unit
class TestMarcarNotificacionesLeidas:

    def test_marca_todas_leibles_del_usuario_y_retorna_total(self, repositorio_mock):
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


@pytest.mark.unit
class TestPublicacionWebSocket:
    """Quien cambia el estado de las notificaciones es quien avisa por el hub."""

    EVENTO = {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'marcadas_leidas'}

    def test_marcar_todas_publica_a_su_destinatario(self, repositorio_mock):
        repositorio_mock.marcar_todas_leidas.return_value = 4
        uc = MarcarNotificacionesLeidasUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(rut_usuario="12345678-9")

        publicar.assert_called_once_with(["12345678-9"], self.EVENTO)

    def test_marcar_todas_no_publica_si_no_hay_no_leidas(self, repositorio_mock):
        repositorio_mock.marcar_todas_leidas.return_value = 0
        uc = MarcarNotificacionesLeidasUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            total = uc.ejecutar(rut_usuario="12345678-9")

        assert total == 0
        publicar.assert_not_called()
