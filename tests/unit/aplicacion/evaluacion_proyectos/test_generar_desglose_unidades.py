from unittest.mock import MagicMock

import pytest

from app.aplicacion.evaluacion_proyectos.use_cases.generar_desglose_unidades import GenerarDesgloseUnidadesUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
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


AUSENTE = object()


def _use_case(
    solicitud=AUSENTE,
    unidades=None,
    cotizacion=AUSENTE,
    prospecto=AUSENTE,
    id_prospecto=5,
    proceso=AUSENTE,
    pertenece=True,
):
    authorization_service = MagicMock()
    authorization_service.usuario_puede_ver_solicitud_cotizacion.return_value = True

    repositorio_solicitudes = MagicMock()
    repositorio_solicitudes.buscar.return_value = _solicitud() if solicitud is AUSENTE else solicitud
    repositorio_solicitudes.buscar_id_prospecto_de_solicitud.return_value = id_prospecto

    repositorio_unidades = MagicMock()
    repositorio_unidades.listar_por_oportunidad.return_value = unidades if unidades is not None else _unidades()

    repositorio_cotizaciones = MagicMock()
    repositorio_cotizaciones.obtener_por_id.return_value = _cotizacion() if cotizacion is AUSENTE else cotizacion
    repositorio_cotizaciones.cotizacion_pertenece_a_solicitud.return_value = pertenece

    repositorio_prospectos = MagicMock()
    repositorio_prospectos.buscar_prospecto_condominio.return_value = (
        _prospecto() if prospecto is AUSENTE else prospecto
    )

    repositorio_procesos_comerciales = MagicMock()
    proceso_oportunidad = MagicMock(id=42)
    repositorio_procesos_comerciales.buscar_por_solicitud_cotizacion.return_value = (
        proceso_oportunidad if proceso is AUSENTE else proceso
    )

    generador_excel = MagicMock()
    generador_excel.generar.return_value = 'documentos/estudios/desglose/desglose.xlsx'

    use_case = GenerarDesgloseUnidadesUseCase(
        authorization_service=authorization_service,
        repositorio_solicitudes=repositorio_solicitudes,
        repositorio_unidades=repositorio_unidades,
        repositorio_cotizaciones=repositorio_cotizaciones,
        repositorio_prospectos=repositorio_prospectos,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
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

    def test_solicitud_sin_prospecto_es_recurso_no_encontrado(self):
        use_case, _ = _use_case(id_prospecto=None)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_prospecto_sin_datos_de_condominio_es_conflicto(self):
        use_case, _ = _use_case(prospecto=None)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_prospecto_sin_datos_de_reconstruccion_es_conflicto(self):
        prospecto = _prospecto()
        prospecto.metros_cuadrados = None
        use_case, _ = _use_case(prospecto=prospecto)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

    def test_sin_rut_no_se_valida_autorizacion(self):
        use_case, _ = _use_case()

        use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario=None)

        use_case.authorization_service.usuario_puede_ver_solicitud_cotizacion.assert_not_called()


@pytest.mark.unit
class TestGenerarDesgloseUnidadesExcel:

    def test_genera_el_excel_con_las_dos_variantes_de_monto(self):
        use_case, generador_excel = _use_case()

        ruta = use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

        assert ruta == 'documentos/estudios/desglose/desglose.xlsx'

        id_solicitud, datos_actual, datos_sugerido = generador_excel.generar.call_args.args
        assert id_solicitud == 10

        assert len(datos_actual) == 1
        assert len(datos_sugerido) == 1

        # Hoja «Actual»: el monto asegurado de la solicitud
        cotizacion, totales_actual, desglose_actual = datos_actual[0]
        assert cotizacion.id == 7
        assert totales_actual.monto_asegurado == 41500.0
        assert totales_actual.prima_neta == 104.58
        assert totales_actual.prima_iva == 4.73
        assert totales_actual.prima_bruta == 109.31
        assert [u.identificador_unidad for u in desglose_actual] == ['Depto 1', 'Depto 2']

        # Hoja «Sugerido»: 50 % del valor de reconstrucción depreciado
        # 10 UF/m² × 1000 m² × 1.19 = 11.900 → depreciado 20 % = 9.520 → unidades = 4.760
        _, totales_sugerido, desglose_sugerido = datos_sugerido[0]
        assert totales_sugerido.monto_asegurado == 4760.0
        assert totales_sugerido.prima_afecta == 2.86
        assert totales_sugerido.prima_excenta == 9.14
        assert totales_sugerido.prima_neta == 12.0
        assert totales_sugerido.prima_iva == 0.54
        assert totales_sugerido.prima_bruta == 12.54
        assert [u.identificador_unidad for u in desglose_sugerido] == ['Depto 1', 'Depto 2']

    def test_las_unidades_se_ordenan_por_fila_de_origen(self):
        unidades = [
            UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.5, fila_origen=3),
            UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.5, fila_origen=2),
        ]
        use_case, generador_excel = _use_case(unidades=unidades)

        use_case.ejecutar(id_solicitud=10, ids_cotizacion=[7], rut_usuario='1-1')

        desglose_actual = generador_excel.generar.call_args.args[1][0][2]
        desglose_sugerido = generador_excel.generar.call_args.args[2][0][2]

        assert [u.identificador_unidad for u in desglose_actual] == ['Depto 1', 'Depto 2']
        assert [u.identificador_unidad for u in desglose_sugerido] == ['Depto 1', 'Depto 2']
