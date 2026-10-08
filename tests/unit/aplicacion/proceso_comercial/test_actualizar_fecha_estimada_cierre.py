from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.proceso_comercial.use_cases.actualizar_fecha_estimada_cierre import ActualizarFechaEstimadaCierreUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import crear_notificacion_mock
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.usuario_factory import crear_usuario_mock

MODULO = 'app.aplicacion.proceso_comercial.use_cases.actualizar_fecha_estimada_cierre'

FECHA = datetime(2026, 10, 15, 0, 0, 0, tzinfo=timezone.utc)
FECHA_ANTERIOR = datetime(2026, 9, 1, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioProcesosComerciales)


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def servicio_alertas_mock():
    mock = MagicMock(spec=ServicioAlertasProceso)
    mock.marcar_leidas.return_value = []
    return mock


@pytest.fixture
def generar_alerta_cierre_mock():
    mock = MagicMock()
    mock.ejecutar.return_value = None
    return mock


@pytest.fixture
def use_case(
    repositorio_mock,
    authorization_service_mock,
    servicio_alertas_mock,
    generar_alerta_cierre_mock,
):
    return ActualizarFechaEstimadaCierreUseCase(
        authorization_service=authorization_service_mock,
        repositorio_procesos_comerciales=repositorio_mock,
        servicio_alertas=servicio_alertas_mock,
        generar_alerta_cierre=generar_alerta_cierre_mock,
    )


def _habilitar(repositorio_mock, authorization_service_mock, proceso):
    repositorio_mock.buscar.return_value = proceso
    authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = True


@pytest.mark.unit
class TestActualizarFechaEstimadaCierreValidaciones:

    def test_actualizar_exitoso(self, use_case, repositorio_mock, authorization_service_mock):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_called_once_with(
            id=1, fecha=FECHA
        )

    def test_actualizar_con_fecha_null_limpia_el_campo(self, use_case, repositorio_mock, authorization_service_mock):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)

        use_case.ejecutar(id=1, fecha_estimada_cierre=None, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_called_once_with(
            id=1, fecha=None
        )

    def test_proceso_no_encontrado_lanza_excepcion(self, use_case, repositorio_mock, authorization_service_mock):
        repositorio_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id=99, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.assert_not_called()
        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()

    def test_sin_autorizacion_lanza_excepcion(self, use_case, repositorio_mock, authorization_service_mock):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()

    def test_proceso_cerrado_lanza_conflicto(self, use_case, repositorio_mock, authorization_service_mock):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = True

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()

    def test_autorizacion_se_verifica_antes_del_estado_cerrado(self, use_case, repositorio_mock, authorization_service_mock):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestActualizarFechaEstimadaCierreFlujoAlertas:

    def test_marca_leidas_las_alertas_de_fecha_via_servicio(
        self, mock_hub, use_case, repositorio_mock, authorization_service_mock,
        servicio_alertas_mock, generar_alerta_cierre_mock,
    ):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)
        servicio_alertas_mock.marcar_leidas.return_value = ['11111111-1']

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_called_once()
        args = servicio_alertas_mock.marcar_leidas.call_args.args
        assert args[0] == 1
        assert args[1] == TIPOS_ALERTA_FECHA
        assert isinstance(args[2], datetime)

        mock_hub.publicar_desde_hilo.assert_called_once()
        destinos = mock_hub.publicar_desde_hilo.call_args.args[0]
        assert destinos == ['11111111-1']

    def test_reevalua_y_agrega_la_alerta_creada_a_destinatarios(
        self, mock_hub, use_case, repositorio_mock, authorization_service_mock,
        servicio_alertas_mock, generar_alerta_cierre_mock,
    ):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)
        creada = crear_notificacion_mock(id=None, rut_usuario='22222222-2', codigo_tipo='FECHA_CIERRE_VENCIDA')
        generar_alerta_cierre_mock.ejecutar.return_value = creada

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        kwargs = generar_alerta_cierre_mock.ejecutar.call_args.kwargs
        assert kwargs['id_proceso_comercial'] == 1
        assert isinstance(kwargs['ahora'], datetime)
        mock_hub.publicar_desde_hilo.assert_called_once()
        destinos = mock_hub.publicar_desde_hilo.call_args.args[0]
        assert destinos == ['22222222-2']
        assert mock_hub.publicar_desde_hilo.call_args.args[1] == {
            'evento': 'notificaciones_actualizadas',
            'motivo': 'alertas_fecha_cierre_actualizadas',
        }

    def test_acumula_marcadas_y_creada(
        self, mock_hub, use_case, repositorio_mock, authorization_service_mock,
        servicio_alertas_mock, generar_alerta_cierre_mock,
    ):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)
        servicio_alertas_mock.marcar_leidas.return_value = ['11111111-1']
        generar_alerta_cierre_mock.ejecutar.return_value = crear_notificacion_mock(
            id=None, rut_usuario='11111111-1', codigo_tipo='FECHA_CIERRE_VENCIDA'
        )

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        destinos = mock_hub.publicar_desde_hilo.call_args.args[0]
        assert destinos == ['11111111-1', '11111111-1']

    def test_no_reevalua_ni_marca_si_la_fecha_no_cambia(
        self, mock_hub, use_case, repositorio_mock, authorization_service_mock,
        servicio_alertas_mock, generar_alerta_cierre_mock,
    ):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_called_once()
        servicio_alertas_mock.marcar_leidas.assert_not_called()
        generar_alerta_cierre_mock.ejecutar.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_sin_destinatarios_no_publica(
        self, mock_hub, use_case, repositorio_mock, authorization_service_mock,
        servicio_alertas_mock, generar_alerta_cierre_mock,
    ):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        generar_alerta_cierre_mock.ejecutar.assert_called_once()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_ruts_nulos_no_se_publican(
        self, mock_hub, use_case, repositorio_mock, authorization_service_mock,
        servicio_alertas_mock, generar_alerta_cierre_mock,
    ):
        proceso = crear_proceso_comercial_mock(cerrado=False, fecha_estimada_cierre=FECHA_ANTERIOR)
        _habilitar(repositorio_mock, authorization_service_mock, proceso)
        servicio_alertas_mock.marcar_leidas.return_value = []

        use_case.ejecutar(id=1, fecha_estimada_cierre=FECHA, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_called_once()
        mock_hub.publicar_desde_hilo.assert_not_called()
