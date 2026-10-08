from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado import (
    GenerarAlertasCierreEstimadoUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import AHORA_REF, crear_notificacion_mock
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock


def _use_case(procesos, evaluar_result=None, registrar_retorno=True, existe=False):
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    generar_alerta_cierre = MagicMock()
    repo_procesos.obtener_procesos_comerciales.return_value = list(procesos)
    repo_notificaciones.registrar.return_value = registrar_retorno
    repo_notificaciones.existe_alerta_proceso.return_value = existe
    generar_alerta_cierre.evaluar.return_value = evaluar_result
    uc = GenerarAlertasCierreEstimadoUseCase(
        repo_procesos, repo_notificaciones, generar_alerta_cierre
    )
    return uc, repo_procesos, repo_notificaciones, generar_alerta_cierre


def _notificacion(proceso_id=1):
    return crear_notificacion_mock(
        id=None,
        rut_usuario='11111111-1',
        codigo_tipo='FECHA_CIERRE_VENCIDA',
        entidad_id=proceso_id,
    )


@pytest.mark.unit
class TestGenerarAlertasCierreEstimado:

    def test_acepta_el_generar_alerta_por_constructor(self):
        uc, _, _, generar_alerta_cierre = _use_case([])

        assert uc.generar_alerta_cierre is generar_alerta_cierre

    def test_consulta_todos_los_procesos_abiertos(self):
        proceso = crear_proceso_comercial_mock()
        uc, repo_procesos, _, generar_alerta_cierre = _use_case([proceso])

        uc.ejecutar(ahora=AHORA_REF)

        repo_procesos.obtener_procesos_comerciales.assert_called_once_with(
            id_prospecto=None,
            abiertos=True,
        )
        generar_alerta_cierre.evaluar.assert_called_once_with(proceso, AHORA_REF)

    def test_no_crea_si_evaluar_no_corresponde(self):
        uc, _, repo_notif, _ = _use_case([crear_proceso_comercial_mock()], evaluar_result=None)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repo_notif.registrar.assert_not_called()

    def test_aplica_guarda_de_existencia_por_tipo_proceso_y_rut(self):
        proceso = crear_proceso_comercial_mock(id=42)
        notificacion = _notificacion(proceso_id=42)
        uc, _, repo_notif, _ = _use_case(
            [proceso], evaluar_result=notificacion, existe=True
        )

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repo_notif.existe_alerta_proceso.assert_called_once_with(
            'FECHA_CIERRE_VENCIDA', 42, '11111111-1'
        )
        repo_notif.registrar.assert_not_called()

    def test_registra_cuando_no_existe(self):
        notificacion = _notificacion()
        uc, _, repo_notif, _ = _use_case(
            [crear_proceso_comercial_mock()], evaluar_result=notificacion
        )

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == [notificacion]
        repo_notif.registrar.assert_called_once_with(notificacion)

    def test_registrar_false_no_se_agrega(self):
        uc, _, _, _ = _use_case(
            [crear_proceso_comercial_mock()],
            evaluar_result=_notificacion(),
            registrar_retorno=False,
        )

        assert uc.ejecutar(ahora=AHORA_REF) == []

    @patch('app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado.hub')
    def test_publica_en_hub_cuando_crea(self, mock_hub):
        uc, _, _, _ = _use_case([crear_proceso_comercial_mock()], evaluar_result=_notificacion())

        uc.ejecutar(ahora=AHORA_REF)

        mock_hub.publicar_desde_hilo.assert_called_once()

    @patch('app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado.hub')
    def test_no_publica_si_no_crea(self, mock_hub):
        uc, _, _, _ = _use_case([crear_proceso_comercial_mock()], evaluar_result=None)

        uc.ejecutar(ahora=AHORA_REF)

        mock_hub.publicar_desde_hilo.assert_not_called()
