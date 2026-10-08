from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from app.aplicacion.notificacion.use_cases.generar_alerta_cierre_estimado import (
    GenerarAlertaCierreEstimadoUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import AHORA_REF
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock


def _use_case(registrar_retorno: bool = True):
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    repo_notificaciones.registrar.return_value = registrar_retorno
    return (
        GenerarAlertaCierreEstimadoUseCase(repo_procesos, repo_notificaciones),
        repo_procesos,
        repo_notificaciones,
    )


class _Ejecutivo:
    def __init__(self, rut: str):
        self.rut = rut


def _proceso(**kwargs):
    defaults = {
        'fecha_estimada_cierre': AHORA_REF + timedelta(days=3),
        'ejecutivo_comercial': _Ejecutivo('11111111-1'),
    }
    defaults.update(kwargs)
    return crear_proceso_comercial_mock(**defaults)


@pytest.mark.unit
class TestEvaluarAlertaCierreEstimado:

    def test_sin_fecha_estimada_no_genera(self):
        uc, _, _ = _use_case()

        assert uc.evaluar(_proceso(fecha_estimada_cierre=None), AHORA_REF) is None

    def test_sin_ejecutivo_comercial_no_genera(self):
        uc, _, _ = _use_case()

        assert uc.evaluar(_proceso(ejecutivo_comercial=None), AHORA_REF) is None

    def test_mas_de_5_dias_no_genera(self):
        uc, _, _ = _use_case()

        assert uc.evaluar(_proceso(fecha_estimada_cierre=AHORA_REF + timedelta(days=6)), AHORA_REF) is None

    def test_cierre_siguiente_dia_a_hora_no_medianoche_cuenta_un_dia(self):
        """Regresión: restar instantes daba 'faltan 0 días' tras la medianoche."""
        uc, _, _ = _use_case()
        cierre = datetime(2026, 10, 9, 0, 0, tzinfo=ZoneInfo('America/Santiago'))
        ahora = datetime(2026, 10, 8, 19, 45, tzinfo=ZoneInfo('America/Santiago'))

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=cierre), ahora)

        assert notificacion is not None
        assert notificacion.codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert 'el 09/10/2026' in notificacion.mensaje
        assert '(faltan 1 días)' in notificacion.mensaje

    def test_cierre_siguiente_dia_utc_tambien_cuenta_un_dia(self):
        """La comparación usa la zona de negocio, no la del servidor."""
        uc, _, _ = _use_case()
        # 09/10 00:00 en Santiago = 09/10 03:00 UTC
        cierre = datetime(2026, 10, 9, 3, 0, tzinfo=timezone.utc)
        # 08/10 22:45 UTC = 08/10 19:45 en Santiago
        ahora = datetime(2026, 10, 8, 22, 45, tzinfo=timezone.utc)

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=cierre), ahora)

        assert notificacion is not None
        assert '(faltan 1 días)' in notificacion.mensaje

    def test_mismo_dia_a_hora_no_medianoche_cuenta_cero_dias(self):
        uc, _, _ = _use_case()
        cierre = datetime(2026, 10, 9, 0, 0, tzinfo=ZoneInfo('America/Santiago'))
        ahora = datetime(2026, 10, 9, 19, 45, tzinfo=ZoneInfo('America/Santiago'))

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=cierre), ahora)

        assert notificacion is not None
        assert notificacion.codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert '(faltan 0 días)' in notificacion.mensaje

    def test_dia_anterior_a_hora_no_medianoche_cuenta_dia_de_atraso(self):
        uc, _, _ = _use_case()
        cierre = datetime(2026, 10, 8, 0, 0, tzinfo=ZoneInfo('America/Santiago'))
        ahora = datetime(2026, 10, 9, 8, 0, tzinfo=ZoneInfo('America/Santiago'))

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=cierre), ahora)

        assert notificacion is not None
        assert notificacion.codigo_tipo == 'FECHA_CIERRE_VENCIDA'
        assert notificacion.nivel == 'CRITICO'
        assert '(1 días de atraso)' in notificacion.mensaje

    def test_exactamente_5_dias_genera_proximo(self):
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=AHORA_REF + timedelta(days=5)), AHORA_REF)

        assert notificacion is not None
        assert notificacion.codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert notificacion.nivel == 'AVISO'
        assert notificacion.rut_usuario == '11111111-1'

    def test_fecha_hoy_genera_proximo(self):
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=AHORA_REF), AHORA_REF)

        assert notificacion is not None
        assert notificacion.codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert notificacion.nivel == 'AVISO'

    def test_fecha_vencida_genera_critico(self):
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=AHORA_REF - timedelta(days=3)), AHORA_REF)

        assert notificacion is not None
        assert notificacion.codigo_tipo == 'FECHA_CIERRE_VENCIDA'
        assert notificacion.nivel == 'CRITICO'

    def test_proceso_cerrado_no_genera(self):
        uc, _, _ = _use_case()

        assert uc.evaluar(_proceso(cerrado=True), AHORA_REF) is None

    def test_dedupe_key_incluye_tipo_id_rut_y_timestamp(self):
        proceso = _proceso()
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(proceso, AHORA_REF)

        assert notificacion is not None
        assert notificacion.dedupe_key == (
            f'CIERRE_ESTIMADO_PROXIMO:{proceso.id}:11111111-1:{AHORA_REF.isoformat()}'
        )

    def test_ids_correctos(self):
        proceso = _proceso(id=42, id_prospecto=7)
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(proceso, AHORA_REF)

        assert notificacion is not None
        assert notificacion.entidad_id == 42
        assert notificacion.id_prospecto == 7

    def test_mensaje_incluye_producto_y_cliente(self):
        proceso = _proceso(nombre_cliente='Comunidad Edificio Exequiel Torre C')
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(proceso, AHORA_REF)

        assert notificacion is not None
        assert "La oportunidad 'Seguro de Vida'" in notificacion.mensaje
        assert 'Comunidad Edificio Exequiel Torre C' in notificacion.mensaje
        assert 'tiene fecha de cierre estimada' in notificacion.mensaje

    def test_mensaje_critico_incluye_atraso(self):
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(_proceso(fecha_estimada_cierre=AHORA_REF - timedelta(days=8)), AHORA_REF)

        assert notificacion is not None
        assert '8 días de atraso' in notificacion.mensaje

    def test_notificacion_no_es_leible(self):
        uc, _, _ = _use_case()

        notificacion = uc.evaluar(_proceso(), AHORA_REF)

        assert notificacion is not None
        assert notificacion.leible is False


