from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.proceso_comercial.use_cases.registrar_aceptacion_cliente import (
    RegistrarAceptacionClienteUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import (
    RepositorioNotificaciones,
)
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.usuario_factory import crear_usuario_mock

MODULO = 'app.aplicacion.proceso_comercial.use_cases.registrar_aceptacion_cliente'


@pytest.fixture
def repositorio_procesos_mock():
    mock = MagicMock(spec=RepositorioProcesosComerciales)
    mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
    return mock


@pytest.fixture
def repositorio_notificaciones_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.fixture
def servicio_alertas_mock():
    mock = MagicMock(spec=ServicioAlertasProceso)
    mock.marcar_leidas.return_value = ['22222222-2']
    return mock


@pytest.fixture
def use_case(repositorio_procesos_mock, repositorio_notificaciones_mock, servicio_alertas_mock):
    return RegistrarAceptacionClienteUseCase(
        repositorio_procesos_comerciales=repositorio_procesos_mock,
        repositorio_notificaciones=repositorio_notificaciones_mock,
        servicio_alertas=servicio_alertas_mock,
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestRegistrarAceptacionClienteAlertas:

    def test_registra_y_marca_alertas_sla(self, mock_hub, use_case,
            repositorio_procesos_mock, servicio_alertas_mock):
        use_case.ejecutar(id_proceso_comercial=4, usuario=crear_usuario_mock())

        repositorio_procesos_mock.registrar_aceptacion_cliente.assert_called_once()
        servicio_alertas_mock.marcar_leidas.assert_called_once()
        args = servicio_alertas_mock.marcar_leidas.call_args.args
        assert args[0] == 4
        assert args[1] == TIPOS_ALERTA_SLA
        assert isinstance(args[2], datetime)
        assert args[2].tzinfo is not None

    def test_publica_con_motivo_alertas_leidas_cambio_estado(self, mock_hub, use_case):
        use_case.ejecutar(id_proceso_comercial=4, usuario=crear_usuario_mock())

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['22222222-2'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub, use_case, servicio_alertas_mock):
        servicio_alertas_mock.marcar_leidas.return_value = []

        use_case.ejecutar(id_proceso_comercial=4, usuario=crear_usuario_mock())

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_proceso_no_encontrado_no_marca_ni_publica(self, mock_hub, use_case,
            repositorio_procesos_mock, servicio_alertas_mock):
        repositorio_procesos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id_proceso_comercial=99, usuario=crear_usuario_mock())

        servicio_alertas_mock.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()
