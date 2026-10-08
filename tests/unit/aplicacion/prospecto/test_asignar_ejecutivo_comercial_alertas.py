from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial import (
    AsignarEjecutivoComercialUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import (
    ROL_EJECUTIVO_COMERCIAL,
    TIPOS_ALERTA_FECHA,
    TIPO_ASIGNACION,
    TIPO_DESASIGNACION,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import crear_notificacion_mock

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial'


def _prospecto_mock(id=1, ejecutivo_previo=None, nombre_riesgo='Prospecto Test'):
    p = MagicMock()
    p.id = id
    p.nombre_riesgo = nombre_riesgo
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
    repo_notificaciones.buscar_notificaciones_sla_por_rol.return_value = []
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = []
    generar_alerta_cierre.ejecutar.return_value = None
    uc = AsignarEjecutivoComercialUseCase(
        repo_prospectos,
        repo_usuarios,
        repo_procesos,
        repo_notificaciones,
        generar_alerta_cierre,
        servicio_alertas,
    )
    return uc, repo_prospectos, repo_procesos, repo_notificaciones, servicio_alertas


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoComercialFlujoFecha:

    def test_reevalua_por_proceso_abierto_del_prospecto(self, _mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, repo_prospectos, repo_procesos, _, _ = _use_case(
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

    def test_marca_leidas_las_alertas_de_fecha_via_servicio(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, _, servicio_alertas = _use_case(
            prospecto, generar, rut_nuevo='22222222-2',
            procesos=[_proceso_mock(id=42)],
        )
        servicio_alertas.marcar_leidas.return_value = ['11111111-1']

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        servicio_alertas.marcar_leidas.assert_called_once()
        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_FECHA
        assert isinstance(args[2], datetime)
        destinos = mock_hub.publicar_desde_hilo.call_args_list[0].args[0]
        assert destinos == ['11111111-1']

    def test_agrega_la_alerta_creada_a_destinatarios(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, _, _ = _use_case(
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
        uc, _, _, _, _ = _use_case(
            prospecto, generar, rut_nuevo='11111111-1', procesos=[_proceso_mock(id=42)]
        )
        creada = crear_notificacion_mock(id=None, rut_usuario='11111111-1', codigo_tipo='FECHA_CIERRE_VENCIDA')
        generar.ejecutar.return_value = creada

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        generar.ejecutar.assert_called_once()

    def test_no_hace_nada_si_el_rut_no_cambia(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, repo_procesos, repo_notificaciones, servicio_alertas = _use_case(
            prospecto, generar, rut_nuevo='11111111-1', procesos=[_proceso_mock(id=42)]
        )

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='11111111-1', asignado_por=MagicMock())

        repo_procesos.obtener_procesos_comerciales.assert_not_called()
        repo_notificaciones.buscar_notificaciones_sla_por_rol.assert_not_called()
        servicio_alertas.marcar_leidas.assert_not_called()
        generar.ejecutar.assert_not_called()

    def test_desasignacion_tambien_marca_y_reevalua(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, repo_procesos, _, servicio_alertas = _use_case(
            prospecto, generar, rut_nuevo=None, procesos=[_proceso_mock(id=42)]
        )

        uc.ejecutar(id_prospecto=1, rut_ej_comercial=None, asignado_por=MagicMock())

        repo_procesos.obtener_procesos_comerciales.assert_called_once()
        assert servicio_alertas.marcar_leidas.call_count == 1
        generar.ejecutar.assert_called_once()

    def test_sigue_notificando_asignacion_y_desasignacion(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, _, _ = _use_case(prospecto, generar, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'asignacion_ejecutivo' in motivos
        assert 'desasignacion_ejecutivo' in motivos


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoComercialReasignacionAlertasSla:

    def test_reasigna_alertas_sla_y_publica_destinatarios(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo='22222222-2')
        alerta = crear_notificacion_mock(id=1, rut_usuario='11111111-1', codigo_tipo='SLA_VENCIDO')
        alerta_sin_rut = crear_notificacion_mock(id=2, rut_usuario=None, codigo_tipo='SLA_POR_VENCER')
        repo_notificaciones.buscar_notificaciones_sla_por_rol.return_value = [alerta, alerta_sin_rut]

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        repo_notificaciones.buscar_notificaciones_sla_por_rol.assert_called_once_with(
            1, ROL_EJECUTIVO_COMERCIAL
        )
        assert alerta.rut_usuario == '22222222-2'
        assert alerta_sin_rut.rut_usuario == '22222222-2'
        assert repo_notificaciones.actualizar.call_count == 2
        mock_hub.publicar_desde_hilo.assert_any_call(
            {'11111111-1', '22222222-2'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )

    def test_no_reasigna_sla_si_el_rut_no_cambia(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo='11111111-1')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.buscar_notificaciones_sla_por_rol.assert_not_called()
        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'destinatarios_reasignados' not in motivos

    def test_desasignacion_sla_publica_solo_previos(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo=None)
        alerta = crear_notificacion_mock(id=1, rut_usuario='11111111-1', codigo_tipo='SLA_VENCIDO')
        repo_notificaciones.buscar_notificaciones_sla_por_rol.return_value = [alerta]

        uc.ejecutar(id_prospecto=1, rut_ej_comercial=None, asignado_por=MagicMock())

        assert alerta.rut_usuario is None
        mock_hub.publicar_desde_hilo.assert_any_call(
            {'11111111-1'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )

    def test_alertas_ya_asignadas_al_nuevo_rut_no_se_tocan(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo='22222222-2')
        alerta_propia = crear_notificacion_mock(id=1, rut_usuario='22222222-2', codigo_tipo='SLA_VENCIDO')
        repo_notificaciones.buscar_notificaciones_sla_por_rol.return_value = [alerta_propia]

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        repo_notificaciones.actualizar.assert_not_called()
        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'destinatarios_reasignados' not in motivos


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoComercialNotificacionesAsignacion:

    def test_crea_notificacion_asignacion_en_cada_invocacion_con_rut(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo='11111111-1')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_called_once()
        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.codigo_tipo == TIPO_ASIGNACION
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.leida is False
        assert notificacion.fecha_leida is None
        assert notificacion.titulo == 'Asignación de gestión comercial'
        assert notificacion.mensaje == (
            'Se le ha asignado la gestión comercial del prospecto Prospecto Test.'
        )
        assert notificacion.entidad_tipo == 'PROSPECTO'
        assert notificacion.entidad_id == 1
        assert notificacion.id_prospecto == 1
        assert notificacion.dedupe_key.startswith(
            f'{TIPO_ASIGNACION}:PROSPECTO:1:gestión comercial:'
        )

    def test_crea_desasignacion_solo_si_cambio(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION, TIPO_DESASIGNACION]
        desasignacion = repo_notificaciones.registrar.call_args_list[1].args[0]
        assert desasignacion.rut_usuario == '11111111-1'
        assert desasignacion.titulo == 'Desasignación de gestión comercial'
        assert desasignacion.mensaje == (
            'Se le ha desasignado la gestión comercial del prospecto Prospecto Test.'
        )
        assert desasignacion.dedupe_key.startswith(
            f'{TIPO_DESASIGNACION}:PROSPECTO:1:gestión comercial:'
        )

    def test_no_crea_notificaciones_sin_previo_ni_nuevo(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=None)
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo=None)

        uc.ejecutar(id_prospecto=1, rut_ej_comercial=None, asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_not_called()

    def test_nombre_entidad_usa_fallback_sin_riesgo(self, mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=None, nombre_riesgo=None)
        generar = MagicMock()
        uc, _, _, repo_notificaciones, _ = _use_case(prospecto, generar, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.mensaje == (
            'Se le ha asignado la gestión comercial del prospecto #1.'
        )
