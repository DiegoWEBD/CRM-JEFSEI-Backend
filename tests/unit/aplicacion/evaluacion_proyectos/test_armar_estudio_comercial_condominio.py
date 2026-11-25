from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import (
    ArmarEstudioComercialCondominioUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException

MODULO = 'app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio'

BUSCAR_COTIZACIONES = '_ArmarEstudioComercialCondominioUseCase__buscar_cotizaciones'


def _use_case(solicitudes=None, cotizacion=None, pertenece=False):
    authorization_service = MagicMock()
    authorization_service.usuario_puede_crear_estudio_comercial.return_value = True

    repositorio_prospectos = MagicMock()
    repositorio_prospectos.buscar_prospecto_condominio.return_value = MagicMock(id=5)

    repositorio_company_seguros = MagicMock()

    repositorio_cotizaciones = MagicMock()
    repositorio_cotizaciones.obtener_por_id.return_value = cotizacion
    repositorio_cotizaciones.cotizacion_pertenece_a_solicitud.return_value = pertenece

    proceso = MagicMock(id=10, id_prospecto=5, cerrado=False)
    proceso.producto.codigo = 'espacios_comunes'
    repositorio_procesos_comerciales = MagicMock()
    repositorio_procesos_comerciales.buscar.return_value = proceso

    repositorio_solicitudes = MagicMock()
    repositorio_solicitudes.obtener_solicitudes.return_value = (
        solicitudes if solicitudes is not None else []
    )

    with patch(f'{MODULO}.DocxTemplate') as docx_mock:
        uc = ArmarEstudioComercialCondominioUseCase(
            authorization_service=authorization_service,
            repositorio_prospectos=repositorio_prospectos,
            repositorio_company_seguros=repositorio_company_seguros,
            repositorio_cotizaciones=repositorio_cotizaciones,
            repositorio_procesos_comerciales=repositorio_procesos_comerciales,
            repositorio_solicitudes_cotizacion=repositorio_solicitudes,
        )

    return uc, repositorio_cotizaciones, repositorio_solicitudes, docx_mock.return_value


EJECUTAR_ARGS = dict(
    id_proceso_comercial=10,
    monto_asegurado_actual=None,
    con_monto_sugerido=True,
    infraseguro_primer_ejemplo=None,
    infraseguro_segundo_ejemplo=None,
    cantidad_cuotas=12,
    ids_cotizacion=[10],
    secciones=None,
    valor_uf=39000.0,
    usuario=MagicMock(rut='12345678-9'),
)


@pytest.mark.unit
class TestArmarEstudioComercialValidacionCotizaciones:

    def test_cotizacion_ajena_no_se_filtra_al_estudio(self):
        uc, repo_cotizaciones, _, doc = _use_case(
            solicitudes=[MagicMock(id=5)],
            cotizacion=MagicMock(id=10),
            pertenece=False,
        )

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(**EJECUTAR_ARGS)

        doc.render.assert_not_called()

    def test_cotizacion_inexistente_retorna_404(self):
        uc, _, _, doc = _use_case(
            solicitudes=[MagicMock(id=5)],
            cotizacion=None,
        )

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(**EJECUTAR_ARGS)

        doc.render.assert_not_called()

    def test_cotizacion_pertenece_a_una_de_las_solicitudes_del_proceso(self):
        uc, repo_cotizaciones, _, _ = _use_case(
            solicitudes=[MagicMock(id=5), MagicMock(id=7)],
            cotizacion=MagicMock(id=10),
            pertenece=False,
        )
        repo_cotizaciones.cotizacion_pertenece_a_solicitud.side_effect = [
            False,
            True,
        ]

        cotizaciones = getattr(uc, BUSCAR_COTIZACIONES)([10], 10)

        assert cotizaciones == [repo_cotizaciones.obtener_por_id.return_value]
        assert repo_cotizaciones.cotizacion_pertenece_a_solicitud.call_count == 2

    def test_proceso_sin_solicitudes_rechaza_cotizaciones(self):
        uc, _, _, _ = _use_case(
            solicitudes=[],
            cotizacion=MagicMock(id=10),
            pertenece=True,
        )

        with pytest.raises(ConflictoEnAccionException):
            getattr(uc, BUSCAR_COTIZACIONES)([10], 10)

    def test_cotizacion_inexistente_en_el_body_retorna_404(self):
        uc, repo_cotizaciones, _, _ = _use_case(
            solicitudes=[MagicMock(id=5)],
            cotizacion=None,
        )

        with pytest.raises(RecursoNoEncontradoException):
            getattr(uc, BUSCAR_COTIZACIONES)([99], 10)
