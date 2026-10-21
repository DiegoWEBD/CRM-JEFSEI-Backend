from unittest.mock import MagicMock

import pytest

from app.aplicacion.evaluacion_proyectos.use_cases.generar_desglose_unidades import GenerarDesgloseUnidadesUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import CalculadoraDesgloseReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


def _solicitud(id=10, tipo='unidades', monto_asegurado=41500.0):
    solicitud = MagicMock()
    solicitud.id = id
    solicitud.tipo = tipo
    solicitud.monto_asegurado = monto_asegurado
    return solicitud


def _cotizacion(id=7):
    cotizacion = MagicMock()
    cotizacion.id = id
    cotizacion.monto_total_asegurado = 41500.0
    cotizacion.tasa_afecta = 0.6
    cotizacion.tasa_excenta = 1.92
    cotizacion.tasa_politica = 0.0
    cotizacion.asistencia_afecta = 0.0
    cotizacion.asistencia_excenta = 0.0
    return cotizacion


def _unidades():
    return [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.030456521, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
    ]


def _desglose_reconstruccion():
    # Depto 1: 144,97 → sugerido 200 (prorrateo_pago 1/3)
    # Depto 2: 331,03 → sugerido 400 (prorrateo_pago 2/3)
    return CalculadoraDesgloseReconstruccion.calcular(4760.0, _unidades())


AUSENTE = object()


def _use_case(
    solicitud=AUSENTE,
    unidades=None,
    cotizacion=AUSENTE,
    proceso=AUSENTE,
    pertenece=True,
    desglose=AUSENTE,
    total_sugerido=600.0,
):
    authorization_service = MagicMock()
    authorization_service.usuario_puede_ver_solicitud_cotizacion.return_value = True

    repositorio_solicitudes = MagicMock()
    repositorio_solicitudes.buscar.return_value = _solicitud() if solicitud is AUSENTE else solicitud

    repositorio_unidades = MagicMock()
    repositorio_unidades.listar_por_oportunidad.return_value = unidades if unidades is not None else _unidades()

    repositorio_cotizaciones = MagicMock()
    repositorio_cotizaciones.obtener_por_id.return_value = _cotizacion() if cotizacion is AUSENTE else cotizacion
    repositorio_cotizaciones.cotizacion_pertenece_a_solicitud.return_value = pertenece

    repositorio_procesos_comerciales = MagicMock()
    proceso_oportunidad = MagicMock(id=42, id_prospecto=5)
    repositorio_procesos_comerciales.buscar_por_solicitud_cotizacion.return_value = (
        proceso_oportunidad if proceso is AUSENTE else proceso
    )

    calcular_desglose_reconstruccion = MagicMock()
    calcular_desglose_reconstruccion.ejecutar.return_value = (
        (_desglose_reconstruccion() if desglose is AUSENTE else desglose),
        total_sugerido,
    )

    generador_excel = MagicMock()
    generador_excel.generar.return_value = 'documentos/estudios/desglose/desglose.xlsx'

    use_case = GenerarDesgloseUnidadesUseCase(
        authorization_service=authorization_service,
        repositorio_solicitudes=repositorio_solicitudes,
        repositorio_unidades=repositorio_unidades,
        repositorio_cotizaciones=repositorio_cotizaciones,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        calcular_desglose_reconstruccion=calcular_desglose_reconstruccion,
        generador_excel=generador_excel,
    )

    return use_case, generador_excel


@pytest.mark.unit
class TestGenerarDesgloseUnidadesValidaciones:

    def test_sin_cotizaciones_es_conflicto(self):
        use_case, _ = _use_case()

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[], rut_usuario='1-1')

    def test_solicitud_no_encontrada(self):
        use_case, _ = _use_case(solicitud=None)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id_solicitud=99, ids_cotizacion=[7], rut_usuario='1-1')

    def test_usuario_no_autorizado(self):
        use_case, _ = _use_case()
        use_case.authorization_service.usuario_puede_ver_solicitud_cotizacion.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_solicitud_que_no_es_de_unidades_es_conflicto(self):
        use_case, _ = _use_case(solicitud=_solicitud(tipo='espacios_comunes'))

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_solicitud_sin_monto_asegurado_es_conflicto(self):
        use_case, _ = _use_case(solicitud=_solicitud(monto_asegurado=None))

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_solicitud_sin_unidades_es_conflicto(self):
        use_case, _ = _use_case(unidades=[])

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_desglose_no_calculable_es_conflicto(self):
        use_case, _ = _use_case(desglose=None, total_sugerido=None)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_total_sugerido_cero_es_conflicto(self):
        use_case, _ = _use_case(total_sugerido=0.0)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_solicitud_sin_oportunidad_es_recurso_no_encontrado(self):
        use_case, _ = _use_case(proceso=None)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_cotizacion_no_encontrada(self):
        use_case, _ = _use_case(cotizacion=None)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_cotizacion_de_otra_solicitud_es_conflicto(self):
        use_case, _ = _use_case(pertenece=False)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_sin_rut_no_se_valida_autorizacion(self):
        use_case, _ = _use_case()

        use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario=None)

        use_case.authorization_service.usuario_puede_ver_solicitud_cotizacion.assert_not_called()


