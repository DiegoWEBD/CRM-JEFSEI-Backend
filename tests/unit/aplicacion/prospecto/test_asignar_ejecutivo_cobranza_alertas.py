from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_cobranza import (
    AsignarEjecutivoCobranzaUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPO_ASIGNACION, TIPO_DESASIGNACION

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_ejecutivo_cobranza'


def _prospecto_mock(id=1, id_cliente=5, cobranza_previo=None, nombre_riesgo='Cliente Test'):
    p = MagicMock()
    p.id = id
    p.id_cliente = id_cliente
    p.nombre_riesgo = nombre_riesgo
    p.ejecutivo_cobranza_asignado = cobranza_previo
    return p


def _use_case(prospecto, rut_nuevo=None):
    repo_prospectos = MagicMock()
    repo_prospectos.buscar_cliente.return_value = prospecto
    repo_usuarios = MagicMock()
    if rut_nuevo is not None:
        repo_usuarios.buscar.return_value = MagicMock(rut=rut_nuevo)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    uc = AsignarEjecutivoCobranzaUseCase(repo_prospectos, repo_usuarios, repo_notificaciones)
    return uc, repo_prospectos, repo_notificaciones


@pytest.mark.unit
class TestAsignarEjecutivoCobranza:

    def test_cliente_no_encontrado_lanza_excepcion(self):
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = None
        uc = AsignarEjecutivoCobranzaUseCase(repo_prospectos, MagicMock(), MagicMock())

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_cliente=99, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

    def test_sin_cliente_asociado_no_llama_al_repo_ni_notifica(self):
        prospecto = _prospecto_mock(id_cliente=None)
        uc, repo_prospectos, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

        repo_prospectos.asignar_ejecutivo_cobranza.assert_not_called()
        repo_notificaciones.registrar.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoCobranzaNotificaciones:

    def test_crea_notificacion_asignacion_cliente(self, mock_hub):
        prospecto = _prospecto_mock(cobranza_previo=None)
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_called_once()
        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.codigo_tipo == TIPO_ASIGNACION
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.titulo == 'Asignación de cobranza'
        assert notificacion.mensaje == (
            'Se le ha asignado la cobranza del cliente Cliente Test.'
        )
        assert notificacion.entidad_tipo == 'CLIENTE'
        assert notificacion.entidad_id == 5
        assert notificacion.id_prospecto == 1
        assert notificacion.dedupe_key.startswith(f'{TIPO_ASIGNACION}:CLIENTE:5:cobranza:')

    def test_crea_desasignacion_solo_si_cambio(self, mock_hub):
        prospecto = _prospecto_mock(cobranza_previo=MagicMock(rut='33333333-3'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION, TIPO_DESASIGNACION]
        desasignacion = repo_notificaciones.registrar.call_args_list[1].args[0]
        assert desasignacion.rut_usuario == '33333333-3'
        assert desasignacion.dedupe_key.startswith(f'{TIPO_DESASIGNACION}:CLIENTE:5:cobranza:')

    def test_asignacion_repite_en_invocacion_sin_cambio_de_rut(self, mock_hub):
        prospecto = _prospecto_mock(cobranza_previo=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION]

    def test_nombre_entidad_usa_fallback_sin_riesgo(self, mock_hub):
        prospecto = _prospecto_mock(nombre_riesgo=None)
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.mensaje == 'Se le ha asignado la cobranza del cliente #5.'

    def test_sigue_notificando_asignacion_y_desasignacion(self, mock_hub):
        prospecto = _prospecto_mock(cobranza_previo=MagicMock(rut='33333333-3'))
        uc, _, _ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_cobranza='11111111-1', asignado_por=MagicMock())

        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'asignacion_ejecutivo' in motivos
        assert 'desasignacion_ejecutivo' in motivos
