from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

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


def _registrar_commit(conexion) -> dict:
    estado = {'commiteado': False}

    def _al_salir(*args):
        estado['commiteado'] = True
        return False

    conexion.__exit__.side_effect = _al_salir
    return estado


def _prospecto(id: int | None = 1, ejecutivo=None) -> Prospecto:
    return Prospecto(
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


@pytest.mark.unit
@patch(f'{MODULO}.hub')
@patch(f'{MODULO}.reasignar_destinatario_alertas')
@patch(f'{MODULO}.marcar_alertas_fecha_leidas_por_prospecto')
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarEjecutivoComercial:

    def test_cambia_destinatario_solo_segun_rol_responsable(
        self, mock_conexion, mock_marcar, mock_reasignar, mock_hub
    ):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        _registrar_commit(conexion)
        mock_marcar.return_value = set()
        mock_reasignar.return_value = ({'11111111-1'}, {'22222222-2'})
        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        args = mock_reasignar.call_args.args
        assert args[1] == 1
        assert args[2] == 'EJECUTIVO_COMERCIAL'
        assert args[3] == '22222222-2'

    def test_publica_recien_despues_del_commit(self, mock_conexion, mock_marcar, mock_reasignar, mock_hub):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        estado = _registrar_commit(conexion)
        mock_marcar.return_value = set()
        mock_reasignar.return_value = ({'11111111-1'}, {'22222222-2'})

        def _publicar(*args, **kwargs):
            assert estado['commiteado'], 'publicó antes del commit'

        mock_hub.publicar_desde_hilo.side_effect = _publicar
        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            {'11111111-1', '22222222-2'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )

    def test_desasignacion_pone_alertas_en_null_y_notifica_solo_a_previos(
        self, mock_conexion, mock_marcar, mock_reasignar, mock_hub
    ):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        _registrar_commit(conexion)
        mock_marcar.return_value = set()
        mock_reasignar.return_value = ({'11111111-1'}, set())
        prospecto = _prospecto(ejecutivo=None)

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        assert mock_reasignar.call_args.args[3] is None
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            {'11111111-1'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )

    def test_sin_alertas_afectadas_no_publica(
        self, mock_conexion, mock_marcar, mock_reasignar, mock_hub
    ):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        mock_marcar.return_value = set()
        mock_reasignar.return_value = (set(), set())
        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_sin_prospecto_no_hace_nada(self, mock_conexion, mock_marcar, mock_reasignar, mock_hub):
        prospecto = _prospecto(id=None, ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        mock_conexion.assert_not_called()
        mock_marcar.assert_not_called()
        mock_reasignar.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_marca_alertas_fecha_leidas_dentro_de_la_transaccion(
        self, mock_conexion, mock_marcar, mock_reasignar, mock_hub
    ):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        estado = _registrar_commit(conexion)
        mock_reasignar.return_value = (set(), set())

        def _dentro_de_transaccion(*args, **kwargs):
            assert not estado['commiteado'], 'marcó alertas de fecha fuera de la transacción'
            return {'11111111-1'}

        mock_marcar.side_effect = _dentro_de_transaccion
        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        args = mock_marcar.call_args.args
        assert args[0] is cursor
        assert args[1] == 1
        assert isinstance(args[2], datetime)

    def test_publica_ruts_de_alertas_fecha_junto_con_reasignados(
        self, mock_conexion, mock_marcar, mock_reasignar, mock_hub
    ):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        _registrar_commit(conexion)
        mock_marcar.return_value = {'33333333-3'}
        mock_reasignar.return_value = ({'11111111-1'}, {'22222222-2'})
        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            {'11111111-1', '22222222-2', '33333333-3'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )

    def test_sin_cambio_de_rut_no_marca_alertas_fecha(
        self, mock_conexion, mock_marcar, mock_reasignar, mock_hub
    ):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        _registrar_commit(conexion)
        cursor.fetchone.return_value = {'rut_ej_comercial_asignado': '22222222-2'}
        mock_marcar.return_value = set()
        mock_reasignar.return_value = (set(), set())
        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_comercial(prospecto, asignado_por=SimpleNamespace(rut='99999999-9'))

        mock_marcar.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO}.hub')
@patch(f'{MODULO}.reasignar_destinatario_alertas')
@patch(f'{MODULO}.obtener_conexion')
class TestAsignarEjecutivoEvaluacion:

    def test_usa_el_rol_de_evaluacion_y_no_el_comercial(
        self, mock_conexion, mock_reasignar, mock_hub
    ):
        conexion, _ = _conexion_mock()
        mock_conexion.return_value = conexion
        _registrar_commit(conexion)
        mock_reasignar.return_value = ({'33333333-3'}, {'44444444-4'})

        prospecto = _prospecto(ejecutivo=SimpleNamespace(rut='22222222-2'))
        prospecto.ejecutivo_evaluacion_asignado = SimpleNamespace(rut='44444444-4')

        repo = RepositorioProspectosPostgres()
        repo.asignar_ejecutivo_evaluacion_proyectos(
            prospecto, asignado_por=SimpleNamespace(rut='99999999-9')
        )

        args = mock_reasignar.call_args.args
        assert args[1] == 1
        assert args[2] == 'EJECUTIVO_EVALUACION_PROYECTOS'
        assert args[3] == '44444444-4'
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            {'33333333-3', '44444444-4'},
            {'evento': 'notificaciones_actualizadas', 'motivo': 'destinatarios_reasignados'},
        )
