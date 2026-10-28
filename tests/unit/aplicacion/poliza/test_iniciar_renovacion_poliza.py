from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.poliza.use_cases.iniciar_renovacion_poliza import IniciarRenovacionPolizaUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales

MODULO = 'app.aplicacion.poliza.use_cases.iniciar_renovacion_poliza'


class _Usuario:
    def __init__(self, rut: str = '11111111-1'):
        self.rut = rut


def _use_case(poliza_existe=True, autorizado=True, renovacion_existente=None):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    repo_polizas.buscar.return_value = MagicMock(spec=Poliza) if poliza_existe else None

    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar_renovacion_por_poliza_base.return_value = renovacion_existente
    repo_procesos.nuevo_renovacion.return_value = 77

    authorization_service = MagicMock(spec=AuthorizationService)
    authorization_service.usuario_puede_gestionar_renovacion.return_value = autorizado

    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas_renovacion.return_value = ['11111111-1']

    uc = IniciarRenovacionPolizaUseCase(
        repo_polizas, repo_procesos, authorization_service, servicio_alertas
    )
    return uc, repo_polizas, repo_procesos, authorization_service, servicio_alertas


@pytest.mark.unit
class TestIniciarRenovacionPoliza:

    def test_poliza_no_encontrada(self):
        uc, *_ = _use_case(poliza_existe=False)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar('POL-001', _Usuario())

    def test_sin_permiso_no_inicia(self):
        uc, _, repo_procesos, _, _ = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar('POL-001', _Usuario())

        repo_procesos.nuevo_renovacion.assert_not_called()

    def test_renovacion_ya_iniciada(self):
        uc, _, repo_procesos, _, _ = _use_case(renovacion_existente=77)

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar('POL-001', _Usuario())

        repo_procesos.nuevo_renovacion.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_crea_el_proceso_de_renovacion(self, hub_mock):
        uc, _, repo_procesos, _, _ = _use_case()

        id_proceso = uc.ejecutar('POL-001', _Usuario(rut='11111111-1'))

        repo_procesos.nuevo_renovacion.assert_called_once_with('POL-001', '11111111-1')
        assert id_proceso == 77

    @patch(f'{MODULO}.hub')
    def test_resuelve_las_alertas_de_renovacion(self, hub_mock):
        uc, _, _, _, servicio_alertas = _use_case()

        uc.ejecutar('POL-001', _Usuario())

        servicio_alertas.marcar_leidas_renovacion.assert_called_once()
        assert servicio_alertas.marcar_leidas_renovacion.call_args.args[0] == 'POL-001'
        hub_mock.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_resueltas'},
        )

    @patch(f'{MODULO}.hub')
    def test_sin_alertas_marcadas_no_publica(self, hub_mock):
        uc, _, _, _, servicio_alertas = _use_case()
        servicio_alertas.marcar_leidas_renovacion.return_value = []

        uc.ejecutar('POL-001', _Usuario())

        hub_mock.publicar_desde_hilo.assert_not_called()
