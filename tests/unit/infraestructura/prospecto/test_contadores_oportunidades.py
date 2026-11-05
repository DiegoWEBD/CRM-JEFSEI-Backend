from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.proceso_comercial.dto.oportunidades_contadores import OportunidadesContadores
from app.infraestructura.prospecto.adaptadores.dictrows_prospectos_resumen_adapter import (
    DictRowsProspectoResumenAdapter,
)
from app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service import (
    ConsultaProspectosPostgresService,
)

MODULO = 'app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service'


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


def _fila_prospecto(id: int) -> dict:
    return {
        'id': id,
        'id_cliente': None,
        'rut_riesgo': '12345678-9',
        'nombre_riesgo': f'Prospecto {id}',
        'nombre_fantasia': None,
        'nombre_administrador': None,
        'linea_negocio': 'Condominios',
        'ejecutivo_comercial': 'Juan Pérez',
        'estado_general_cliente': 'prospecto',
        'comuna': 'Santiago',
    }


@pytest.mark.unit
class TestContadoresOportunidades:

    def test_sin_permiso_global_separa_por_flag_renovacion(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            {'id_prospecto': 1, 'comerciales': 3, 'renovaciones': 0},
            {'id_prospecto': 2, 'comerciales': 0, 'renovaciones': 2},
        ]

        contadores = ConsultaProspectosPostgresService._obtener_contadores_oportunidades(
            cursor, [1, 2], True
        )

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'PC.cerrado = false' in query_str
        assert 'PC.id_prospecto = ANY(%(ids)s)' in query_str
        assert 'not PC.renovacion' in query_str
        assert 'PC.renovacion' in query_str
        assert 'rut_ej_comercial' not in query_str
        assert params == {'ids': [1, 2]}
        assert contadores == {
            1: OportunidadesContadores(comerciales=3, renovaciones=0),
            2: OportunidadesContadores(comerciales=0, renovaciones=2),
        }

    def test_con_permiso_propio_cuenta_segun_roles_del_usuario(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            {'id_prospecto': 7, 'comerciales': 1, 'renovaciones': 1},
        ]

        contadores = ConsultaProspectosPostgresService._obtener_contadores_oportunidades(
            cursor, [7], False, '12345678-9'
        )

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'PC.cerrado = false' in query_str
        assert 'PC.rut_ej_comercial = %(rut_usuario)s' in query_str
        assert 'PC.rut_ej_evaluacion = %(rut_usuario)s' in query_str
        assert 'PC.rut_ej_renovacion = %(rut_usuario)s' in query_str
        assert 'PC.rut_as_renovacion = %(rut_usuario)s' in query_str
        assert params == {'ids': [7], 'rut_usuario': '12345678-9'}
        assert contadores == {7: OportunidadesContadores(comerciales=1, renovaciones=1)}


@pytest.mark.unit
class TestDictRowsProspectoResumenAdapter:

    def test_asigna_contadores_por_prospecto(self):
        rows = [_fila_prospecto(1), _fila_prospecto(2)]
        contadores = {1: OportunidadesContadores(comerciales=4, renovaciones=1)}

        prospectos = DictRowsProspectoResumenAdapter(rows, contadores).to_prospectos_resumen()

        assert len(prospectos) == 2
        assert prospectos[0].oportunidades == OportunidadesContadores(comerciales=4, renovaciones=1)
        assert prospectos[1].oportunidades == OportunidadesContadores(comerciales=0, renovaciones=0)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestObtenerTodosConContadores:

    def test_los_prospectos_incluyen_contadores_de_oportunidades(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'total': 2}
        cursor.fetchall.side_effect = [
            [{'id': 1}, {'id': 2}],
            [_fila_prospecto(1), _fila_prospecto(2)],
            [{'id_prospecto': 1, 'comerciales': 4, 'renovaciones': 1}],
            [],
            [],
        ]

        service = ConsultaProspectosPostgresService()
        resultado = service.obtener_todos(
            usuario=MagicMock(rut='12345678-9'),
            oportunidades_todas=True,
        )

        assert len(resultado['data']) == 2
        assert resultado['data'][0].oportunidades == OportunidadesContadores(
            comerciales=4, renovaciones=1
        )
        assert resultado['data'][1].oportunidades == OportunidadesContadores(
            comerciales=0, renovaciones=0
        )
        assert 'contadores_estado' in resultado

        data_query = str(cursor.execute.call_args_list[2].args[0])
        assert 'P.id = ANY(%(ids)s)' in data_query
        assert 'cerrado' not in data_query

    def test_con_permiso_propio_filtra_contadores_por_usuario(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'total': 1}
        cursor.fetchall.side_effect = [
            [{'id': 1}],
            [_fila_prospecto(1)],
            [{'id_prospecto': 1, 'comerciales': 1, 'renovaciones': 0}],
            [],
            [],
        ]

        service = ConsultaProspectosPostgresService()
        service.obtener_todos(
            usuario=MagicMock(rut='12345678-9'),
            oportunidades_todas=False,
            rut_usuario_filtro='12345678-9',
        )

        query, params = cursor.execute.call_args_list[3].args
        query_str = str(query)
        assert 'PC.rut_ej_comercial = %(rut_usuario)s' in query_str
        assert 'PC.rut_ej_renovacion = %(rut_usuario)s' in query_str
        assert params == {'ids': [1], 'rut_usuario': '12345678-9'}


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestObtenerPorAdministradorConContadores:

    def test_sin_rut_separa_por_flag_renovacion(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.side_effect = [
            [_fila_prospecto(1)],
            [{'id_prospecto': 1, 'comerciales': 2, 'renovaciones': 3}],
        ]

        service = ConsultaProspectosPostgresService()
        prospectos = service.obtener_por_administrador(5)

        query, params = cursor.execute.call_args_list[1].args
        query_str = str(query)
        assert 'not PC.renovacion' in query_str
        assert 'PC.renovacion' in query_str
        assert params == {'ids': [1]}
        assert prospectos[0].oportunidades == OportunidadesContadores(
            comerciales=2, renovaciones=3
        )

    def test_con_rut_cuenta_segun_roles_del_usuario(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.side_effect = [
            [_fila_prospecto(1)],
            [{'id_prospecto': 1, 'comerciales': 0, 'renovaciones': 1}],
        ]

        service = ConsultaProspectosPostgresService()
        prospectos = service.obtener_por_administrador(5, '12345678-9')

        query, params = cursor.execute.call_args_list[1].args
        query_str = str(query)
        assert 'PC.rut_ej_evaluacion = %(rut_usuario)s' in query_str
        assert 'PC.rut_as_renovacion = %(rut_usuario)s' in query_str
        assert params == {'ids': [1], 'rut_usuario': '12345678-9'}
        assert prospectos[0].oportunidades == OportunidadesContadores(
            comerciales=0, renovaciones=1
        )
