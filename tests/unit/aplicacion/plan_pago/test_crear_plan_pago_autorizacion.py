from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.plan_pago.use_cases.crear_plan_pago import CrearPlanPagoUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException

MODULO = 'app.aplicacion.plan_pago.use_cases.crear_plan_pago'

MENSAJE_NO_ENCONTRADA = 'Póliza POL-001 no encontrada'

_AUSENTE = object()


def _use_case(poliza=_AUSENTE, puede_crear=True, plan_existente=None):
    repo_polizas = MagicMock()
    repo_polizas.buscar.return_value = (
        MagicMock(numero_poliza='POL-001', id_proceso_comercial=42)
        if poliza is _AUSENTE
        else poliza
    )
    repo_planes_pago = MagicMock()
    repo_planes_pago.buscar_plan_pago_poliza.return_value = plan_existente
    authorization = MagicMock()
    authorization.usuario_puede_crear_plan_pago.return_value = puede_crear
    repo_procesos = MagicMock()
    repo_procesos.buscar.return_value = MagicMock(id=42)
    servicio_alertas = MagicMock()
    servicio_alertas.marcar_leidas.return_value = []
    uc = CrearPlanPagoUseCase(
        repo_polizas,
        repo_planes_pago,
        authorization,
        repo_procesos,
        MagicMock(),
        servicio_alertas,
    )
    return uc, repo_planes_pago, authorization


EJECUTAR_ARGS = dict(
    numero_poliza='POL-001',
    fecha_primera_cuota=datetime(2026, 3, 1),
    numero_cuotas=3,
    usuario=MagicMock(rut='99999999-9'),
)


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestCrearPlanPagoAutorizacion:

    def test_poliza_inexistente_retorna_404(self, hub_mock):
        uc, repo_planes_pago, authorization = _use_case(poliza=None)

        with pytest.raises(RecursoNoEncontradoException) as exc:
            uc.ejecutar(**EJECUTAR_ARGS)

        assert str(exc.value) == MENSAJE_NO_ENCONTRADA
        authorization.usuario_puede_crear_plan_pago.assert_not_called()
        repo_planes_pago.registrar_plan_pago_poliza.assert_not_called()

    def test_denegacion_retorna_404_identico_al_inexistente(self, hub_mock):
        # Política anti-oráculo: la denegación de ownership responde 404 con el
        # mismo mensaje que una póliza que no existe.
        uc, repo_planes_pago, authorization = _use_case(puede_crear=False)

        with pytest.raises(RecursoNoEncontradoException) as exc:
            uc.ejecutar(**EJECUTAR_ARGS)

        assert str(exc.value) == MENSAJE_NO_ENCONTRADA
        authorization.usuario_puede_crear_plan_pago.assert_called_once_with('99999999-9', 'POL-001')
        repo_planes_pago.registrar_plan_pago_poliza.assert_not_called()

    def test_plan_ya_existente_retorna_conflicto(self, hub_mock):
        uc, repo_planes_pago, _ = _use_case(plan_existente=MagicMock())

        with pytest.raises(RecursoYaExisteException):
            uc.ejecutar(**EJECUTAR_ARGS)

        repo_planes_pago.registrar_plan_pago_poliza.assert_not_called()

    def test_creacion_exitosa_con_ownership(self, hub_mock):
        uc, repo_planes_pago, authorization = _use_case()

        uc.ejecutar(**EJECUTAR_ARGS)

        authorization.usuario_puede_crear_plan_pago.assert_called_once_with('99999999-9', 'POL-001')
        repo_planes_pago.registrar_plan_pago_poliza.assert_called_once()
