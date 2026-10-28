from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.aplicacion.notificacion.use_cases.generar_alertas_renovacion import (
    GenerarAlertasRenovacionUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import (
    AHORA_REF,
    crear_notificacion_mock,
    crear_poliza_alertable_renovacion_mock,
)

MODULO = 'app.aplicacion.notificacion.use_cases.generar_alertas_renovacion'


def _use_case(polizas):
    repo = MagicMock(spec=RepositorioNotificaciones)
    repo.obtener_polizas_alertables_renovacion.return_value = polizas
    repo.registrar.return_value = True
    generar = MagicMock(spec=GenerarAlertaRenovacionPolizaUseCase)
    return GenerarAlertasRenovacionUseCase(repo, generar), repo, generar


@pytest.mark.unit
class TestGenerarAlertasRenovacion:

    @patch(f'{MODULO}.hub')
    def test_registra_las_alertas_de_cada_poliza(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta = crear_notificacion_mock(
            id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE', rut_usuario='11111111-1'
        )
        uc, repo, generar = _use_case([poliza])
        generar.evaluar.return_value = [alerta]

        creadas = uc.ejecutar(AHORA_REF)

        generar.evaluar.assert_called_once_with(poliza, AHORA_REF)
        repo.registrar.assert_called_once_with(alerta)
        assert creadas == [alerta]
        hub_mock.publicar_desde_hilo.assert_called_once()

    @patch(f'{MODULO}.hub')
    def test_no_duplica_alertas_ya_registradas(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta = crear_notificacion_mock(
            id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE', rut_usuario='11111111-1'
        )
        uc, repo, generar = _use_case([poliza])
        generar.evaluar.return_value = [alerta]
        repo.registrar.return_value = False

        creadas = uc.ejecutar(AHORA_REF)

        assert creadas == []
        hub_mock.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_sin_alertas_no_publica(self, hub_mock):
        uc, repo, generar = _use_case([crear_poliza_alertable_renovacion_mock()])
        generar.evaluar.return_value = []

        assert uc.ejecutar(AHORA_REF) == []
        repo.registrar.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_publica_los_destinatarios_de_las_alertas_creadas(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alertas = [
            crear_notificacion_mock(
                id=None,
                codigo_tipo='RENOVACION_COTIZACION_PENDIENTE',
                rut_usuario='11111111-1',
            ),
            crear_notificacion_mock(
                id=None,
                codigo_tipo='RENOVACION_COTIZACION_PENDIENTE',
                rut_usuario='22222222-2',
            ),
        ]
        uc, repo, generar = _use_case([poliza])
        generar.evaluar.return_value = alertas

        uc.ejecutar(AHORA_REF)

        destinatarios = list(hub_mock.publicar_desde_hilo.call_args.args[0])
        assert sorted(destinatarios) == ['11111111-1', '22222222-2']

    @patch(f'{MODULO}.hub')
    def test_evalua_todas_las_polizas_alertables(self, hub_mock):
        polizas = [
            crear_poliza_alertable_renovacion_mock(numero_poliza=f'POL-00{i}')
            for i in range(3)
        ]
        uc, repo, generar = _use_case(polizas)
        generar.evaluar.return_value = []

        uc.ejecutar(AHORA_REF)

        assert generar.evaluar.call_count == 3
