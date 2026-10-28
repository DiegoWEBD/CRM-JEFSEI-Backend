from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import (
    AHORA_REF,
    crear_poliza_alertable_renovacion_mock,
)

FIN_VIGENCIA = AHORA_REF + timedelta(days=10)

ZONA_NEGOCIO = ZoneInfo('America/Santiago')


def _use_case(repo=None):
    return GenerarAlertaRenovacionPolizaUseCase(
        repo or MagicMock(spec=RepositorioNotificaciones)
    )


def _poliza(**kwargs):
    defaults = {'fin_vigencia': FIN_VIGENCIA}
    defaults.update(kwargs)
    return crear_poliza_alertable_renovacion_mock(**defaults)


@pytest.mark.unit
class TestEvaluarAlertasRenovacion:

    def test_lejos_del_fin_de_vigencia_no_genera(self):
        uc = _use_case()

        alertas = uc.evaluar(
            _poliza(fin_vigencia=AHORA_REF + timedelta(days=100)), AHORA_REF
        )

        assert alertas == []

    def test_con_proceso_renovacion_no_genera(self):
        uc = _use_case()

        alertas = uc.evaluar(
            _poliza(tiene_proceso_renovacion=True), FIN_VIGENCIA + timedelta(days=30)
        )

        assert alertas == []

    def test_sin_destinatarios_asignados_no_genera(self):
        """Sin ejecutivo ni asistente de renovación no hay destinatario: la
        salvaguarda es asignar un responsable (no hay fan-out por rol)."""
        uc = _use_case()

        alertas = uc.evaluar(
            _poliza(rut_ej_renovacion=None, rut_as_renovacion=None), AHORA_REF
        )

        assert alertas == []

    def test_a_2_meses_genera_solo_la_cotizacion(self):
        uc = _use_case()
        ahora = FIN_VIGENCIA - timedelta(days=60)

        alertas = uc.evaluar(_poliza(), ahora)

        assert len(alertas) == 1
        assert alertas[0].codigo_tipo == 'RENOVACION_COTIZACION_PENDIENTE'
        assert alertas[0].nivel == 'AVISO'
        assert alertas[0].titulo == 'Iniciar cotización de renovación'
        assert alertas[0].numero_poliza == 'POL-001'

    def test_a_20_dias_genera_cotizacion_y_gestion(self):
        uc = _use_case()
        ahora = FIN_VIGENCIA - timedelta(days=20)

        alertas = uc.evaluar(_poliza(), ahora)

        tipos = [alerta.codigo_tipo for alerta in alertas]
        assert sorted(tipos) == [
            'RENOVACION_COTIZACION_PENDIENTE',
            'RENOVACION_GESTION_PENDIENTE',
        ]

    def test_vencida_agrega_la_critica(self):
        uc = _use_case()

        alertas = uc.evaluar(_poliza(), FIN_VIGENCIA)

        tipos = sorted(alerta.codigo_tipo for alerta in alertas)
        assert tipos == [
            'RENOVACION_COTIZACION_PENDIENTE',
            'RENOVACION_GESTION_PENDIENTE',
            'RENOVACION_POLIZA_VENCIDA',
        ]

    def test_critica_es_de_nivel_critico_y_menciona_vencimiento(self):
        uc = _use_case()

        alertas = uc.evaluar(_poliza(), FIN_VIGENCIA + timedelta(days=3))

        critica = [a for a in alertas if a.codigo_tipo == 'RENOVACION_POLIZA_VENCIDA'][0]
        assert critica.nivel == 'CRITICO'
        assert critica.titulo == 'Póliza vencida sin renovación'
        assert 'venció' in critica.mensaje
        assert 'no tiene un proceso de renovación iniciado' in critica.mensaje

    def test_mensajes_de_los_avisos_mencionan_poliza_y_fecha(self):
        uc = _use_case()

        alertas = uc.evaluar(_poliza(), FIN_VIGENCIA - timedelta(days=10))

        for alerta in alertas:
            assert 'POL-001' in alerta.mensaje
            assert FIN_VIGENCIA.strftime('%d-%m-%Y') in alerta.mensaje

    def test_genera_una_alerta_por_destinatario_asignado(self):
        uc = _use_case()

        alertas = uc.evaluar(
            _poliza(rut_ej_renovacion='11111111-1', rut_as_renovacion='22222222-2'),
            FIN_VIGENCIA - timedelta(days=20),
        )

        ruts = {alerta.rut_usuario for alerta in alertas}
        assert ruts == {'11111111-1', '22222222-2'}
        # 2 hitos x 2 destinatarios
        assert len(alertas) == 4

    def test_sin_asignados_no_genera_ni_aunque_haya_ejecutivos_de_renovacion(self):
        """Ya no hay fan-out por rol: sin asignados no se genera ninguna alerta."""
        uc = _use_case()

        alertas = uc.evaluar(
            _poliza(rut_ej_renovacion=None, rut_as_renovacion=None),
            FIN_VIGENCIA - timedelta(days=20),
        )

        assert alertas == []

    def test_mismo_rut_como_ejecutivo_y_asistente_no_se_duplica(self):
        uc = _use_case()

        alertas = uc.evaluar(
            _poliza(rut_ej_renovacion='11111111-1', rut_as_renovacion='11111111-1'),
            FIN_VIGENCIA - timedelta(days=20),
        )

        # 2 hitos x 1 destinatario (el set de destinatarios no duplica el RUT)
        assert len(alertas) == 2
        assert {alerta.rut_usuario for alerta in alertas} == {'11111111-1'}

    def test_dedupe_key_por_destinatario_y_vigencia(self):
        uc = _use_case()
        ahora = FIN_VIGENCIA - timedelta(days=10)

        alertas = uc.evaluar(_poliza(), ahora)

        for alerta in alertas:
            assert alerta.dedupe_key.endswith(f':{FIN_VIGENCIA.isoformat()}:11111111-1')
            assert alerta.leible is False
            assert alerta.leida is False


