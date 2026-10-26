from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from openpyxl import load_workbook

from app.main import app
from app.aplicacion.evaluacion_proyectos.use_cases.generar_desglose_unidades import GenerarDesgloseUnidadesUseCase
from app.dominio.estudio_comercial.desglose_unidades.desglose_unidad import DesgloseUnidad
from app.dominio.estudio_comercial.desglose_unidades.totales_prima import TotalesPrima
from app.infraestructura.estudio_comercial_condominio.generador_excel_desglose_unidades import GeneradorExcelDesgloseUnidades
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.estudio_comercial.deps import get_generar_desglose_unidades_use_case
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock

TIPO_CONTENIDO_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _usuario_con_permisos(*codigos: str):
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


def _datos_desglose():
    totales = TotalesPrima(
        monto_asegurado=41500.0,
        prima_afecta=24.9,
        prima_excenta=79.68,
        prima_iva=4.73,
        prima_neta=104.58,
        prima_bruta=109.31,
    )
    desglose = [
        DesgloseUnidad(
            identificador_unidad='Depto 1',
            prorrateo=0.030456521,
            monto_asegurado=200.0,
            prima_afecta=0.12,
            prima_excenta=0.38,
            prima_neta=0.5,
            prima_iva=0.02,
            prima_bruta=0.53,
            prorrateo_pago=0.3333333333333333,
            monto_reconstruccion=144.97,
            monto_asegurado_sugerido=200.0,
            valor_cuota_uf=1.06,
            valor_cuota_pesos=40280,
        ),
        DesgloseUnidad(
            identificador_unidad='Depto 2',
            prorrateo=0.069543479,
            monto_asegurado=400.0,
            prima_afecta=0.24,
            prima_excenta=0.76,
            prima_neta=1.0,
            prima_iva=0.04,
            prima_bruta=1.06,
            prorrateo_pago=0.6666666666666666,
            monto_reconstruccion=331.03,
            monto_asegurado_sugerido=400.0,
            valor_cuota_uf=2.12,
            valor_cuota_pesos=80560,
            descartada=True,
        ),
    ]

    cotizacion = MagicMock()
    cotizacion.id = 7
    cotizacion.company.nombre = 'Company'

    # (cotizacion, totales de referencia, desglose, cuota referencia UF, cuota referencia CLP)
    return [(cotizacion, totales, desglose, 218.62, 8307560)]


def _encabezado():
    return {
        'cliente': 'Condominio Prueba',
        'id_solicitud': 10,
        'fecha': datetime(2026, 1, 1),
        'cantidad_unidades': 1,
        'monto_asegurado_sugerido_total': 200.0,
        'cantidad_cuotas': 11,
        'valor_uf': 38000.0,
    }


def _ruta_xlsx(tmp_path) -> str:
    generador = GeneradorExcelDesgloseUnidades(carpeta_base=str(tmp_path))
    return generador.generar(10, _datos_desglose(), _encabezado())


@pytest.fixture
def use_case_mock():
    return MagicMock(spec=GenerarDesgloseUnidadesUseCase)


@pytest.fixture
def client_desglose(tmp_path, use_case_mock):
    usuario = _usuario_con_permisos('ARMAR_ESTUDIO_COMERCIAL')
    use_case_mock.ejecutar.return_value = _ruta_xlsx(tmp_path)

    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_generar_desglose_unidades_use_case] = lambda: use_case_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_desglose_sin_permiso(use_case_mock):
    usuario = _usuario_con_permisos('OBTENER_PROSPECTOS_TODOS')

    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_generar_desglose_unidades_use_case] = lambda: use_case_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


class TestGenerarDesgloseUnidadesEndpoint:

    def test_genera_y_descarga_el_excel(self, client_desglose, use_case_mock):
        response = client_desglose.post(
            '/estudio-comercial/unidades/desglose-excel',
            json={'id_solicitud': 10, 'ids_cotizacion': [7], 'cantidad_cuotas': 11, 'valor_uf': 38000},
        )

        assert response.status_code == 200
        assert response.headers['content-type'] == TIPO_CONTENIDO_XLSX
        assert 'desglose_unidades_solicitud_10.xlsx' in response.headers['content-disposition']
        assert response.content[:2] == b'PK'  # el .xlsx es un ZIP

        use_case_mock.ejecutar.assert_called_once()
        kwargs = use_case_mock.ejecutar.call_args.kwargs
        assert kwargs['id_solicitud'] == 10
        assert kwargs['ids_cotizacion'] == [7]
        assert kwargs['cantidad_cuotas'] == 11
        assert kwargs['valor_uf'] == 38000
        # Sin permiso global: se delega la validación con el RUT del usuario
        assert kwargs['rut_usuario'] == '12345678-9'

    def test_el_excel_solo_lista_las_unidades_no_descartadas_y_sin_columna_estado(self, client_desglose):
        response = client_desglose.post(
            '/estudio-comercial/unidades/desglose-excel',
            json={'id_solicitud': 10, 'ids_cotizacion': [7], 'cantidad_cuotas': 11, 'valor_uf': 38000},
        )

        libro = load_workbook(BytesIO(response.content))

        hoja_prorrateo = libro['Prorrateo metros cuadrados']
        assert [celda.value for celda in hoja_prorrateo[5]] == [
            'Unidad', 'Prorrateo (m²)', 'Monto de reconstrucción (UF)',
            'Monto asegurado sugerido (UF)', 'Monto asegurado (UF)',
        ]
        assert hoja_prorrateo['A6'].value == 'Depto 1'
        assert hoja_prorrateo['A7'].value == 'TOTAL'

        hoja_desglose = libro['Desglose cotizaciones']
        assert [celda.value for celda in hoja_desglose[6]] == [
            'Unidad', 'Monto asegurado (UF)', 'Prorrateo por monto asegurado',
            'Prima bruta (UF)', 'Valor cuota (UF)', 'Valor cuota (CLP)',
        ]
        assert hoja_desglose['A7'].value == 'Depto 1'
        assert hoja_desglose['A8'].value == 'TOTAL'

        valores = {
            celda.value
            for hoja in libro.worksheets
            for fila in hoja.iter_rows()
            for celda in fila
            if isinstance(celda.value, str)
        }
        assert not {'Estado', 'Activa', 'Descartada'} & valores

    def test_sin_permiso_es_rechazado(self, client_desglose_sin_permiso, use_case_mock):
        response = client_desglose_sin_permiso.post(
            '/estudio-comercial/unidades/desglose-excel',
            json={'id_solicitud': 10, 'ids_cotizacion': [7], 'cantidad_cuotas': 11, 'valor_uf': 38000},
        )

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_not_called()
