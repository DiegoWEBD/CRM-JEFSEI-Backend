from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado import (
    GenerarAlertasCierreEstimadoUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import AHORA_REF
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock


def _use_case(procesos, registrar_retorno: bool = True):
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    repo_procesos.obtener_procesos_comerciales.return_value = list(procesos)
    repo_notificaciones.registrar.return_value = registrar_retorno
    return GenerarAlertasCierreEstimadoUseCase(repo_procesos, repo_notificaciones), repo_procesos, repo_notificaciones


class _Ejecutivo:
    def __init__(self, rut: str):
        self.rut = rut


@pytest.mark.unit
class TestGenerarAlertasCierreEstimado:

    def test_sin_fecha_estimada_no_genera(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=None,
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, repo_notif = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repo_notif.registrar.assert_not_called()

    def test_sin_ejecutivo_comercial_no_genera(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=None,
        )
        uc, _, repo_notif = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repo_notif.registrar.assert_not_called()

    def test_mas_de_5_dias_no_genera(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=6),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []

    def test_exactamente_5_dias_genera_proximo(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=5),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert creadas[0].nivel == 'AVISO'
        assert creadas[0].rut_usuario == '11111111-1'

    def test_1_dia_genera_proximo(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=1),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'

    def test_fecha_hoy_genera_proximo(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF,
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert creadas[0].nivel == 'AVISO'

    def test_fecha_vencida_genera_critico(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF - timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == 'FECHA_CIERRE_VENCIDA'
        assert creadas[0].nivel == 'CRITICO'

    def test_proceso_cerrado_no_genera(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
            cerrado=True,
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []

    def test_dedupe_key_incluye_estado(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert 'CIERRE_ESTIMADO_PROXIMO' in creadas[0].dedupe_key
        assert str(proceso.id) in creadas[0].dedupe_key

    def test_url_destino_correcta(self):
        proceso = crear_proceso_comercial_mock(
            id=42,
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas[0].url_destino == '/oportunidades?id=42'
        assert creadas[0].entidad_id == 42

    def test_no_duplica_si_dedupe_key_existe(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso], registrar_retorno=False)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []

    @patch('app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado.hub')
    def test_publica_en_hub_cuando_crea(self, mock_hub):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        uc.ejecutar(ahora=AHORA_REF)

        mock_hub.publicar_desde_hilo.assert_called_once()

    def test_consulta_solo_abiertos(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, repo_procesos, _ = _use_case([proceso])

        uc.ejecutar(ahora=AHORA_REF)

        repo_procesos.obtener_procesos_comerciales.assert_called_once_with(
            id_prospecto=None,
            abiertos=True,
        )
