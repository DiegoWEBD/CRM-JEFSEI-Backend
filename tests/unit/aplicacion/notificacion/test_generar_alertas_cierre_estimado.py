from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado import (
    GenerarAlertasCierreEstimadoUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.notificacion_factory import AHORA_REF, crear_notificacion_mock
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock


def _use_case(
    procesos,
    evaluar_result=None,
    registrar_retorno=True,
    existe=False,
    servicio_alertas=None,
):
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    generar_alerta_cierre = MagicMock()
    repo_procesos.obtener_procesos_comerciales.return_value = list(procesos)
    repo_notificaciones.registrar.return_value = registrar_retorno
    repo_notificaciones.existe_alerta_proceso.return_value = existe
    generar_alerta_cierre.evaluar.return_value = evaluar_result
    if servicio_alertas is None:
        servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
        servicio_alertas.marcar_leidas.return_value = []
    uc = GenerarAlertasCierreEstimadoUseCase(
        repo_procesos, repo_notificaciones, generar_alerta_cierre, servicio_alertas
    )
    return uc, repo_procesos, repo_notificaciones, generar_alerta_cierre


def _notificacion(proceso_id=1):
    return crear_notificacion_mock(
        id=None,
        rut_usuario='11111111-1',
        codigo_tipo='FECHA_CIERRE_VENCIDA',
        entidad_id=proceso_id,
    )


def _notificacion_por_vencer(proceso_id=1):
    return crear_notificacion_mock(
        id=None,
        rut_usuario='11111111-1',
        codigo_tipo='CIERRE_ESTIMADO_PROXIMO',
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


@pytest.mark.unit
class TestResolverEscalonesFechaCierre:

    def _servicio(self, marcados=None):
        servicio = MagicMock(spec=ServicioAlertasProceso)
        servicio.marcar_leidas.return_value = marcados or []
        return servicio

    def test_vencida_resuelve_el_por_vencer_del_proceso(self):
        proceso = crear_proceso_comercial_mock(id=42)
        servicio = self._servicio()
        uc, _, _, _ = _use_case(
            [proceso], evaluar_result=_notificacion(proceso_id=42), servicio_alertas=servicio
        )

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas.assert_called_once_with(
            42, ('CIERRE_ESTIMADO_PROXIMO',), AHORA_REF
        )

    def test_vencida_ya_existente_igual_resuelve_el_por_vencer(self):
        """La guarda de existencia salta la creación, pero la resolución corre:
        auto-sana los pares pendientes heredados (aviso + crítica sin leer)."""
        proceso = crear_proceso_comercial_mock(id=42)
        servicio = self._servicio()
        uc, _, repo_notif, _ = _use_case(
            [proceso],
            evaluar_result=_notificacion(proceso_id=42),
            existe=True,
            servicio_alertas=servicio,
        )

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas.assert_called_once_with(
            42, ('CIERRE_ESTIMADO_PROXIMO',), AHORA_REF
        )
        repo_notif.registrar.assert_not_called()

    def test_por_vencer_no_resuelve_nada(self):
        proceso = crear_proceso_comercial_mock(id=42)
        servicio = self._servicio()
        uc, _, _, _ = _use_case(
            [proceso],
            evaluar_result=_notificacion_por_vencer(proceso_id=42),
            servicio_alertas=servicio,
        )

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas.assert_not_called()

    def test_sin_alerta_no_resuelve_nada(self):
        proceso = crear_proceso_comercial_mock(id=42)
        servicio = self._servicio()
        uc, _, _, _ = _use_case([proceso], evaluar_result=None, servicio_alertas=servicio)

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas.assert_not_called()

    @patch('app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado.hub')
    def test_publica_los_destinatarios_de_las_alertas_resueltas(self, mock_hub):
        proceso = crear_proceso_comercial_mock(id=42)
        servicio = self._servicio(marcados=['11111111-1', '22222222-2'])
        uc, _, _, _ = _use_case(
            [proceso],
            evaluar_result=_notificacion(proceso_id=42),
            existe=True,
            servicio_alertas=servicio,
        )

        uc.ejecutar(ahora=AHORA_REF)

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1', '22222222-2'],
            {
                'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
                'motivo': 'alertas_fecha_cierre_actualizadas',
            },
        )

    @patch('app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado.hub')
    def test_sin_resueltas_no_publica(self, mock_hub):
        proceso = crear_proceso_comercial_mock(id=42)
        servicio = self._servicio()
        uc, _, _, _ = _use_case(
            [proceso],
            evaluar_result=_notificacion(proceso_id=42),
            existe=True,
            servicio_alertas=servicio,
        )

        uc.ejecutar(ahora=AHORA_REF)

        mock_hub.publicar_desde_hilo.assert_not_called()
