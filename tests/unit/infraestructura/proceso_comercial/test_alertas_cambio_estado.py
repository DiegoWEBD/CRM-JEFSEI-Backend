from unittest.mock import MagicMock, patch

import pytest

import app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres as modulo_repo
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


def _consultas(cursor) -> list[str]:
    return [str(call.args[0]) for call in cursor.execute.call_args_list]


def _sin_alertas(cursor):
    """Los métodos de cambio de estado son puros: no tocan Notificacion."""
    for query in _consultas(cursor):
        assert 'Notificacion' not in query, f'el repo tocó alertas: {query}'


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestCerrarProcesoComercialPuro:

    def test_ganado_actualiza_el_proceso_y_registra_historial(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        resultado = repo.cerrar(id=1, ganado=True, observacion='obs', rut_usuario='99999999-9')

        assert resultado is None
        updates = [
            call for call in cursor.execute.call_args_list
            if 'update ProcesoComercial' in str(call.args[0])
        ]
        assert len(updates) == 1
        params_update = updates[0].args[1]
        assert params_update['cerrado'] is True
        assert params_update['codigo_estado'] == 'GANADO'
        assert params_update['id'] == 1

        historial = [
            call.args[1] for call in cursor.execute.call_args_list
            if 'insert into HistorialEstadoInformativoProcesoComercial' in str(call.args[0])
        ]
        assert len(historial) == 1
        assert historial[0]['codigo_estado'] == 'GANADO'
        assert historial[0]['observacion'] == 'obs'
        assert historial[0]['rut_registrado_por'] == '99999999-9'
        assert historial[0]['fecha_registro'] == params_update['fecha_cierre']

    def test_perdido_usa_estado_PERDIDO(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        repo.cerrar(id=1, ganado=False, observacion=None, rut_usuario='99999999-9')

        update = next(
            call.args[1] for call in cursor.execute.call_args_list
            if 'update ProcesoComercial' in str(call.args[0])
        )
        assert update['codigo_estado'] == 'PERDIDO'

    def test_no_toca_notificaciones(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        repo.cerrar(id=1, ganado=False, observacion=None, rut_usuario='99999999-9')

        _sin_alertas(cursor)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestRegistrarAceptacionClientePuro:

    def test_actualiza_estado_y_registra_historial_sin_update_duplicado(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        resultado = repo.registrar_aceptacion_cliente(id=4, rut_usuario='99999999-9')

        assert resultado is None
        updates = [
            call for call in cursor.execute.call_args_list
            if 'update ProcesoComercial' in str(call.args[0])
        ]
        assert len(updates) == 1, 'el update de estado debe ser único'
        assert updates[0].args[1]['codigo_estado'] == 'PROPUESTA_ACEPTADA'
        assert updates[0].args[1]['id'] == 4

        historial = [
            call.args[1] for call in cursor.execute.call_args_list
            if 'insert into HistorialEstadoInformativoProcesoComercial' in str(call.args[0])
        ]
        assert len(historial) == 1
        assert historial[0]['codigo_estado'] == 'PROPUESTA_ACEPTADA'
        assert historial[0]['rut_registrado_por'] == '99999999-9'

    def test_no_toca_notificaciones(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        repo.registrar_aceptacion_cliente(id=4, rut_usuario='99999999-9')

        _sin_alertas(cursor)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestNuevoProcesoComercialPuro:

    def test_crea_proceso_e_historial_sin_tocar_alertas(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'id': 1}

        repo = RepositorioProcesosComercialesPostgres()
        id_proceso = repo.nuevo(tipo='PROD-1', id_prospecto=7, rut_usuario='99999999-9')

        assert id_proceso == 1
        insert_proceso = next(
            call.args[1] for call in cursor.execute.call_args_list
            if 'insert into ProcesoComercial' in str(call.args[0])
        )
        assert insert_proceso['id_prospecto'] == 7
        assert insert_proceso['codigo_estado_actual'] == 'OPORTUNIDAD_CREADA'

        _sin_alertas(cursor)

    def test_producto_inexistente_lanza_excepcion(self, mock_conexion):
        from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException

        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = None

        repo = RepositorioProcesosComercialesPostgres()

        with pytest.raises(RecursoNoEncontradoException):
            repo.nuevo(tipo='NOEXISTE', id_prospecto=7, rut_usuario='99999999-9')

    def test_el_modulo_no_expone_hub_ni_funciones_de_alertas(self, mock_conexion):
        assert not hasattr(modulo_repo, 'hub')
        assert not hasattr(modulo_repo, 'marcar_alertas_sla_leidas')
        assert not hasattr(modulo_repo, 'marcar_alertas_fecha_leidas')
