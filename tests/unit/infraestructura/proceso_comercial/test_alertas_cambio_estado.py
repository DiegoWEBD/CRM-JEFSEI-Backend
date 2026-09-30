from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import (
    RepositorioProcesosComercialesPostgres,
)

MODULO = 'app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres'


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


def _registrar_commit(conexion) -> dict:
    """Simula el commit de psycopg al salir del with y deja el estado visible."""
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
class TestCerrarPublicaAlertasLeidas:

    def test_publica_recien_despues_del_commit(self, mock_conexion, mock_marcar, mock_hub):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        estado = _registrar_commit(conexion)
        mock_marcar.return_value = ['11111111-1']

        def _publicar(*args, **kwargs):
            assert estado['commiteado'], 'publicó antes del commit'

        mock_hub.publicar_desde_hilo.side_effect = _publicar

        repo = RepositorioProcesosComercialesPostgres()
        resultado = repo.cerrar(id=1, ganado=True, observacion=None, rut_usuario='99999999-9')

        assert resultado is None
        mock_marcar.assert_called_once()
        id_proceso, fecha = mock_marcar.call_args.args[1], mock_marcar.call_args.args[2]
        assert id_proceso == 1
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_alertas_afectadas_no_publica(self, mock_conexion, mock_marcar, mock_hub):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        mock_marcar.return_value = []

        repo = RepositorioProcesosComercialesPostgres()
        repo.cerrar(id=1, ganado=False, observacion=None, rut_usuario='99999999-9')

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_si_falla_la_transaccion_no_publica(self, mock_conexion, mock_marcar, mock_hub):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.execute.side_effect = RuntimeError('boom')

        repo = RepositorioProcesosComercialesPostgres()

        with pytest.raises(RuntimeError):
            repo.cerrar(id=1, ganado=True, observacion=None, rut_usuario='99999999-9')

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_usa_la_misma_fecha_para_historial_y_alertas(self, mock_conexion, mock_marcar, mock_hub):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        mock_marcar.return_value = []

        repo = RepositorioProcesosComercialesPostgres()
        repo.cerrar(id=1, ganado=True, observacion='obs', rut_usuario='99999999-9')

        fecha_alerta = mock_marcar.call_args.args[2]
        historial = [
            call.args[1] for call in cursor.execute.call_args_list
            if 'insert into HistorialEstadoInformativoProcesoComercial' in str(call.args[0])
        ]
        assert historial, 'no se registró el historial'
        assert historial[0]['fecha_registro'] == fecha_alerta


@pytest.mark.unit
@patch(f'{MODULO}.hub')
@patch(f'{MODULO}.marcar_alertas_sla_leidas')
@patch(f'{MODULO}.obtener_conexion')
class TestRegistrarAceptacionClientePublicaAlertasLeidas:

    def test_publica_con_motivo_cambio_estado(self, mock_conexion, mock_marcar, mock_hub):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        estado = _registrar_commit(conexion)
        mock_marcar.return_value = ['22222222-2']

        def _publicar(*args, **kwargs):
            assert estado['commiteado'], 'publicó antes del commit'

        mock_hub.publicar_desde_hilo.side_effect = _publicar

        repo = RepositorioProcesosComercialesPostgres()
        repo.registrar_aceptacion_cliente(id=4, rut_usuario='99999999-9')

        mock_marcar.assert_called_once()
        assert mock_marcar.call_args.args[1] == 4
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['22222222-2'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )
