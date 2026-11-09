from unittest.mock import MagicMock, patch

import pytest

import app.infraestructura.prospecto.repositorio_prospectos_postgres as modulo_repo
from app.dominio.prospecto.prospecto import Prospecto
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import (
    RepositorioProcesosComercialesPostgres,
)
from app.infraestructura.prospecto.repositorio_prospectos_postgres import (
    RepositorioProspectosPostgres,
)
from tests.factories.linea_negocio_factory import crear_linea_negocio_mock
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.usuario_factory import crear_usuario_mock

MODULO = 'app.infraestructura.prospecto.repositorio_prospectos_postgres'
MODULO_PROCESOS = 'app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres'


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


def _prospecto(id: int | None = 1, **ejecutivos) -> Prospecto:
    """Prospecto real con los ejecutivos informados por nombre de atributo.

    Los métodos de asignación son puros: solo persistencia. La actualización
    del prospecto persiste los ejecutivos comerciales/de evaluación en
    Prospecto y los de cobranza/renovación/asistencia en Cliente.
    """
    prospecto = Prospecto(
        rut_riesgo='12345678-9',
        nombre_riesgo='Riesgo de prueba',
        telefono_contacto=None,
        correo_contacto=None,
        direccion='Av. Principal 123',
        region='Metropolitana',
        comuna='Santiago',
        observaciones=None,
        linea_negocio=crear_linea_negocio_mock(),
        registrado_por=crear_usuario_mock(),
        ejecutivo_comercial_asignado=ejecutivos.get('ejecutivo_comercial'),
        ejecutivo_evaluacion_asignado=ejecutivos.get('ejecutivo_evaluacion'),
        ejecutivo_cobranza_asignado=ejecutivos.get('ejecutivo_cobranza'),
        ejecutivo_renovacion_asignado=ejecutivos.get('ejecutivo_renovacion'),
        asistente_renovacion_asignado=ejecutivos.get('asistente_renovacion'),
        informacion_completa=False,
        id=id,
    )
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
class TestActualizarProspectoEjecutivos:

    def test_persiste_los_ejecutivos_comercial_y_de_evaluacion_en_el_prospecto(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto(
            ejecutivo_comercial=crear_usuario_mock(rut='22222222-2'),
            ejecutivo_evaluacion=crear_usuario_mock(rut='33333333-3'),
        )

        RepositorioProspectosPostgres().actualizar_prospecto(prospecto)

        params_prospecto = _consultas_de(cursor, 'update Prospecto')
        assert len(params_prospecto) == 1
        assert params_prospecto[0]['rut_ej_comercial_asignado'] == '22222222-2'
        assert params_prospecto[0]['rut_ej_evaluacion_asignado'] == '33333333-3'
        assert params_prospecto[0]['id'] == 1

    def test_persiste_los_ejecutivos_de_cobranza_renovacion_y_asistente_en_el_cliente(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto(
            ejecutivo_cobranza=crear_usuario_mock(rut='44444444-4'),
            ejecutivo_renovacion=crear_usuario_mock(rut='55555555-5'),
            asistente_renovacion=crear_usuario_mock(rut='66666666-6'),
        )

        RepositorioProspectosPostgres().actualizar_prospecto(prospecto)

        params_cliente = _consultas_de(cursor, 'update Cliente')
        assert len(params_cliente) == 1
        assert params_cliente[0]['rut_ej_cobranza_asignado'] == '44444444-4'
        assert params_cliente[0]['rut_ej_renovacion_asignado'] == '55555555-5'
        assert params_cliente[0]['rut_as_renovacion_asignado'] == '66666666-6'
        assert params_cliente[0]['id_prospecto'] == 1

    def test_sin_ejecutivos_deja_los_ruts_en_none(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        prospecto = _prospecto()

        RepositorioProspectosPostgres().actualizar_prospecto(prospecto)

        assert _consultas_de(cursor, 'update Prospecto')[0]['rut_ej_comercial_asignado'] is None
        assert _consultas_de(cursor, 'update Prospecto')[0]['rut_ej_evaluacion_asignado'] is None
        assert _consultas_de(cursor, 'update Cliente')[0]['rut_ej_cobranza_asignado'] is None
        assert _consultas_de(cursor, 'update Cliente')[0]['rut_ej_renovacion_asignado'] is None
        assert _consultas_de(cursor, 'update Cliente')[0]['rut_as_renovacion_asignado'] is None

    def test_sin_id_no_hace_nada(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        RepositorioProspectosPostgres().actualizar_prospecto(_prospecto(id=None))

        cursor.execute.assert_not_called()

    def test_no_toca_alertas(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        RepositorioProspectosPostgres().actualizar_prospecto(_prospecto())

        _sin_alertas(cursor)


@pytest.mark.unit
@patch(f'{MODULO_PROCESOS}.obtener_conexion')
class TestActualizarProcesoComercialEjecutivos:

    def test_persiste_los_ejecutivos_en_la_oportunidad(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        proceso = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='22222222-2'),
            ejecutivo_evaluacion=crear_usuario_mock(rut='33333333-3'),
            ejecutivo_renovacion=crear_usuario_mock(rut='44444444-4'),
            asistente_renovacion=crear_usuario_mock(rut='55555555-5'),
        )

        RepositorioProcesosComercialesPostgres().guardar(proceso, es_nuevo=False)

        query, params = cursor.execute.call_args.args
        assert 'UPDATE ProcesoComercial' in str(query)
        assert params['rut_ej_comercial'] == '22222222-2'
        assert params['rut_ej_evaluacion'] == '33333333-3'
        assert params['rut_ej_renovacion'] == '44444444-4'
        assert params['rut_as_renovacion'] == '55555555-5'

    def test_sin_ejecutivos_deja_los_ruts_en_none(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        proceso = crear_proceso_comercial_mock()

        RepositorioProcesosComercialesPostgres().guardar(proceso, es_nuevo=False)

        params = cursor.execute.call_args.args[1]
        assert params['rut_ej_comercial'] is None
        assert params['rut_ej_evaluacion'] is None
        assert params['rut_ej_renovacion'] is None
        assert params['rut_as_renovacion'] is None

    def test_no_toca_alertas(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        RepositorioProcesosComercialesPostgres().guardar(crear_proceso_comercial_mock(), es_nuevo=False)

        _sin_alertas(cursor)


@pytest.mark.unit
class TestModuloLimpio:

    def test_el_modulo_no_expone_hub_ni_funciones_de_alertas(self):
        assert not hasattr(modulo_repo, 'hub')
        assert not hasattr(modulo_repo, 'EVENTO_NOTIFICACIONES_ACTUALIZADAS')
        assert not hasattr(modulo_repo, 'reasignar_destinatario_alertas')
        assert not hasattr(modulo_repo, 'registrar_notificacion_asignacion')
        assert not hasattr(modulo_repo, 'registrar_notificacion_desasignacion')