@pytest.mark.unit
class TestGenerarDesgloseUnidadesExcel:

    def test_calcula_las_primas_una_unica_vez_y_las_reparte_por_prorrateo_de_pago(self):
        use_case, generador_excel = _use_case()

        ruta = use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

        assert ruta == 'documentos/estudios/desglose/desglose.xlsx'

        id_solicitud, datos = generador_excel.generar.call_args.args
        assert id_solicitud == 10
        assert len(datos) == 1

        cotizacion, totales_referencia, desglose = datos[0]
        assert cotizacion.id == 7

        # Fila de referencia: totales registrados de la cotización (41.500 UF)
        assert totales_referencia.monto_asegurado == 41500.0
        assert totales_referencia.prima_neta == 104.58
        assert totales_referencia.prima_iva == 4.73
        assert totales_referencia.prima_bruta == 109.31

        # El cálculo único sobre el total sugerido (600 UF) da:
        # afecta 0,36 | excenta 1,15 | neta 1,51 | IVA 0,07 | bruta 1,58
        # y se reparte por el prorrateo de pago de cada unidad
        assert [u.identificador_unidad for u in desglose] == ['Depto 1', 'Depto 2']

        assert desglose[0].prorrateo_pago == pytest.approx(1 / 3)
        assert desglose[0].monto_asegurado == 200.0
        assert desglose[0].monto_reconstruccion == 144.97
        assert desglose[0].monto_asegurado_sugerido == 200.0
        assert desglose[0].prima_afecta == 0.12
        assert desglose[0].prima_excenta == 0.38
        assert desglose[0].prima_neta == 0.5
        assert desglose[0].prima_iva == 0.02
        assert desglose[0].prima_bruta == 0.53

        assert desglose[1].prorrateo_pago == pytest.approx(2 / 3)
        assert desglose[1].monto_asegurado == 400.0
        assert desglose[1].prima_afecta == 0.24
        assert desglose[1].prima_excenta == 0.77
        assert desglose[1].prima_neta == 1.01
        assert desglose[1].prima_iva == 0.05
        assert desglose[1].prima_bruta == 1.05

    def test_las_asistencias_se_incluyen_en_el_calculo_unico(self):
        cotizacion = _cotizacion()
        cotizacion.asistencia_afecta = 5.0
        cotizacion.asistencia_excenta = 3.0
        use_case, generador_excel = _use_case(cotizacion=cotizacion)

        use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

        _, datos = generador_excel.generar.call_args.args
        desglose = datos[0][2]

        # Prima afecta total = 0,36 + 5 = 5,36 y excenta = 1,15 + 3 = 4,15
        assert desglose[0].prima_afecta == 1.79
        assert desglose[0].prima_excenta == 1.38
        assert desglose[1].prima_afecta == 3.57
        assert desglose[1].prima_excenta == 2.77

    def test_las_unidades_se_ordenan_por_fila_de_origen(self):
        unidades = [
            UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.5, fila_origen=3),
            UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.5, fila_origen=2),
        ]
        # El caso de uso pasa las unidades ordenadas al cálculo del desglose
        desglose = CalculadoraDesgloseReconstruccion.calcular(
            4760.0, sorted(unidades, key=lambda u: u.fila_origen)
        )
        use_case, generador_excel = _use_case(unidades=unidades, desglose=desglose)

        use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

        desglose_resultado = generador_excel.generar.call_args.args[1][0][2]

        assert [u.identificador_unidad for u in desglose_resultado] == ['Depto 1', 'Depto 2']
