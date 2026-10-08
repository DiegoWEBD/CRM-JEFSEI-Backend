from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion import (
    AsignarAsistenteRenovacionUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPO_ASIGNACION, TIPO_DESASIGNACION

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion'


def _prospecto_mock(id=1, id_cliente=5, asistente_previo=None, nombre_riesgo='Cliente Test'):
    p = MagicMock()
    p.id = id
    p.id_cliente = id_cliente
    p.nombre_riesgo = nombre_riesgo
    p.asistente_renovacion_asignado = asistente_previo
    return p


def _use_case(prospecto, rut_nuevo=None):
    repo_prospectos = MagicMock()
    repo_prospectos.buscar_cliente.return_value = prospecto
    repo_usuarios = MagicMock()
    if rut_nuevo is not None:
        repo_usuarios.buscar.return_value = MagicMock(rut=rut_nuevo)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios, repo_notificaciones)
    return uc, repo_prospectos, repo_notificaciones


@pytest.mark.unit
class TestAsignarAsistenteRenovacion:

    def test_cliente_no_encontrado_lanza_excepcion(self):
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = None
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, MagicMock(), MagicMock())

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_cliente=99, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

    def test_usuario_no_encontrado_lanza_excepcion(self):
        prospecto = _prospecto_mock()
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        repo_usuarios.buscar.return_value = None
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios, MagicMock())

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_cliente=5, rut_as_renovacion='99999999-9', asignado_por=MagicMock())

    def test_asigna_asistente_correctamente(self):
        prospecto = _prospecto_mock()
        usuario = MagicMock()
        usuario.rut = '11111111-1'
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        repo_usuarios.buscar.return_value = usuario
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios, MagicMock())

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        assert prospecto.asistente_renovacion_asignado == usuario
        repo_prospectos.asignar_asistente_renovacion.assert_called_once()

    def test_desasignar_con_none(self):
        prospecto = _prospecto_mock()
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios, MagicMock())

        uc.ejecutar(id_cliente=5, rut_as_renovacion=None, asignado_por=MagicMock())

        assert prospecto.asistente_renovacion_asignado is None
        repo_prospectos.asignar_asistente_renovacion.assert_called_once()

    def test_sin_cliente_asociado_no_llama_al_repo_ni_notifica(self):
        prospecto = _prospecto_mock(id_cliente=None)
        uc, repo_prospectos, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        repo_prospectos.asignar_asistente_renovacion.assert_not_called()
        repo_notificaciones.registrar.assert_not_called()

    @pytest.mark.parametrize(
        'previo, nuevo, esperados',
        [
            # (asistente previo, RUT nuevo, [(RUT destino, motivo)])
            ('33333333-3', '11111111-1', [('11111111-1', 'asignacion_ejecutivo'),
                                           ('33333333-3', 'desasignacion_ejecutivo')]),
            ('33333333-3', None,           [('33333333-3', 'desasignacion_ejecutivo')]),
            (None,        '11111111-1',   [('11111111-1', 'asignacion_ejecutivo')]),
            (None,        None,            []),
        ],
    )
    @patch(f'{MODULO}.hub')
    def test_notifica_a_los_usuarios_correctos(self, mock_hub, previo, nuevo, esperados):
        """Verifica que cada usuario correcto recibe la notificación de asignación o desasignación."""
        asistente_previo = MagicMock(rut=previo) if previo else None
        prospecto = _prospecto_mock(asistente_previo=asistente_previo)
        uc, _, _ = _use_case(prospecto, rut_nuevo=nuevo)

        uc.ejecutar(id_cliente=5, rut_as_renovacion=nuevo, asignado_por=MagicMock())

        for rut_esperado, motivo_esperado in esperados:
            mock_hub.publicar_desde_hilo.assert_any_call(
                [rut_esperado],
                {'evento': 'notificaciones_actualizadas', 'motivo': motivo_esperado},
            )

        assert mock_hub.publicar_desde_hilo.call_count == len(esperados)


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarAsistenteRenovacionNotificaciones:

    def test_crea_notificacion_asignacion_cliente(self, mock_hub):
        prospecto = _prospecto_mock(asistente_previo=None)
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_called_once()
        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.codigo_tipo == TIPO_ASIGNACION
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.titulo == 'Asignación de asistencia de renovación'
        assert notificacion.mensaje == (
            'Se le ha asignado la asistencia de renovación del cliente Cliente Test.'
        )
        assert notificacion.entidad_tipo == 'CLIENTE'
        assert notificacion.entidad_id == 5
        assert notificacion.id_prospecto == 1
        assert notificacion.dedupe_key.startswith(
            f'{TIPO_ASIGNACION}:CLIENTE:5:asistencia de renovación:'
        )

    def test_crea_desasignacion_solo_si_cambio(self, mock_hub):
        prospecto = _prospecto_mock(asistente_previo=MagicMock(rut='33333333-3'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION, TIPO_DESASIGNACION]
        desasignacion = repo_notificaciones.registrar.call_args_list[1].args[0]
        assert desasignacion.rut_usuario == '33333333-3'
        assert desasignacion.dedupe_key.startswith(
            f'{TIPO_DESASIGNACION}:CLIENTE:5:asistencia de renovación:'
        )

    def test_asignacion_repite_en_invocacion_sin_cambio_de_rut(self, mock_hub):
        prospecto = _prospecto_mock(asistente_previo=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION]
