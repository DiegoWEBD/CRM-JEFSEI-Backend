from unittest.mock import MagicMock

import pytest

from app.aplicacion.proceso_comercial.use_cases.calcular_desglose_reconstruccion_unidades import (
    CalcularDesgloseReconstruccionUnidadesUseCase,
)
from app.aplicacion.proceso_comercial.use_cases.generar_excel_desglose_reconstruccion_unidades import (
    GenerarExcelDesgloseReconstruccionUnidadesUseCase,
)
from app.aplicacion.proceso_comercial.use_cases.obtener_desglose_reconstruccion_unidades import (
    ObtenerDesgloseReconstruccionUnidadesUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import CalculadoraDesgloseReconstruccion
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota

AUSENTE = object()


def _prospecto():
    prospecto = MagicMock()
    prospecto.metros_cuadrados = 1000
    prospecto.uf_por_metro_cuadrado = 10.0
    prospecto.porcentaje_depreciacion = 0.2
    return prospecto


def _unidades():
    return [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.030456521, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
    ]


def _desglose():
    # Fixture con montos de ejemplo: 4.760 UF repartidas por el prorrateo de cada
    # unidad: Depto 1: 4.760 × 0,030456521 = 144,97303996 → 200 | Depto 2: 331,02696004 → 400
    return CalculadoraDesgloseReconstruccion.calcular(4760.0, _unidades())


def _uc_calcular(prospecto=AUSENTE):
    repositorio_prospectos = MagicMock()
    repositorio_prospectos.buscar_prospecto_condominio.return_value = (
        _prospecto() if prospecto is AUSENTE else prospecto
    )
    return CalcularDesgloseReconstruccionUnidadesUseCase(repositorio_prospectos)


def _proceso(id=42, id_prospecto=5):
    proceso = MagicMock()
    proceso.id = id
    proceso.id_prospecto = id_prospecto
    return proceso


def _mock_calcular(desglose=AUSENTE, total=600.0):
    calcular = MagicMock()
    calcular.ejecutar.return_value = (
        (_desglose() if desglose is AUSENTE else desglose),
        total,
    )
    return calcular


def _use_case_obtener(calcular=None, proceso=AUSENTE, autorizado=True):
    repositorio_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repositorio_procesos.buscar.return_value = _proceso() if proceso is AUSENTE else proceso

    repositorio_unidades = MagicMock(spec=RepositorioUnidadesAlicuotas)
    repositorio_unidades.listar_por_oportunidad.return_value = _unidades()

    authorization = MagicMock()
    authorization.usuario_puede_ver_solicitudes_cotizacion.return_value = autorizado

    uc = ObtenerDesgloseReconstruccionUnidadesUseCase(
        repositorio_procesos,
        repositorio_unidades,
        calcular if calcular is not None else _mock_calcular(),
        authorization,
    )
    return uc, repositorio_unidades


def _use_case_excel(calcular=None, proceso=AUSENTE, autorizado=True, unidades=None):
    repositorio_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repositorio_procesos.buscar.return_value = _proceso() if proceso is AUSENTE else proceso

    repositorio_unidades = MagicMock(spec=RepositorioUnidadesAlicuotas)
    repositorio_unidades.listar_por_oportunidad.return_value = (
        _unidades() if unidades is None else unidades
    )

    authorization = MagicMock()
    authorization.usuario_puede_ver_solicitudes_cotizacion.return_value = autorizado

    generador_excel = MagicMock()
    generador_excel.generar.return_value = 'documentos/estudios/desglose/desglose.xlsx'

    uc = GenerarExcelDesgloseReconstruccionUnidadesUseCase(
        repositorio_procesos,
        repositorio_unidades,
        calcular if calcular is not None else _mock_calcular(),
        authorization,
        generador_excel,
    )
    return uc, generador_excel


@pytest.mark.unit
class TestCalcularDesgloseReconstruccionUnidades:

    def test_calcula_montos_prorrateo_de_pago_y_total(self):
        uc = _uc_calcular()

        desglose, total = uc.ejecutar(5, _unidades())

        # Regla de negocio vigente: el valor de las unidades NO se deprecia
        # valor_unidades = 11.900 x 0,5 = 5.950 (sin redondear por unidad)
        assert [u.identificador_unidad for u in desglose] == ['Depto 1', 'Depto 2']
        assert [u.monto_reconstruccion for u in desglose] == [
            pytest.approx(181.21629995),
            pytest.approx(413.78370005),
        ]
        assert [u.monto_asegurado_sugerido for u in desglose] == [200.0, 500.0]
        assert [round(u.prorrateo_pago, 6) for u in desglose] == [0.285714, 0.714286]
        assert total == 700.0

    def test_consulta_el_prospecto_de_la_oportunidad(self):
        uc = _uc_calcular()

        uc.ejecutar(5, _unidades())

        uc.repositorio_prospectos.buscar_prospecto_condominio.assert_called_once_with(5)

    def test_prospecto_inexistente_no_calcula(self):
        uc = _uc_calcular(prospecto=None)

        desglose, total = uc.ejecutar(5, _unidades())

        assert desglose is None
        assert total is None

    def test_prospecto_sin_datos_de_reconstruccion_no_calcula(self):
        prospecto = _prospecto()
        prospecto.metros_cuadrados = None
        uc = _uc_calcular(prospecto=prospecto)

        desglose, total = uc.ejecutar(5, _unidades())

        assert desglose is None
        assert total is None

    def test_sin_prospecto_no_consulta_el_repositorio(self):
        uc = _uc_calcular()

        desglose, total = uc.ejecutar(None, _unidades())

        assert desglose is None
        assert total is None
        uc.repositorio_prospectos.buscar_prospecto_condominio.assert_not_called()

    def test_sin_unidades_no_hay_nada_que_calcular(self):
        uc = _uc_calcular()

        desglose, total = uc.ejecutar(5, [])

        assert desglose is None
        assert total is None


@pytest.mark.unit
class TestObtenerDesgloseReconstruccionUnidades:

    def test_devuelve_total_y_unidades_calculados_al_momento(self):
        calcular = _mock_calcular()
        uc, repositorio_unidades = _use_case_obtener(calcular=calcular)

        total, total_sugerido, desglose = uc.ejecutar(42, MagicMock(rut='1'))

        assert total == 600.0
        assert total_sugerido == 600.0
        assert [u.monto_asegurado_sugerido for u in desglose] == [200.0, 400.0]
        repositorio_unidades.listar_por_oportunidad.assert_called_once_with(42)
        args = calcular.ejecutar.call_args.args
        assert args[0] == 5
        assert [u.identificador_unidad for u in args[1]] == ['Depto 1', 'Depto 2']

    def test_sin_desglose_devuelve_total_nulo(self):
        calcular = _mock_calcular(desglose=None, total=None)
        uc, _ = _use_case_obtener(calcular=calcular)

        total, total_sugerido, desglose = uc.ejecutar(42, MagicMock(rut='1'))

        assert total is None
        assert total_sugerido is None
        assert desglose == []

    def test_oportunidad_no_encontrada(self):
        uc, repositorio_unidades = _use_case_obtener(proceso=None)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(99, MagicMock(rut='1'))

        repositorio_unidades.listar_por_oportunidad.assert_not_called()

    def test_sin_permiso_es_rechazado(self):
        uc, repositorio_unidades = _use_case_obtener(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(42, MagicMock(rut='1'))

        repositorio_unidades.listar_por_oportunidad.assert_not_called()


@pytest.mark.unit
class TestGenerarExcelDesgloseReconstruccionUnidades:

    def test_genera_el_excel(self):
        uc, generador_excel = _use_case_excel()

        ruta = uc.ejecutar(42, MagicMock(rut='1'))

        assert ruta == 'documentos/estudios/desglose/desglose.xlsx'
        id_proceso, desglose, encabezado = generador_excel.generar.call_args.args
        assert id_proceso == 42
        assert [u.identificador_unidad for u in desglose] == ['Depto 1', 'Depto 2']
        assert encabezado['cantidad_unidades'] == 2
        assert encabezado['monto_asegurado_sugerido_total'] == 600.0

    def test_sin_alicuota_es_conflicto(self):
        uc, generador_excel = _use_case_excel(unidades=[])

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, MagicMock(rut='1'))

        generador_excel.generar.assert_not_called()

    def test_desglose_no_calculable_es_conflicto(self):
        calcular = _mock_calcular(desglose=None, total=None)
        uc, generador_excel = _use_case_excel(calcular=calcular)

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, MagicMock(rut='1'))

        generador_excel.generar.assert_not_called()

    def test_oportunidad_no_encontrada(self):
        uc, _ = _use_case_excel(proceso=None)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(99, MagicMock(rut='1'))

    def test_sin_permiso_es_rechazado(self):
        uc, generador_excel = _use_case_excel(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(42, MagicMock(rut='1'))

        generador_excel.generar.assert_not_called()
