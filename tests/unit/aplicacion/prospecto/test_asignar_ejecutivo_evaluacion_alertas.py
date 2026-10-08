from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_evaluacion import (
    AsignarEjecutivoEvaluacionUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import (
    ROL_EJECUTIVO_EVALUACION_PROYECTOS,
    TIPO_ASIGNACION,
    TIPO_DESASIGNACION,
)

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_ejecutivo_evaluacion'


def _prospecto_mock(id=1, evaluacion_previo=None, nombre_riesgo='Prospecto Test'):
    p = MagicMock()
    p.id = id
    p.nombre_riesgo = nombre_riesgo
    p.ejecutivo_evaluacion_asignado = evaluacion_previo
    return p


def _use_case(prospecto, rut_nuevo=None):
    repo_prospectos = MagicMock()
    repo_prospectos.buscar.return_value = prospecto
    repo_usuarios = MagicMock()
    if rut_nuevo is not None:
        repo_usuarios.buscar.return_value = MagicMock(rut=rut_nuevo)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    repo_notificaciones.buscar_notificaciones_sla_por_rol.return_value = []
    uc = AsignarEjecutivoEvaluacionUseCase(repo_prospectos, repo_usuarios, repo_notificaciones)
    return uc, repo_prospectos, repo_notificaciones


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoEvaluacionReasignacionAlertasSla:

    def test_reasigna_alertas_sla_del_rol_evaluacion(self, mock_hub):
        from tests.factories.notificacion_factory import crear_notificacion_mock

        prospecto = _prospecto_mock(evaluacion_previo=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='22222222-2')
        alerta = crear_notificacion_mock(id=1, rut_usuario='11111111-1', codigo_tipo='SLA_VENCIDO')
        repo_notificaciones.buscar_notificaciones_sla_por_rol.return_value = [alerta]

        uc.ejecutar(id_prospecto=1, rut_ej_evaluacion='22222222-2', asignado_por=MagicMock())

        repo_notificaciones.buscar_notificaciones_sla_por_rol.assert_called_once_with(
            1, ROL_EJECUTIVO_EVALUACION_PROYECTOS
        )
        assert alerta.rut_usuario == '22222222-2'
        repo_notificaciones.actualizar.assert_called_once_with(alerta)
        mock_hub.publicar_desde_hilo.assert_any_call(
            {'11111111-1', '22222222-2'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )

    def test_no_reasigna_sla_si_el_rut_no_cambia(self, mock_hub):
        prospecto = _prospecto_mock(evaluacion_previo=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_prospecto=1, rut_ej_evaluacion='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.buscar_notificaciones_sla_por_rol.assert_not_called()
        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'destinatarios_reasignados' not in motivos


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoEvaluacionNotificacionesAsignacion:

    def test_crea_notificacion_asignacion_evaluacion_tecnica(self, mock_hub):
        prospecto = _prospecto_mock(evaluacion_previo=None)
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_evaluacion='22222222-2', asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_called_once()
        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.codigo_tipo == TIPO_ASIGNACION
        assert notificacion.rut_usuario == '22222222-2'
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.titulo == 'Asignación de evaluación técnica'
        assert notificacion.mensaje == (
            'Se le ha asignado la evaluación técnica del prospecto Prospecto Test.'
        )
        assert notificacion.entidad_tipo == 'PROSPECTO'
        assert notificacion.entidad_id == 1
        assert notificacion.dedupe_key.startswith(
            f'{TIPO_ASIGNACION}:PROSPECTO:1:evaluación técnica:'
        )

    def test_crea_desasignacion_solo_si_cambio(self, mock_hub):
        prospecto = _prospecto_mock(evaluacion_previo=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_evaluacion='22222222-2', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION, TIPO_DESASIGNACION]
        desasignacion = repo_notificaciones.registrar.call_args_list[1].args[0]
        assert desasignacion.rut_usuario == '11111111-1'
        assert desasignacion.dedupe_key.startswith(
            f'{TIPO_DESASIGNACION}:PROSPECTO:1:evaluación técnica:'
        )

    def test_asignacion_repite_en_invocacion_sin_cambio_de_rut(self, mock_hub):
        prospecto = _prospecto_mock(evaluacion_previo=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_prospecto=1, rut_ej_evaluacion='11111111-1', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION]

    def test_sigue_notificando_asignacion_y_desasignacion(self, mock_hub):
        prospecto = _prospecto_mock(evaluacion_previo=MagicMock(rut='11111111-1'))
        uc, _, _ = _use_case(prospecto, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_evaluacion='22222222-2', asignado_por=MagicMock())

        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'asignacion_ejecutivo' in motivos
        assert 'desasignacion_ejecutivo' in motivos
