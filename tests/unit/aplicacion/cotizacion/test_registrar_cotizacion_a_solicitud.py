from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import (
    RegistrarCotizacionASolicitudUseCase,
)
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)

MODULO = 'app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud'


def _use_case(existe_solicitud=True, puede_registrar=True, proceso=None):
    repo_companies = MagicMock()
    repo_solicitudes = MagicMock()
    repo_solicitudes.existe_solicitud.return_value = existe_solicitud
    repo_cotizaciones = MagicMock()
    authorization = MagicMock()
    authorization.usuario_puede_registrar_cotizacion.return_value = puede_registrar
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar_por_solicitud_cotizacion.return_value = proceso
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = []
    servicio_archivos = MagicMock(spec=ServicioArchivos)
    uc = RegistrarCotizacionASolicitudUseCase(
        repo_companies,
        repo_solicitudes,
        repo_cotizaciones,
        authorization,
        repo_procesos,
        MagicMock(),
        servicio_alertas,
        servicio_archivos,
    )
    return uc, repo_solicitudes, repo_cotizaciones, authorization, repo_procesos


EJECUTAR_ARGS = dict(
    rut_usuario='99999999-9',
    id_solicitud=3,
    monto_total_asegurado=1000.0,
    asistencia_afecta=0.0,
    asistencia_excenta=0.0,
    id_company=1,
    fecha_emision='2026-01-01T00:00:00',
    fecha_vencimiento='2027-01-01T00:00:00',
    tipo='prima',
    prima_afecta=100.0,
    prima_excenta=50.0,
)


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestRegistrarCotizacionASolicitudAutorizacion:

    def test_solicitud_inexistente_retorna_404(self, mock_hub):
        uc, _, repo_cotizaciones, authorization, _ = _use_case(existe_solicitud=False)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(**EJECUTAR_ARGS)

        authorization.usuario_puede_registrar_cotizacion.assert_not_called()
        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_not_called()

    def test_sin_permiso_de_carga_retorna_403(self, mock_hub):
        uc, _, repo_cotizaciones, authorization, _ = _use_case(puede_registrar=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(**EJECUTAR_ARGS)

        # El re-chequeo es de escritura (CARGAR_COTIZACIONES + ownership),
        # no de vista.
        authorization.usuario_puede_ver_solicitud_cotizacion.assert_not_called()
        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_not_called()

    def test_permiso_de_carga_sin_ownership_retorna_403(self, mock_hub):
        # El repositorio de autorización deniega cuando el usuario no es el
        # rut_ej_evaluacion_asignado de la solicitud (ownership estricto).
        uc, _, repo_cotizaciones, authorization, _ = _use_case(puede_registrar=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(**EJECUTAR_ARGS)

        authorization.usuario_puede_registrar_cotizacion.assert_called_once_with('99999999-9', 3)
        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_not_called()

    def test_proceso_inexistente_retorna_404_sin_escritura_parcial(self, mock_hub):
        uc, _, repo_cotizaciones, _, repo_procesos = _use_case(proceso=None)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(**EJECUTAR_ARGS)

        repo_procesos.buscar_por_solicitud_cotizacion.assert_called_once_with(3)
        # La cotización no se registra si el proceso no existe (antes quedaba
        # una escritura parcial).
        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_not_called()

    def test_proceso_cerrado_retorna_conflicto(self, mock_hub):
        uc, _, repo_cotizaciones, _, _ = _use_case(proceso=MagicMock(id=42, cerrado=True))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(**EJECUTAR_ARGS)

        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_not_called()

    def test_registro_exitoso_con_ownership(self, mock_hub):
        uc, _, repo_cotizaciones, authorization, _ = _use_case(
            proceso=MagicMock(id=42, cerrado=False)
        )

        uc.ejecutar(**EJECUTAR_ARGS)

        authorization.usuario_puede_registrar_cotizacion.assert_called_once_with('99999999-9', 3)
        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_called_once()
        assert repo_cotizaciones.registrar_cotizacion_a_solicitud.call_args.args[0] == 3
        assert repo_cotizaciones.registrar_cotizacion_a_solicitud.call_args.args[2] == '99999999-9'
