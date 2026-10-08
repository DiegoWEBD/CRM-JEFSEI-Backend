from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial import (
    AsignarEjecutivoComercialUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import crear_notificacion_mock

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial'


def _prospecto_mock(id=1, ejecutivo_previo=None):
    p = MagicMock()
    p.id = id
    p.nombre_riesgo = 'Prospecto Test'
    p.ejecutivo_comercial_asignado = ejecutivo_previo
    return p


def _proceso_mock(id=42):
    p = MagicMock()
    p.id = id
    return p


def _use_case(prospecto, generar_alerta_cierre, rut_nuevo=None, procesos=None):
    repo_prospectos = MagicMock()
    repo_prospectos.buscar.return_value = prospecto
    repo_usuarios = MagicMock()
    if rut_nuevo is not None:
        repo_usuarios.buscar.return_value = MagicMock(rut=rut_nuevo)
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.obtener_procesos_comerciales.return_value = list(procesos or [])
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    repo_notificaciones.buscar_notificaciones_proceso_comercial.return_value = []
    generar_alerta_cierre.ejecutar.return_value = None
    uc = AsignarEjecutivoComercialUseCase(
        repo_prospectos,
        repo_usuarios,
        repo_procesos,
        repo_notificaciones,
        generar_alerta_cierre,
    )
    return uc, repo_prospectos, repo_procesos, repo_notificaciones


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoComercialAlertas:

    def test_acepta_las_dependencias_por_constructor(self, _mock_hub):
        generar = MagicMock()
        uc, _, _, _ = _use_case(_prospecto_mock(), generar, rut_nuevo='22222222-2')

        assert uc.generar_alerta_cierre is generar

    def test_reevalua_por_proceso_abierto_del_prospecto(self, _mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, repo_prospectos, repo_procesos, _ = _use_case(
            prospecto, generar, rut_nuevo='22222222-2',
            procesos=[_proceso_mock(id=42), _proceso_mock(id=43)],
        )

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        repo_prospectos.asignar_ejecutivo_comercial.assert_called_once()
        repo_procesos.obtener_procesos_comerciales.assert_called_once_with(
            id_prospecto=1,
            abiertos=True,
        )
        assert generar.ejecutar.call_count == 2
        ids = [c.kwargs['id_proceso_comercial'] for c in generar.ejecutar.call_args_list]
        assert ids == [42, 43]
        for c in generar.ejecutar.call_args_list:
            assert isinstance(c.kwargs['ahora'], datetime)

    def test_marca_leidas_las_alertas_de_fecha_de_cada_proceso(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones = _use_case(
            prospecto, generar, rut_nuevo='22222222-2',
            procesos=[_proceso_mock(id=42)],
        )
        alerta_fecha = crear_notificacion_mock(
            id=1, rut_usuario='11111111-1', codigo_tipo='FECHA_CIERRE_VENCIDA', leida=False
        )
        alerta_sla = crear_notificacion_mock(
            id=2, rut_usuario='11111111-1', codigo_tipo='SLA_VENCIDO', leida=False
        )
        repo_notificaciones.buscar_notificaciones_proceso_comercial.return_value = [
            alerta_fecha, alerta_sla,
        ]

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        repo_notificaciones.buscar_notificaciones_proceso_comercial.assert_called_once_with(42)
        repo_notificaciones.actualizar.assert_called_once()
        notificacion_actualizada = repo_notificaciones.actualizar.call_args.args[0]
        assert notificacion_actualizada.id == 1
        assert notificacion_actualizada.leida is True
        assert isinstance(notificacion_actualizada.fecha_leida, datetime)
        assert alerta_sla.leida is False

        destinos = mock_hub.publicar_desde_hilo.call_args_list[0].args[0]
        assert destinos == ['11111111-1']

    def test_agrega_la_alerta_creada_a_destinatarios(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, _ = _use_case(
            prospecto, generar, rut_nuevo='22222222-2', procesos=[_proceso_mock(id=42)]
        )
        creada = crear_notificacion_mock(id=None, rut_usuario='22222222-2', codigo_tipo='FECHA_CIERRE_VENCIDA')
        generar.ejecutar.return_value = creada

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        llamadas = mock_hub.publicar_desde_hilo.call_args_list
        llamada_alertas = [
            c for c in llamadas
            if c.args[1]['motivo'] == 'alertas_fecha_cierre_actualizadas'
        ]
        assert len(llamada_alertas) == 1
        assert llamada_alertas[0].args[0] == ['22222222-2']

    def test_reasignacion_de_vuelta_al_mismo_ejecutivo_recrea_alerta(self, mock_hub):
        """Sin guarda de existencia en esta ruta: la alerta previa (leída) del
        usuario no impide crear una nueva al volver a asignarle el prospecto."""
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, _ = _use_case(
            prospecto, generar, rut_nuevo='11111111-1', procesos=[_proceso_mock(id=42)]
        )
        creada = crear_notificacion_mock(id=None, rut_usuario='11111111-1', codigo_tipo='FECHA_CIERRE_VENCIDA')
        generar.ejecutar.return_value = creada

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        generar.ejecutar.assert_called_once()

    def test_no_hace_nada_si_el_rut_no_cambia(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, repo_procesos, repo_notificaciones = _use_case(
            prospecto, generar, rut_nuevo='11111111-1', procesos=[_proceso_mock(id=42)]
        )

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='11111111-1', asignado_por=MagicMock())

        repo_procesos.obtener_procesos_comerciales.assert_not_called()
        repo_notificaciones.buscar_notificaciones_proceso_comercial.assert_not_called()
        generar.ejecutar.assert_not_called()

    def test_desasignacion_tambien_marca_y_reevalua(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, repo_procesos, repo_notificaciones = _use_case(
            prospecto, generar, rut_nuevo=None, procesos=[_proceso_mock(id=42)]
        )
        repo_notificaciones.buscar_notificaciones_proceso_comercial.return_value = [
            crear_notificacion_mock(id=1, rut_usuario='11111111-1', codigo_tipo='FECHA_CIERRE_VENCIDA', leida=False),
        ]

        uc.ejecutar(id_prospecto=1, rut_ej_comercial=None, asignado_por=MagicMock())

        repo_procesos.obtener_procesos_comerciales.assert_called_once()
        generar.ejecutar.assert_called_once()

    def test_sigue_notificando_asignacion_y_desasignacion(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, _ = _use_case(prospecto, generar, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'asignacion_ejecutivo' in motivos
        assert 'desasignacion_ejecutivo' in motivos
