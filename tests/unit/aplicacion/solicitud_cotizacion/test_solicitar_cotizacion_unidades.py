from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import (
    SolicitudCotizacionRequest,
)
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import (
    SolicitarCotizacionUseCase,
)
from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import (
    RepositorioSolicitudesCotizacion,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion


def _request(monto_asegurado=41500.0):
    return SolicitudCotizacionRequest(
        prioridad='ALTA',
        observaciones=None,
        tipo='unidades',
        id_solicitud_previa=None,
        monto_asegurado=monto_asegurado,
    )


def _use_case():
    repo_solicitudes = MagicMock(spec=RepositorioSolicitudesCotizacion)
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar.return_value = MagicMock(id=42)
    authorization = MagicMock()
    authorization.usuario_puede_solicitar_cotizacion.return_value = True
    repo_estados = MagicMock(spec=RepositorioEstadosProcesoComercial)
    repo_estados.obtener_por_codigo.return_value = EstadoInformativoProcesoComercial(
        codigo='COTIZACION_SOLICITADA_COMPANY', nombre=''
    )
    repo_historial = MagicMock(spec=RepositorioHistorialEstadoProcesosComerciales)
    servicio_alertas = MagicMock()
    servicio_alertas.marcar_leidas.return_value = []

    uc = SolicitarCotizacionUseCase(
        repo_solicitudes,
        repo_procesos,
        authorization,
        repo_estados,
        repo_historial,
        servicio_alertas,
    )
    return uc, repo_solicitudes


@pytest.mark.unit
class TestSolicitarCotizacionUnidades:

    def test_crea_la_solicitud_sin_datos_de_alicuota(self):
        # La alícuota vive en la oportunidad: la solicitud solo lleva su monto
        uc, repo = _use_case()

        uc.ejecutar(id_proceso_comercial=42, request=_request(), usuario=MagicMock(rut='1'))

        solicitud = repo.nueva_solicitud.call_args.kwargs['solicitud']
        assert isinstance(solicitud, SolicitudCotizacion)
        assert solicitud.tipo == 'unidades'
        assert solicitud.monto_asegurado == 41500.0

    def test_crea_la_solicitud_sin_alicuota_importada(self):
        # La alícuota puede agregarse después: no se exige para crear la solicitud
        uc, repo = _use_case()

        uc.ejecutar(
            id_proceso_comercial=42,
            request=_request(monto_asegurado=None),
            usuario=MagicMock(rut='1'),
        )

        repo.nueva_solicitud.assert_called_once()
