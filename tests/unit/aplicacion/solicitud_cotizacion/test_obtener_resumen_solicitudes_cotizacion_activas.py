from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_solicitudes_cotizacion import (
    FiltroSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import (
    SolicitudCotizacionResumen,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import (
    ConsultaSolicitudesCotizacionService,
)
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import (
    ObtenerResumenSolicitudesCotizacionActivasUseCase,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException


def _resumen(
    id_solicitud: int,
    campos_faltantes: list[str] | None = None,
) -> SolicitudCotizacionResumen:
    return SolicitudCotizacionResumen(
        id=id_solicitud,
        id_prospecto=10,
        nombre_riesgo=f'Riesgo {id_solicitud}',
        informacion_completa=True,
        ejecutivo_comercial='Ana Pérez',
        tipo='incendio',
        recotizacion=False,
        motivo_recotizacion=None,
        producto='Incendio Condominio',
        prioridad='alta',
        fecha='2026-11-10T10:00:00',
        tiene_cotizaciones=False,
        campos_faltantes=campos_faltantes if campos_faltantes is not None else [],
        estudio_disponible=False,
    )


CONTADORES = ContadoresSolicitudesCotizacion(
    informacion_incompleta=1,
    listas_para_cotizar=2,
    cotizaciones_emitidas=3,
    estudios_emitidos=4,
)


@pytest.mark.unit
class TestObtenerResumenSolicitudesCotizacion:

    def _use_case(self, filas=None, total=0, contadores=None):
        consulta_service = MagicMock(spec=ConsultaSolicitudesCotizacionService)
        consulta_service.listar.return_value = (filas if filas is not None else [], total)
        consulta_service.contadores.return_value = contadores or CONTADORES

        use_case = ObtenerResumenSolicitudesCotizacionActivasUseCase(
            consulta_service=consulta_service,
        )
        return use_case, consulta_service

    def test_devuelve_listado_con_total_y_contadores_propagados(self):
        filas = [_resumen(1), _resumen(2)]
        use_case, consulta_service = self._use_case(filas=filas, total=23)

        filtro = FiltroSolicitudesCotizacion(pagina=2, tamano_pagina=5)
        listado = use_case.ejecutar('11111111-1', filtro)

        assert listado.solicitudes == filas
        assert listado.total == 23
        assert listado.contadores == CONTADORES

        consulta_service.listar.assert_called_once()
        rut_scoping, filtro_recibido = consulta_service.listar.call_args.args
        assert rut_scoping == '11111111-1'
        assert filtro_recibido.pagina == 2
        assert filtro_recibido.tamano_pagina == 5
        consulta_service.contadores.assert_called_once_with('11111111-1')

    def test_propaga_los_campos_faltantes_de_las_filas(self):
        filas = [
            _resumen(1, campos_faltantes=['direccion']),
            _resumen(2, campos_faltantes=['rut_riesgo', 'comuna']),
        ]
        use_case, _ = self._use_case(filas=filas, total=2)

        listado = use_case.ejecutar(None, FiltroSolicitudesCotizacion())

        assert listado.solicitudes[0].campos_faltantes == ['direccion']
        assert listado.solicitudes[1].campos_faltantes == ['rut_riesgo', 'comuna']

    def test_no_depende_del_repositorio_de_prospectos(self):
        use_case, consulta_service = self._use_case(filas=[_resumen(1)])

        use_case.ejecutar(None, FiltroSolicitudesCotizacion())

        assert not hasattr(use_case, 'repositorio_prospectos')
        assert consulta_service.listar.call_count == 1

    def test_estado_invalido_lanza_dato_invalido(self):
        use_case, consulta_service = self._use_case()

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(None, FiltroSolicitudesCotizacion(estado='lo_que_sea'))

        consulta_service.listar.assert_not_called()

    def test_prioridad_invalida_lanza_dato_invalido(self):
        use_case, consulta_service = self._use_case()

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(None, FiltroSolicitudesCotizacion(prioridad='media'))

        consulta_service.listar.assert_not_called()

    def test_normaliza_texto_busqueda_y_valores_vacios(self):
        use_case, consulta_service = self._use_case()

        use_case.ejecutar(
            None,
            FiltroSolicitudesCotizacion(
                texto_busqueda='  cotiza  ',
                estado='',
                prioridad='',
                rut_usuario='',
            ),
        )

        filtro_recibido = consulta_service.listar.call_args.args[1]
        assert filtro_recibido.texto_busqueda == 'cotiza'
        assert filtro_recibido.estado is None
        assert filtro_recibido.prioridad is None
        assert filtro_recibido.rut_usuario is None

    def test_normaliza_texto_busqueda_solo_espacios_a_none(self):
        use_case, consulta_service = self._use_case()

        use_case.ejecutar(None, FiltroSolicitudesCotizacion(texto_busqueda='   '))

        filtro_recibido = consulta_service.listar.call_args.args[1]
        assert filtro_recibido.texto_busqueda is None
