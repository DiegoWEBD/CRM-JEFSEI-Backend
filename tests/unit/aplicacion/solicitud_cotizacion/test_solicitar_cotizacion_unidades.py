from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import (
    SolicitudCotizacionRequest,
    UnidadAlicuotaRequest,
)
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import (
    SolicitarCotizacionUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import (
    RepositorioSolicitudesCotizacion,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.solicitud_cotizacion_unidades import (
    SolicitudCotizacionUnidades,
)

MODULO = 'app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion'


def _request(unidades=None, nombre_excel='alicuota.xlsx'):
    return SolicitudCotizacionRequest(
        prioridad='ALTA',
        observaciones=None,
        tipo='unidades',
        id_solicitud_previa=None,
        nombre_excel=nombre_excel,
        unidades=unidades,
    )


def _use_case():
    repo_solicitudes = MagicMock(spec=RepositorioSolicitudesCotizacion)
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar.return_value = MagicMock(id=42)
    authorization = MagicMock()
    authorization.usuario_puede_solicitar_cotizacion.return_value = True
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    servicio_alertas = MagicMock()
    servicio_alertas.marcar_leidas.return_value = []

    uc = SolicitarCotizacionUseCase(
        repo_solicitudes,
        repo_procesos,
        authorization,
        repo_notificaciones,
        servicio_alertas,
    )
    return uc, repo_solicitudes


def _unidades():
    return [
        UnidadAlicuotaRequest(identificador_unidad='Depto 1', prorrateo=2.5, fila_origen=2),
        UnidadAlicuotaRequest(identificador_unidad='Depto 2', prorrateo=1.5, fila_origen=3),
    ]


@pytest.mark.unit
class TestSolicitarCotizacionUnidades:

    def test_persiste_las_unidades_en_la_solicitud(self):
        uc, repo = _use_case()

        uc.ejecutar(id_proceso_comercial=42, request=_request(unidades=_unidades()), usuario=MagicMock(rut='1'))

        solicitud = repo.nueva_solicitud.call_args.kwargs['solicitud']
        assert isinstance(solicitud, SolicitudCotizacionUnidades)
        assert len(solicitud.unidades) == 2
        assert solicitud.unidades[0].identificador_unidad == 'Depto 1'
        assert solicitud.unidades[0].prorrateo == 2.5

    def test_unidades_validas_no_bloquean(self):
        uc, repo = _use_case()

        uc.ejecutar(id_proceso_comercial=42, request=_request(unidades=_unidades()), usuario=MagicMock(rut='1'))

        repo.nueva_solicitud.assert_called_once()

    def test_identificador_vacio_es_rechazado(self):
        uc, repo = _use_case()
        unidades = [UnidadAlicuotaRequest(identificador_unidad='  ', prorrateo=2.5, fila_origen=2)]

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(id_proceso_comercial=42, request=_request(unidades=unidades), usuario=MagicMock(rut='1'))

        repo.nueva_solicitud.assert_not_called()

    def test_identificador_duplicado_es_rechazado(self):
        uc, repo = _use_case()
        unidades = [
            UnidadAlicuotaRequest(identificador_unidad='Depto 1', prorrateo=2.5, fila_origen=2),
            UnidadAlicuotaRequest(identificador_unidad='depto 1', prorrateo=1.5, fila_origen=3),
        ]

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(id_proceso_comercial=42, request=_request(unidades=unidades), usuario=MagicMock(rut='1'))

        repo.nueva_solicitud.assert_not_called()

    def test_prorrateo_negativo_es_rechazado(self):
        uc, repo = _use_case()
        unidades = [UnidadAlicuotaRequest(identificador_unidad='Depto 1', prorrateo=-1, fila_origen=2)]

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(id_proceso_comercial=42, request=_request(unidades=unidades), usuario=MagicMock(rut='1'))

        repo.nueva_solicitud.assert_not_called()

    def test_sin_unidades_mantiene_el_comportamiento_actual(self):
        uc, repo = _use_case()

        uc.ejecutar(id_proceso_comercial=42, request=_request(unidades=None), usuario=MagicMock(rut='1'))

        solicitud = repo.nueva_solicitud.call_args.kwargs['solicitud']
        assert solicitud.nombre_excel == 'alicuota.xlsx'
        assert solicitud.unidades == []