@pytest.mark.unit
class TestEjecutarGenerarAlertaCierreEstimado:

    def test_proceso_inexistente_no_genera(self):
        uc, repo_procesos, repo_notif = _use_case()
        repo_procesos.buscar.return_value = None

        assert uc.ejecutar(id_proceso_comercial=99) is None
        repo_notif.registrar.assert_not_called()

    def test_evalua_y_registra_el_proceso(self):
        proceso = _proceso(id=42)
        uc, repo_procesos, repo_notif = _use_case()
        repo_procesos.buscar.return_value = proceso

        notificacion = uc.ejecutar(id_proceso_comercial=42, ahora=AHORA_REF)

        repo_procesos.buscar.assert_called_once_with(42)
        repo_notif.registrar.assert_called_once()
        assert notificacion is not None
        assert notificacion.entidad_id == 42

    def test_registrar_false_devuelve_none(self):
        uc, repo_procesos, _ = _use_case(registrar_retorno=False)
        repo_procesos.buscar.return_value = _proceso()

        assert uc.ejecutar(id_proceso_comercial=1, ahora=AHORA_REF) is None

    def test_no_publica_en_hub(self):
        uc, repo_procesos, _ = _use_case()
        repo_procesos.buscar.return_value = _proceso()

        with patch('app.core.hub_notificaciones.hub') as mock_hub:
            uc.ejecutar(id_proceso_comercial=1, ahora=AHORA_REF)

        mock_hub.publicar_desde_hilo.assert_not_called()
