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
    repo_notificaciones.existe_alerta_proceso.return_value = False
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

    def test_dedupe_key_incluye_tipo_id_rut_y_timestamp(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].dedupe_key == (
            f'CIERRE_ESTIMADO_PROXIMO:{proceso.id}:11111111-1:{AHORA_REF.isoformat()}'
        )

    def test_consulta_solo_abiertos_por_prospecto(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, repo_procesos, _ = _use_case([proceso])

        uc.ejecutar(ahora=AHORA_REF, id_prospecto=7)

        repo_procesos.obtener_procesos_comerciales.assert_called_once_with(
            id_prospecto=7,
            abiertos=True,
        )

    def test_id_prospecto_correcto(self):
        proceso = crear_proceso_comercial_mock(
            id=42,
            id_prospecto=7,
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas[0].id_prospecto == 7
        assert creadas[0].entidad_id == 42

    def test_no_duplica_si_dedupe_key_existe(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso], registrar_retorno=False)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []

    def test_no_registra_si_ya_existe_alerta_para_el_proceso(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, repo_notif = _use_case([proceso])
        repo_notif.existe_alerta_proceso.return_value = True

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repo_notif.registrar.assert_not_called()
        repo_notif.existe_alerta_proceso.assert_called_once_with(
            'CIERRE_ESTIMADO_PROXIMO', 1, '11111111-1'
        )

    def test_registra_si_no_existe_alerta(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, repo_notif = _use_case([proceso])
        repo_notif.existe_alerta_proceso.return_value = False

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        repo_notif.registrar.assert_called_once()

    def test_crea_aunque_exista_previa_si_no_verifica_existencia(self):
        """Tras reasignar, la re-evaluación no debe bloquearse por la alerta
        previa (leída) del mismo proceso/tipo/usuario: se crea una nueva."""
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF - timedelta(days=2),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, repo_notif = _use_case([proceso])
        repo_notif.existe_alerta_proceso.return_value = True

        creadas = uc.ejecutar(ahora=AHORA_REF, verificar_existencia=False)

        assert len(creadas) == 1
        repo_notif.existe_alerta_proceso.assert_not_called()
        repo_notif.registrar.assert_called_once()

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

    def test_mensaje_incluye_producto_y_cliente(self):
        proceso = crear_proceso_comercial_mock(
            nombre_cliente='Comunidad Edificio Exequiel Torre C',
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "La oportunidad 'Seguro de Vida'" in creadas[0].mensaje
        assert 'Comunidad Edificio Exequiel Torre C' in creadas[0].mensaje
        assert 'tiene fecha de cierre estimada' in creadas[0].mensaje

    def test_mensaje_critico_incluye_producto_y_cliente(self):
        proceso = crear_proceso_comercial_mock(
            nombre_cliente='Comunidad Edificio Exequiel Torre C',
            fecha_estimada_cierre=AHORA_REF - timedelta(days=8),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "La oportunidad 'Seguro de Vida'" in creadas[0].mensaje
        assert '8 días de atraso' in creadas[0].mensaje

    def test_notificaciones_cierre_no_son_leibles(self):
        proceso = crear_proceso_comercial_mock(
            fecha_estimada_cierre=AHORA_REF + timedelta(days=3),
            ejecutivo_comercial=_Ejecutivo('11111111-1'),
        )
        uc, _, _ = _use_case([proceso])

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].leible is False
