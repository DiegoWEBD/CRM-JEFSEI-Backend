from unittest.mock import MagicMock, patch

import pytest

import app.infraestructura.prospecto.repositorio_prospectos_postgres as modulo_repo
from app.dominio.prospecto.prospecto import Prospecto
from app.infraestructura.prospecto.repositorio_prospectos_postgres import (
    RepositorioProspectosPostgres,
)

MODULO = 'app.infraestructura.prospecto.repositorio_prospectos_postgres'


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


def _prospecto(id: int | None = 1, id_cliente: int | None = 5, ejecutivo=None) -> Prospecto:
    prospecto = Prospecto(
        rut_riesgo='12345678-9',
        nombre_riesgo='Riesgo de prueba',
        telefono_contacto=None,
        correo_contacto=None,
        direccion=None,
        region=None,
        comuna=None,
        observaciones=None,
        linea_negocio=None,  # type: ignore[arg-type]
        registrado_por=None,  # type: ignore[arg-type]
        ejecutivo_comercial_asignado=ejecutivo,
        informacion_completa=False,
        id=id,
    )
    prospecto.id_cliente = id_cliente
    return prospecto


def _sin_alertas(cursor):
    """Los métodos de asignación son puros: solo persistencia."""
    for call in cursor.execute.call_args_list:
        assert 'Notificacion' not in str(call.args[0]), f'el repo tocó alertas: {call.args[0]}'


def _consultas_de(cursor, palabra: str) -> list[dict]:
    return [
        call.args[1] for call in cursor.execute.call_args_list
        if palabra in str(call.args[0])
    ]


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarEjecutivoComercialPuro:

    def test_actualiza_prospecto_y_procesos_abiertos(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto()
        prospecto.ejecutivo_comercial_asignado = MagicMock(rut='22222222-2')

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, MagicMock())

        params_prospecto = _consultas_de(cursor, 'update Prospecto')
        assert len(params_prospecto) == 1
        assert params_prospecto[0]['rut_ej_comercial'] == '22222222-2'
        assert params_prospecto[0]['id_prospecto'] == 1

        params_procesos = _consultas_de(cursor, 'update ProcesoComercial')
        assert len(params_procesos) == 1
        assert params_procesos[0]['rut_ej_comercial'] == '22222222-2'
        assert any(
            'cerrado = false' in str(call.args[0])
            for call in cursor.execute.call_args_list
            if 'update ProcesoComercial' in str(call.args[0])
        )

        _sin_alertas(cursor)

    def test_sin_id_no_hace_nada(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(_prospecto(id=None), MagicMock())

        cursor.execute.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarEjecutivoEvaluacionPuro:

    def test_actualiza_prospecto_y_procesos_abiertos(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto()
        prospecto.ejecutivo_evaluacion_asignado = MagicMock(rut='22222222-2')

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_evaluacion_proyectos(prospecto, MagicMock())

        params_prospecto = _consultas_de(cursor, 'update Prospecto')
        assert len(params_prospecto) == 1
        assert params_prospecto[0]['rut_ej_evaluacion'] == '22222222-2'

        params_procesos = _consultas_de(cursor, 'update ProcesoComercial')
        assert len(params_procesos) == 1
        assert params_procesos[0]['rut_ej_evaluacion'] == '22222222-2'

        _sin_alertas(cursor)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarEjecutivoCobranzaPuro:

    def test_actualiza_cliente(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto()
        prospecto.ejecutivo_cobranza_asignado = MagicMock(rut='22222222-2')

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_cobranza(prospecto, MagicMock())

        params_cliente = _consultas_de(cursor, 'update Cliente')
        assert len(params_cliente) == 1
        assert params_cliente[0]['rut_ej_cobranza'] == '22222222-2'
        assert params_cliente[0]['id_cliente'] == 5

        _sin_alertas(cursor)

    def test_sin_cliente_asociado_no_hace_nada(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        repo = RepositorioProspectosPostgres()
        prospecto = _prospecto()
        prospecto.id_cliente = None
        repo.asignar_ejecutivo_cobranza(prospecto, MagicMock())

        cursor.execute.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarEjecutivoRenovacionPuro:

    def test_actualiza_cliente_y_procesos_abiertos(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto()
        prospecto.ejecutivo_renovacion_asignado = MagicMock(rut='22222222-2')

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_renovacion(prospecto, MagicMock())

        params_cliente = _consultas_de(cursor, 'update Cliente')
        assert len(params_cliente) == 1
        assert params_cliente[0]['rut_ej_renovacion'] == '22222222-2'

        params_procesos = _consultas_de(cursor, 'update ProcesoComercial')
        assert len(params_procesos) == 1
        assert params_procesos[0]['rut_ej_renovacion'] == '22222222-2'

        _sin_alertas(cursor)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarAsistenteRenovacionPuro:

    def test_actualiza_cliente(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto()
        prospecto.asistente_renovacion_asignado = MagicMock(rut='22222222-2')

        repo = RepositorioProspectosPostgres()
        repo.asignar_asistente_renovacion(prospecto, MagicMock())

        params_cliente = _consultas_de(cursor, 'update Cliente')
        assert len(params_cliente) == 1
        assert params_cliente[0]['rut_as_renovacion'] == '22222222-2'

        _sin_alertas(cursor)


@pytest.mark.unit
class TestModuloLimpio:

    def test_el_modulo_no_expone_hub_ni_funciones_de_alertas(self):
        assert not hasattr(modulo_repo, 'hub')
        assert not hasattr(modulo_repo, 'EVENTO_NOTIFICACIONES_ACTUALIZADAS')
        assert not hasattr(modulo_repo, 'reasignar_destinatario_alertas')
        assert not hasattr(modulo_repo, 'registrar_notificacion_asignacion')
        assert not hasattr(modulo_repo, 'registrar_notificacion_desasignacion')
