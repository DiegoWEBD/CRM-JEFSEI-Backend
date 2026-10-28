from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.poliza.use_cases.actualizar_poliza import ActualizarPolizaUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas

MODULO = 'app.aplicacion.poliza.use_cases.actualizar_poliza'

FIN_VIGENCIA = datetime(2026, 12, 31, 0, 0, 0, tzinfo=timezone.utc)


class _Usuario:
    def __init__(self, rut: str = '11111111-1'):
        self.rut = rut


def _use_case(fin_vigencia_guardada=FIN_VIGENCIA, autorizado=True):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    poliza = MagicMock(spec=Poliza)
    poliza.fin_vigencia = fin_vigencia_guardada
    repo_polizas.buscar.return_value = poliza

    authorization_service = MagicMock(spec=AuthorizationService)
    authorization_service.usuario_puede_actualizar_poliza.return_value = autorizado

    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas_renovacion.return_value = ['11111111-1']

    uc = ActualizarPolizaUseCase(repo_polizas, authorization_service, servicio_alertas)
    return uc, repo_polizas, authorization_service, servicio_alertas


def _ejecutar(uc, fin_vigencia=FIN_VIGENCIA):
    uc.ejecutar(
        numero_poliza='POL-001',
        usuario=_Usuario(),
        tipo='nueva',
        prima_neta=100.0,
        comision_corredora_pct=10.0,
        fecha_emision=None,
        inicio_vigencia=None,
        fin_vigencia=fin_vigencia,
        id_company=None,
    )


@pytest.mark.unit
class TestActualizarPolizaAlertasRenovacion:

    def test_poliza_no_encontrada(self):
        uc, repo_polizas, _, _ = _use_case()
        repo_polizas.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar(uc)

    def test_sin_permiso_no_actualiza(self):
        uc, repo_polizas, _, _ = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(uc)

        repo_polizas.actualizar.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_cambiar_fin_vigencia_resuelve_las_alertas(self, hub_mock):
        uc, _, _, servicio_alertas = _use_case()

        _ejecutar(uc, fin_vigencia=datetime(2027, 1, 31, tzinfo=timezone.utc))

        servicio_alertas.marcar_leidas_renovacion.assert_called_once()
        assert servicio_alertas.marcar_leidas_renovacion.call_args.args[0] == 'POL-001'
        hub_mock.publicar_desde_hilo.assert_called_once()

    @patch(f'{MODULO}.hub')
    def test_fin_vigencia_sin_cambio_no_resuelve(self, hub_mock):
        uc, _, _, servicio_alertas = _use_case()

        _ejecutar(uc, fin_vigencia=FIN_VIGENCIA)

        servicio_alertas.marcar_leidas_renovacion.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_mismo_instante_en_otra_zona_horaria_no_resuelve(self, hub_mock):
        """El mismo instante expresado como datetime naive no cuenta como cambio."""
        uc, _, _, servicio_alertas = _use_case()

        _ejecutar(uc, fin_vigencia=datetime(2026, 12, 31, 0, 0, 0))

        servicio_alertas.marcar_leidas_renovacion.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_quitar_fin_vigencia_resuelve_las_alertas(self, hub_mock):
        uc, _, _, servicio_alertas = _use_case()

        _ejecutar(uc, fin_vigencia=None)

        servicio_alertas.marcar_leidas_renovacion.assert_called_once()

    @patch(f'{MODULO}.hub')
    def test_sin_alertas_marcadas_no_publica(self, hub_mock):
        uc, _, _, servicio_alertas = _use_case()
        servicio_alertas.marcar_leidas_renovacion.return_value = []

        _ejecutar(uc, fin_vigencia=datetime(2027, 1, 31, tzinfo=timezone.utc))

        hub_mock.publicar_desde_hilo.assert_not_called()
