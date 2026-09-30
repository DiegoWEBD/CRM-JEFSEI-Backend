from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.estudio_comercial_condominio.repositorio_estudios_comerciales_postgres import (
    RepositorioEstudiosComercialesPostgres,
)

MODULO = (
    'app.infraestructura.estudio_comercial_condominio'
    '.repositorio_estudios_comerciales_postgres'
)


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


def _registrar_commit(conexion) -> dict:
    estado = {'commiteado': False}

    def _al_salir(*args):
        estado['commiteado'] = True
        return False

    conexion.__exit__.side_effect = _al_salir
    return estado


@pytest.mark.unit
@patch(f'{MODULO}.hub')
@patch(f'{MODULO}.marcar_alertas_sla_leidas')
@patch(f'{MODULO}.obtener_conexion')
class TestInsertarEstudioPublicaAlertasLeidas:

    def _preparar(self, mock_conexion, mock_marcar, ruts):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        estado = _registrar_commit(conexion)
        cursor.fetchone.side_effect = [
            {'id': 5},
            {'id_proceso_comercial': 9},
        ]
        mock_marcar.return_value = ruts
        return cursor, estado

    def test_devuelve_el_id_y_publica_recien_despues_del_commit(
        self, mock_conexion, mock_marcar, mock_hub
    ):
        cursor, estado = self._preparar(mock_conexion, mock_marcar, ['11111111-1'])

        def _publicar(*args, **kwargs):
            assert estado['commiteado'], 'publicó antes del commit'

        mock_hub.publicar_desde_hilo.side_effect = _publicar

        repo = RepositorioEstudiosComercialesPostgres()
        id_estudio = repo.insertar(
            id_solicitud=3, nombre_archivo='estudio.pdf', rut_usuario='99999999-9'
        )

        assert id_estudio == 5
        assert mock_marcar.call_args.args[1] == 9
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_alertas_afectadas_no_publica(
        self, mock_conexion, mock_marcar, mock_hub
    ):
        self._preparar(mock_conexion, mock_marcar, [])

        repo = RepositorioEstudiosComercialesPostgres()
        id_estudio = repo.insertar(
            id_solicitud=3, nombre_archivo='estudio.pdf', rut_usuario='99999999-9'
        )

        assert id_estudio == 5
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_si_falla_la_transaccion_no_publica_y_no_devuelve_id(
        self, mock_conexion, mock_marcar, mock_hub
    ):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.execute.side_effect = RuntimeError('boom')

        repo = RepositorioEstudiosComercialesPostgres()

        with pytest.raises(RuntimeError):
            repo.insertar(
                id_solicitud=3, nombre_archivo='estudio.pdf', rut_usuario='99999999-9'
            )

        mock_hub.publicar_desde_hilo.assert_not_called()
