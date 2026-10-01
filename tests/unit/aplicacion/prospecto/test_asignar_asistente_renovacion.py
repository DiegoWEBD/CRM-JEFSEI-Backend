from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion import (
    AsignarAsistenteRenovacionUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


def _prospecto_mock(id_cliente=5):
    p = MagicMock()
    p.id_cliente = id_cliente
    p.nombre_riesgo = 'Cliente Test'
    p.id = 1
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

    @patch('app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion.hub')
    def test_publica_en_hub_al_asignar(self, mock_hub):
        prospecto = _prospecto_mock()
        usuario = MagicMock()
        usuario.rut = '11111111-1'
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        repo_usuarios.buscar.return_value = usuario
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

        uc.ejecutar(id_cliente=5, rut_as_renovacion='11111111-1', asignado_por=MagicMock())

        mock_hub.publicar_desde_hilo.assert_called_once()

    @patch('app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion.hub')
    def test_no_publica_al_desasignar(self, mock_hub):
        prospecto = _prospecto_mock()
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = prospecto
        repo_usuarios = MagicMock()
        uc = AsignarAsistenteRenovacionUseCase(repo_prospectos, repo_usuarios)

        uc.ejecutar(id_cliente=5, rut_as_renovacion=None, asignado_por=MagicMock())

        mock_hub.publicar_desde_hilo.assert_not_called()
