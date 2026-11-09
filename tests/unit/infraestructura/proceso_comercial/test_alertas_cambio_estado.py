from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

import app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres as modulo_repo
from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import (
    EstadoInformativoProcesoComercial,
)
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import (
    RepositorioProcesosComercialesPostgres,
)
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock

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


def _sin_alertas_ni_historial(cursor):
    """guardar es puro: solo toca ProcesoComercial, ni alertas ni historial."""
    for query in _consultas(cursor):
        assert 'Notificacion' not in query, f'el repo tocó alertas: {query}'
        assert 'HistorialEstado' not in query, f'el repo tocó historial: {query}'


def _proceso_cerrado(codigo_estado: str):
    proceso = crear_proceso_comercial_mock(id=1, cerrado=True)
    proceso.estado_actual = EstadoInformativoProcesoComercial(
        codigo=codigo_estado, nombre=''
    )
    proceso.fecha_cierre = datetime.now(tz=timezone.utc)
    return proceso


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestCerrarProcesoComercialPuro:

    def test_ganado_actualiza_el_proceso(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        proceso = _proceso_cerrado('GANADO')

        repo = RepositorioProcesosComercialesPostgres()
        resultado = repo.guardar(proceso, es_nuevo=False)

        assert resultado is proceso
        updates = [
            call for call in cursor.execute.call_args_list
            if 'UPDATE ProcesoComercial' in str(call.args[0])
        ]
        assert len(updates) == 1
        params_update = updates[0].args[1]
        assert params_update['cerrado'] is True
        assert params_update['codigo_estado_actual'] == 'GANADO'
        assert params_update['fecha_cierre'] == proceso.fecha_cierre
        assert params_update['id'] == 1

        _sin_alertas_ni_historial(cursor)

    def test_perdido_usa_estado_PERDIDO(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        proceso = _proceso_cerrado('PERDIDO')

        repo = RepositorioProcesosComercialesPostgres()
        repo.guardar(proceso, es_nuevo=False)

        update = next(
            call.args[1] for call in cursor.execute.call_args_list
            if 'UPDATE ProcesoComercial' in str(call.args[0])
        )
        assert update['codigo_estado_actual'] == 'PERDIDO'

    def test_no_toca_notificaciones(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        repo.guardar(_proceso_cerrado('GANADO'), es_nuevo=False)

        _sin_alertas_ni_historial(cursor)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestNuevoProcesoComercialPuro:

    def test_crea_proceso_sin_tocar_alertas_ni_historial(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'id': 1}

        proceso = crear_proceso_comercial_mock(id=0, id_prospecto=7)
        proceso.estado_actual = EstadoInformativoProcesoComercial(
            codigo='OPORTUNIDAD_CREADA', nombre=''
        )

        repo = RepositorioProcesosComercialesPostgres()
        resultado = repo.guardar(proceso, es_nuevo=True)

        assert resultado is proceso
        assert proceso.id == 1
        insert_proceso = next(
            call.args[1] for call in cursor.execute.call_args_list
            if 'INSERT INTO ProcesoComercial' in str(call.args[0])
        )
        assert insert_proceso['id_prospecto'] == 7
        assert insert_proceso['codigo_estado_actual'] == 'OPORTUNIDAD_CREADA'

        _sin_alertas_ni_historial(cursor)

    def test_el_modulo_no_expone_hub_ni_funciones_de_alertas(self, mock_conexion):
        assert not hasattr(modulo_repo, 'hub')
        assert not hasattr(modulo_repo, 'marcar_alertas_sla_leidas')
        assert not hasattr(modulo_repo, 'marcar_alertas_fecha_leidas')
