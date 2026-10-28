from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.prospecto.use_cases.cambiar_linea_negocio_prospecto import (
    MOTIVO_DESCARTE_CAMBIO_LINEA,
    CambiarLineaNegocioProspectoUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import (
    ConflictoEnAccionException,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import (
    HistorialEstadoProcesoComercial,
)
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import (
    RepositorioHistorialEstadoProcesosComerciales,
)
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from tests.factories.linea_negocio_factory import crear_linea_negocio_mock
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock

MODULO = 'app.aplicacion.prospecto.use_cases.cambiar_linea_negocio_prospecto'


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='12345678-9')


@pytest.fixture
def repositorio_prospectos_mock():
    mock = MagicMock(spec=RepositorioProspectos)
    mock.buscar.return_value = crear_prospecto_mock(
        id=1,
        ejecutivo_comercial_asignado=crear_usuario_mock(rut='12345678-9'),
    )
    return mock


@pytest.fixture
def repositorio_lineas_negocio_mock():
    mock = MagicMock(spec=RepositorioLineasNegocio)
    mock.obtener_por_id.return_value = crear_linea_negocio_mock(id=2, nombre='Líneas Personales')
    return mock


@pytest.fixture
def repositorio_procesos_mock():
    mock = MagicMock(spec=RepositorioProcesosComerciales)
    mock.obtener_procesos_comerciales.return_value = [
        crear_proceso_comercial_mock(id=10, id_prospecto=1),
        crear_proceso_comercial_mock(id=11, id_prospecto=1),
    ]
    return mock


@pytest.fixture
def repositorio_historial_mock():
    return MagicMock(spec=RepositorioHistorialEstadoProcesosComerciales)


@pytest.fixture
def servicio_alertas_mock():
    mock = MagicMock(spec=ServicioAlertasProceso)
    mock.marcar_todas_leidas.return_value = ['11111111-1']
    return mock


@pytest.fixture
def use_case(
    repositorio_prospectos_mock,
    repositorio_lineas_negocio_mock,
    repositorio_procesos_mock,
    repositorio_historial_mock,
    servicio_alertas_mock,
):
    return CambiarLineaNegocioProspectoUseCase(
        repositorio_prospectos=repositorio_prospectos_mock,
        repositorio_lineas_negocio=repositorio_lineas_negocio_mock,
        repositorio_procesos_comerciales=repositorio_procesos_mock,
        repositorio_historial=repositorio_historial_mock,
        servicio_alertas=servicio_alertas_mock,
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestCambiarLineaNegocioProspecto:

    def test_cambia_la_linea_de_negocio(self, mock_hub, use_case,
            repositorio_prospectos_mock, usuario):
        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        prospecto = repositorio_prospectos_mock.buscar.return_value
        repositorio_prospectos_mock.actualizar_prospecto.assert_called_once_with(prospecto)
        assert prospecto.linea_negocio.id == 2

    def test_devuelve_la_cantidad_de_oportunidades_descartadas(self, mock_hub,
            use_case, usuario):
        resultado = use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        assert resultado == 2

    def test_consulta_solo_oportunidades_abiertas_del_prospecto(self, mock_hub,
            use_case, repositorio_procesos_mock, usuario):
        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        repositorio_procesos_mock.obtener_procesos_comerciales.assert_called_once_with(
            id_prospecto=1,
            abiertos=True,
        )

    def test_descarta_todas_las_oportunidades_abiertas(self, mock_hub, use_case,
            repositorio_procesos_mock, usuario):
        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        assert repositorio_procesos_mock.actualizar.call_count == 2
        for proceso in repositorio_procesos_mock.obtener_procesos_comerciales.return_value:
            assert proceso.descartado is True
            assert proceso.cerrado is True
            assert isinstance(proceso.fecha_cierre, datetime)
            assert proceso.fecha_cierre.tzinfo is not None
            assert proceso.motivo_cierre == MOTIVO_DESCARTE_CAMBIO_LINEA

    def test_registra_historial_por_cada_oportunidad_descartada(self, mock_hub,
            use_case, repositorio_historial_mock, usuario):
        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        assert repositorio_historial_mock.registrar.call_count == 2
        for llamada in repositorio_historial_mock.registrar.call_args_list:
            historial = llamada.args[0]
            assert isinstance(historial, HistorialEstadoProcesoComercial)
            assert historial.codigo_estado == 'OPORTUNIDAD_DESCARTADA'
            assert historial.rut_registrado_por == usuario.rut
            assert historial.observacion == MOTIVO_DESCARTE_CAMBIO_LINEA
            assert historial.fecha.tzinfo is not None
        ids_registrados = {
            llamada.args[0].id_proceso_comercial
            for llamada in repositorio_historial_mock.registrar.call_args_list
        }
        assert ids_registrados == {10, 11}

    def test_descarta_antes_de_cambiar_la_linea(self, mock_hub, use_case,
            repositorio_procesos_mock, repositorio_prospectos_mock, usuario):
        orden = []
        repositorio_procesos_mock.actualizar.side_effect = lambda p: orden.append('descarte')
        repositorio_prospectos_mock.actualizar_prospecto.side_effect = lambda p: orden.append('linea')

        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        assert orden == ['descarte', 'descarte', 'linea']

    def test_marca_alertas_leidas_de_cada_oportunidad(self, mock_hub, use_case,
            servicio_alertas_mock, usuario):
        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        assert servicio_alertas_mock.marcar_todas_leidas.call_count == 2
        ids = [
            llamada.args[0]
            for llamada in servicio_alertas_mock.marcar_todas_leidas.call_args_list
        ]
        assert ids == [10, 11]

    def test_publica_destinatarios_unicos_en_el_hub(self, mock_hub, use_case,
            servicio_alertas_mock, usuario):
        servicio_alertas_mock.marcar_todas_leidas.return_value = ['11111111-1', '22222222-2']

        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1', '22222222-2'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_descarte'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub, use_case,
            servicio_alertas_mock, usuario):
        servicio_alertas_mock.marcar_todas_leidas.return_value = []

        use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_sin_oportunidades_abiertas_solo_cambia_la_linea(self, mock_hub,
            use_case, repositorio_procesos_mock, repositorio_prospectos_mock,
            repositorio_historial_mock, usuario):
        repositorio_procesos_mock.obtener_procesos_comerciales.return_value = []

        resultado = use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        assert resultado == 0
        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        prospecto = repositorio_prospectos_mock.buscar.return_value
        repositorio_prospectos_mock.actualizar_prospecto.assert_called_once_with(prospecto)

    def test_prospecto_inexistente_no_cambia_nada(self, mock_hub, use_case,
            repositorio_prospectos_mock, repositorio_procesos_mock,
            repositorio_historial_mock, usuario):
        repositorio_prospectos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id=99, id_linea_negocio=2, usuario=usuario)

        repositorio_procesos_mock.obtener_procesos_comerciales.assert_not_called()
        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        repositorio_prospectos_mock.actualizar_prospecto.assert_not_called()

    def test_solo_el_ejecutivo_comercial_asignado_puede_cambiarla(self, mock_hub,
            use_case, repositorio_prospectos_mock, repositorio_procesos_mock,
            repositorio_historial_mock, usuario):
        repositorio_prospectos_mock.buscar.return_value = crear_prospecto_mock(
            id=1,
            ejecutivo_comercial_asignado=crear_usuario_mock(rut='99999999-9'),
        )

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        repositorio_procesos_mock.obtener_procesos_comerciales.assert_not_called()
        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        repositorio_prospectos_mock.actualizar_prospecto.assert_not_called()

    def test_sin_ejecutivo_asignado_no_puede_cambiarla(self, mock_hub, use_case,
            repositorio_prospectos_mock, repositorio_procesos_mock, usuario):
        repositorio_prospectos_mock.buscar.return_value = crear_prospecto_mock(
            id=1,
            ejecutivo_comercial_asignado=None,
        )

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id=1, id_linea_negocio=2, usuario=usuario)

        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_prospectos_mock.actualizar_prospecto.assert_not_called()

    def test_linea_de_negocio_inexistente_no_descarta(self, mock_hub, use_case,
            repositorio_lineas_negocio_mock, repositorio_procesos_mock,
            repositorio_historial_mock, repositorio_prospectos_mock, usuario):
        repositorio_lineas_negocio_mock.obtener_por_id.return_value = None

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(id=1, id_linea_negocio=999, usuario=usuario)

        repositorio_procesos_mock.obtener_procesos_comerciales.assert_not_called()
        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        repositorio_prospectos_mock.actualizar_prospecto.assert_not_called()

    def test_misma_linea_de_negocio_no_descarta(self, mock_hub, use_case,
            repositorio_procesos_mock, repositorio_historial_mock,
            repositorio_prospectos_mock, usuario):
        # El prospecto de la factory tiene la línea de negocio id=1
        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id=1, id_linea_negocio=1, usuario=usuario)

        repositorio_procesos_mock.obtener_procesos_comerciales.assert_not_called()
        repositorio_procesos_mock.actualizar.assert_not_called()
        repositorio_historial_mock.registrar.assert_not_called()
        repositorio_prospectos_mock.actualizar_prospecto.assert_not_called()
