from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion import (
    AsignarAsistenteRenovacionUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


def _prospecto_mock(id_cliente=5, asistente_previo=None):
    p = MagicMock()
    p.id_cliente = id_cliente
    p.nombre_riesgo = 'Cliente Test'
    p.id = 1
    p.asistente_renovacion_asignado = asistente_previo
    return p


@pytest.mark.unit
class TestAsignarAsistenteRenovacion:

    def test_cliente_no_encontrado_lanza_excepcion(self):
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = None
        repo_usuarios = MagicMock()
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_cliente=99, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

    def test_usuario_no_encontrado_lanza_excepcion(self):
        prospecto = _prospecto_mock()
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        repo_usuarios.buscar.return_value = None
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

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
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        assert prospecto.asistente_renovacion_asignado == usuario
        repo_prospectos.asignar_asistente_renovacion.assert_called_once()

    def test_desasignar_con_none(self):
        prospecto = _prospecto_mock()
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

        uc.ejecutar(id_cliente=5, rut_as_renovacion=None, asignado_por=MagicMock())

        assert prospecto.asistente_renovacion_asignado is None
        repo_prospectos.asignar_asistente_renovacion.assert_called_once()

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
    @patch('app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion.hub')
    def test_notifica_a_los_usuarios_correctos(self, mock_hub, previo, nuevo, esperados):
        """Verifica que cada usuario correcto recibe la notificación de asignación o desasignación."""
        asistente_previo = MagicMock(rut=previo) if previo else None
        prospecto = _prospecto_mock(asistente_previo=asistente_previo)
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        if nuevo:
            repo_usuarios.buscar.return_value = MagicMock(rut=nuevo)
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

        uc.ejecutar(id_cliente=5, rut_as_renovacion=nuevo, asignado_por=MagicMock())

        for rut_esperado, motivo_esperado in esperados:
            mock_hub.publicar_desde_hilo.assert_any_call(
                [rut_esperado],
                {'evento': 'notificaciones_actualizadas', 'motivo': motivo_esperado},
            )

        assert mock_hub.publicar_desde_hilo.call_count == len(esperados)
