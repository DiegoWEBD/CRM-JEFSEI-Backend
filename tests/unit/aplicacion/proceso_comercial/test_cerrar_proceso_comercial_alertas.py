from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.proceso_comercial.use_cases.cerrar_proceso_comercial import (
    CerrarProcesoComercialUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import (
    ConflictoEnAccionException,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.notificacion.repositorio_notificaciones import (
    RepositorioNotificaciones,
)
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA, TIPOS_ALERTA_SLA
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.usuario_factory import crear_usuario_mock

MODULO = 'app.aplicacion.proceso_comercial.use_cases.cerrar_proceso_comercial'


@pytest.fixture
def repositorio_procesos_mock():
    mock = MagicMock(spec=RepositorioProcesosComerciales)
    mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
    return mock


@pytest.fixture
def repositorio_polizas_mock():
    mock = MagicMock(spec=RepositorioPolizas)
    mock.buscar_por_proceso_comercial.return_value = MagicMock(numero_poliza='POL-001')
    return mock


@pytest.fixture
def repositorio_planes_pago_mock():
    mock = MagicMock(spec=RepositorioPlanesPago)
    mock.buscar_plan_pago_poliza.return_value = MagicMock()
    return mock


@pytest.fixture
def repositorio_notificaciones_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.fixture
def servicio_alertas_mock():
    mock = MagicMock(spec=ServicioAlertasProceso)
    mock.marcar_leidas.return_value = ['11111111-1']
    return mock


@pytest.fixture
def use_case(
    repositorio_procesos_mock,
    repositorio_polizas_mock,
    repositorio_planes_pago_mock,
    repositorio_notificaciones_mock,
    servicio_alertas_mock,
):
    return CerrarProcesoComercialUseCase(
        repositorio_procesos_comerciales=repositorio_procesos_mock,
        repositorio_planes_pago=repositorio_planes_pago_mock,
        repositorio_polizas=repositorio_polizas_mock,
        repositorio_notificaciones=repositorio_notificaciones_mock,
        servicio_alertas=servicio_alertas_mock,
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestCerrarProcesoComercialAlertas:

    def test_cierra_y_marca_alertas_sla_y_fecha(self, mock_hub, use_case,
            repositorio_procesos_mock, servicio_alertas_mock):
        use_case.ejecutar(id=1, ganado=False, observacion=None, usuario=crear_usuario_mock())

        repositorio_procesos_mock.cerrar.assert_called_once()
        servicio_alertas_mock.marcar_leidas.assert_called_once()
        args = servicio_alertas_mock.marcar_leidas.call_args.args
        assert args[0] == 1
        assert args[1] == TIPOS_ALERTA_SLA + TIPOS_ALERTA_FECHA
        assert isinstance(args[2], datetime)
        assert args[2].tzinfo is not None

    def test_publica_con_motivo_alertas_leidas_cambio_estado(self, mock_hub, use_case):
        use_case.ejecutar(id=1, ganado=False, observacion=None, usuario=crear_usuario_mock())

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub, use_case, servicio_alertas_mock):
        servicio_alertas_mock.marcar_leidas.return_value = []

        use_case.ejecutar(id=1, ganado=False, observacion=None, usuario=crear_usuario_mock())

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_proceso_no_encontrado_no_marca_ni_publica(self, mock_hub, use_case,
            repositorio_procesos_mock, servicio_alertas_mock):
        repositorio_procesos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id=99, ganado=False, observacion=None, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_proceso_ya_cerrado_no_marca_ni_publica(self, mock_hub, use_case,
            repositorio_procesos_mock, servicio_alertas_mock):
        repositorio_procesos_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)

        with pytest.raises(RecursoYaExisteException):
            use_case.ejecutar(id=1, ganado=False, observacion=None, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_ganado_sin_poliza_no_marca_ni_publica(self, mock_hub, use_case,
            repositorio_polizas_mock, servicio_alertas_mock):
        repositorio_polizas_mock.buscar_por_proceso_comercial.return_value = None

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id=1, ganado=True, observacion=None, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_ganado_sin_plan_pago_no_marca_ni_publica(self, mock_hub, use_case,
            repositorio_planes_pago_mock, servicio_alertas_mock):
        repositorio_planes_pago_mock.buscar_plan_pago_poliza.return_value = None

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id=1, ganado=True, observacion=None, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()