@pytest.mark.unit
class TestEjecutarAlertasRenovacion:
    """ejecutar: trae la póliza por número, evalúa y registra (espejo del
    generar_alerta_cierre.ejecutar usado por _refrescar_alertas_de_cierre)."""

    def test_trae_la_poliza_evalua_y_registra(self):
        repo = MagicMock(spec=RepositorioNotificaciones)
        repo.registrar.return_value = True
        uc = _use_case(repo)
        # A 45 días del fin de vigencia aplica solo el hito de cotización.
        poliza = _poliza(
            fin_vigencia=AHORA_REF + timedelta(days=45), rut_ej_renovacion='11111111-1'
        )
        repo.obtener_poliza_alertable_renovacion.return_value = poliza

        creadas = uc.ejecutar('POL-001', AHORA_REF)

        repo.obtener_poliza_alertable_renovacion.assert_called_once_with('POL-001')
        assert len(creadas) == 1
        repo.registrar.assert_called_once_with(creadas[0])
        assert creadas[0].rut_usuario == '11111111-1'

    def test_sin_poliza_alertable_no_genera(self):
        repo = MagicMock(spec=RepositorioNotificaciones)
        uc = _use_case(repo)
        repo.obtener_poliza_alertable_renovacion.return_value = None

        assert uc.ejecutar('POL-404', AHORA_REF) == []
        repo.registrar.assert_not_called()

    def test_solo_devuelve_las_efectivamente_creadas(self):
        repo = MagicMock(spec=RepositorioNotificaciones)
        repo.registrar.return_value = False
        uc = _use_case(repo)
        repo.obtener_poliza_alertable_renovacion.return_value = _poliza()

        assert uc.ejecutar('POL-001', AHORA_REF) == []

    def test_sin_ahora_usa_el_momento_actual(self):
        repo = MagicMock(spec=RepositorioNotificaciones)
        repo.registrar.return_value = True
        uc = _use_case(repo)
        # Vigencia futura relativa al momento real: solo aplica el hito de
        # cotización, con created_at del momento actual (sin `ahora` explícito).
        repo.obtener_poliza_alertable_renovacion.return_value = _poliza(
            fin_vigencia=datetime.now(tz=timezone.utc) + timedelta(days=45)
        )

        creadas = uc.ejecutar('POL-001')

        assert len(creadas) == 1
        assert isinstance(creadas[0].created_at, datetime)


@pytest.mark.unit
class TestDiasDeCalendarioEnZonaDeNegocio:

    def test_mensaje_muestra_el_dia_de_santiago_no_el_dia_utc(self):
        """Regresión: el instante 2026-08-30 00:00+00 es el 29-08 en Santiago.

        El mensaje formateaba el día UTC (30-08) mientras la UI mostraba el
        día de Santiago (29-08)."""
        uc = _use_case()
        fin_vigencia = datetime(2026, 8, 30, 0, 0, tzinfo=timezone.utc)
        ahora = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)

        alertas = uc.evaluar(_poliza(fin_vigencia=fin_vigencia), ahora)

        assert alertas
        for alerta in alertas:
            assert '29-08-2026' in alerta.mensaje
            assert '30-08-2026' not in alerta.mensaje

    def test_hitos_por_calendario_de_santiago_a_traves_del_cambio_de_horario(self):
        """El hito de cotización se calcula por día calendario de Santiago.

        El fin de vigencia está en horario de verano (-03) y el hito a 2 meses
        cae en horario de invierno (-04): restar instantes adelantaba el hito
        una hora (al día calendario anterior)."""
        uc = _use_case()
        fin_vigencia = datetime(2026, 11, 5, 0, 0, tzinfo=ZONA_NEGOCIO)
        # 04-09 23:30 en Santiago: todavía NO son los 2 meses de calendario.
        antes_del_hito = datetime(2026, 9, 5, 3, 30, tzinfo=timezone.utc)
        # 05-09 00:30 en Santiago: sí se cumple el hito.
        tras_el_hito = datetime(2026, 9, 5, 4, 30, tzinfo=timezone.utc)

        assert uc.evaluar(_poliza(fin_vigencia=fin_vigencia), antes_del_hito) == []
        assert len(uc.evaluar(_poliza(fin_vigencia=fin_vigencia), tras_el_hito)) == 1
