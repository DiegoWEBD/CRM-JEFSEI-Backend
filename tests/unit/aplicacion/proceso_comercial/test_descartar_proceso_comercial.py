from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.notificacion.use_cases.reevaluar_alertas_renovacion_descarte import (
    ReevaluarAlertasRenovacionDescarteUseCase,
)
from app.aplicacion.proceso_comercial.use_cases.descartar_proceso_comercial import (
    DescartarProcesoComercialUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import (
    ConflictoEnAccionException,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import (
    HistorialEstadoProcesoComercial,
)
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import (
    RepositorioHistorialEstadoProcesosComerciales,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock

MODULO = 'app.aplicacion.proceso_comercial.use_cases.descartar_proceso_comercial'


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='12345678-9')


@pytest.fixture
def repositorio_procesos_mock():
    mock = MagicMock(spec=RepositorioProcesosComerciales)
    mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
    return mock


@pytest.fixture
def repositorio_prospectos_mock():
    mock = MagicMock(spec=RepositorioProspectos)
    mock.buscar.return_value = crear_prospecto_mock(
        ejecutivo_comercial_asignado=crear_usuario_mock(rut='12345678-9')
    )
    return mock


@pytest.fixture
def authorization_service_mock():
    mock = MagicMock(spec=AuthorizationService)
    mock.usuario_puede_descartar_proceso_comercial.return_value = True
    return mock


@pytest.fixture
def repositorio_historial_mock():
    return MagicMock(spec=RepositorioHistorialEstadoProcesosComerciales)


@pytest.fixture
def reevaluar_alertas_mock():
    mock = MagicMock(spec=ReevaluarAlertasRenovacionDescarteUseCase)
    mock.ejecutar.return_value = []
    return mock


@pytest.fixture
def servicio_alertas_mock():
    mock = MagicMock(spec=ServicioAlertasProceso)
    mock.marcar_todas_leidas.return_value = ['11111111-1']
    return mock


@pytest.fixture
def use_case(
    authorization_service_mock,
    repositorio_procesos_mock,
    repositorio_prospectos_mock,
    repositorio_historial_mock,
    servicio_alertas_mock,
    reevaluar_alertas_mock,
):
    return DescartarProcesoComercialUseCase(
        authorization_service=authorization_service_mock,
        repositorio_procesos_comerciales=repositorio_procesos_mock,
        repositorio_prospectos=repositorio_prospectos_mock,
        repositorio_historial=repositorio_historial_mock,
        servicio_alertas=servicio_alertas_mock,
        reevaluar_alertas=reevaluar_alertas_mock,
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestDescartarProcesoComercial:

    def test_descarta_y_cierra_la_oportunidad(self, mock_hub, use_case,
            repositorio_procesos_mock, usuario):
        use_case.ejecutar(id=1, observacion='Cliente no interesado', usuario=usuario)

        proceso = repositorio_procesos_mock.buscar.return_value
        repositorio_procesos_mock.actualizar.assert_called_once_with(proceso)
        assert proceso.descartado is True
        assert proceso.cerrado is True
        assert isinstance(proceso.fecha_cierre, datetime)
        assert proceso.fecha_cierre.tzinfo is not None
        assert proceso.motivo_cierre == 'Cliente no interesado'

    def test_registra_historial_en_estado_oportunidad_descartada(self, mock_hub,
            use_case, repositorio_historial_mock, usuario):
        use_case.ejecutar(id=1, observacion='Cliente no interesado', usuario=usuario)

        repositorio_historial_mock.registrar.assert_called_once()
        historial = repositorio_historial_mock.registrar.call_args.args[0]
        assert isinstance(historial, HistorialEstadoProcesoComercial)
        assert historial.id_proceso_comercial == 1
        assert historial.codigo_estado == 'OPORTUNIDAD_DESCARTADA'
        assert historial.rut_registrado_por == usuario.rut
        assert historial.observacion == 'Cliente no interesado'
        assert historial.fecha.tzinfo is not None

    def test_usa_la_misma_fecha_para_cierre_e_historial(self, mock_hub, use_case,
            repositorio_procesos_mock, repositorio_historial_mock, usuario):
        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        proceso = repositorio_procesos_mock.buscar.return_value
        historial = repositorio_historial_mock.registrar.call_args.args[0]
        assert historial.fecha == proceso.fecha_cierre

    def test_marca_todas_las_alertas_no_leidas(self, mock_hub, use_case,
            servicio_alertas_mock, usuario):
        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        servicio_alertas_mock.marcar_todas_leidas.assert_called_once()
        args = servicio_alertas_mock.marcar_todas_leidas.call_args.args
        assert args[0] == 1
        assert isinstance(args[1], datetime)
        assert args[1].tzinfo is not None

    def test_publica_con_motivo_alertas_leidas_descarte(self, mock_hub, use_case, usuario):
        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_descarte'},
        )

    def test_reevalua_alertas_de_renovacion_de_la_poliza_base(self, mock_hub,
            use_case, reevaluar_alertas_mock, usuario):
        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        reevaluar_alertas_mock.ejecutar.assert_called_once()
        args = reevaluar_alertas_mock.ejecutar.call_args.args
        assert args[0] == 1
        assert isinstance(args[1], datetime)
        assert args[1].tzinfo is not None

    def test_reevalua_tras_persistir_el_descarte(self, mock_hub, use_case,
            repositorio_procesos_mock, reevaluar_alertas_mock, usuario):
        orden = []
        repositorio_procesos_mock.actualizar.side_effect = lambda p: orden.append('descarte')

        def _reevaluar(id, ahora):
            orden.append('reevaluar')
            return []

        reevaluar_alertas_mock.ejecutar.side_effect = _reevaluar

        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        assert orden == ['descarte', 'reevaluar']

    def test_publica_alertas_renovacion_si_hay_destinatarios(self, mock_hub,
            use_case, reevaluar_alertas_mock, usuario):
        reevaluar_alertas_mock.ejecutar.return_value = ['22222222-2']

        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        assert mock_hub.publicar_desde_hilo.call_count == 2
        mock_hub.publicar_desde_hilo.assert_called_with(
            ['22222222-2'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_renovacion_actualizadas'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub, use_case,
            servicio_alertas_mock, usuario):
        servicio_alertas_mock.marcar_todas_leidas.return_value = []

        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_proceso_no_encontrado_no_descarta(self, mock_hub, use_case,
            repositorio_procesos_mock, repositorio_historial_mock,
            servicio_alertas_mock, reevaluar_alertas_mock, usuario):
        repositorio_procesos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id=99, observacion=None, usuario=usuario)

        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        servicio_alertas_mock.marcar_todas_leidas.assert_not_called()
        reevaluar_alertas_mock.ejecutar.assert_not_called()

    def test_proceso_cerrado_no_descarta(self, mock_hub, use_case,
            repositorio_procesos_mock, repositorio_historial_mock, usuario):
        repositorio_procesos_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()

    def test_prospecto_no_encontrado_no_descarta(self, mock_hub, use_case,
            repositorio_prospectos_mock, authorization_service_mock,
            repositorio_historial_mock, usuario):
        repositorio_prospectos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        authorization_service_mock.usuario_puede_descartar_proceso_comercial.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()

    def test_valida_autorizacion_con_prospecto_y_usuario(self, mock_hub, use_case,
            repositorio_prospectos_mock, authorization_service_mock, usuario):
        use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        authorization_service_mock.usuario_puede_descartar_proceso_comercial.assert_called_once_with(
            repositorio_prospectos_mock.buscar.return_value,
            usuario,
        )

    def test_no_autorizado_no_descarta(self, mock_hub, use_case,
            authorization_service_mock, repositorio_procesos_mock,
            repositorio_historial_mock, servicio_alertas_mock,
            reevaluar_alertas_mock, usuario):
        authorization_service_mock.usuario_puede_descartar_proceso_comercial.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id=1, observacion=None, usuario=usuario)

        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        servicio_alertas_mock.marcar_todas_leidas.assert_not_called()
        reevaluar_alertas_mock.ejecutar.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()
