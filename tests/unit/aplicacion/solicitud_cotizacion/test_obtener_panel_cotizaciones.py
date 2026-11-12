from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.dto.contadores_panel_cotizaciones import (
    ContadoresPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.cotizacion_resumen import CotizacionResumen
from app.aplicacion.solicitud_cotizacion.dto.filtro_panel_cotizaciones import (
    FiltroPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.fila_panel_cotizaciones import (
    FilaPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_service import (
    ConsultaPanelCotizacionesService,
)
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_panel_cotizaciones import (
    ObtenerPanelCotizacionesUseCase,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException


def _fila(id_solicitud: int) -> FilaPanelCotizaciones:
    return FilaPanelCotizaciones(
        id=id_solicitud,
        id_prospecto=10,
        id_proceso_comercial=20,
        cliente=f'Condominio {id_solicitud}',
        linea_seguro='Incendio Condominio',
        ejecutivo_comercial='Ana Pérez',
        prioridad='alta',
        fecha='2026-11-10T10:00:00',
        cantidad_cotizaciones=1,
        vencimiento_mas_proximo='2026-12-01T00:00:00',
        estado='VIGENTE',
        tiene_estudio=False,
        id_estudio=None,
        cotizaciones=[
            CotizacionResumen(
                id=11,
                company='Company',
                prima_neta=10.0,
                prima_bruta=11.9,
                fecha_vencimiento='2026-12-01T00:00:00',
                estado='VIGENTE',
            )
        ],
    )


CONTADORES = ContadoresPanelCotizaciones(
    cotizaciones_vigentes=1,
    cotizaciones_por_vencer=2,
    cotizaciones_vencidas=3,
    estudios_pendientes=4,
    estudios_emitidos=5,
)


@pytest.mark.unit
class TestObtenerPanelCotizaciones:

    def _use_case(self, filas=None, total=0, contadores=None):
        consulta_service = MagicMock(spec=ConsultaPanelCotizacionesService)
        consulta_service.listar.return_value = (filas if filas is not None else [], total)
        consulta_service.contadores.return_value = contadores or CONTADORES

        use_case = ObtenerPanelCotizacionesUseCase(consulta_service=consulta_service)
        return use_case, consulta_service

    def test_devuelve_listado_con_total_y_contadores_propagados(self):
        filas = [_fila(1), _fila(2)]
        use_case, consulta_service = self._use_case(filas=filas, total=23)

        filtro = FiltroPanelCotizaciones(pagina=2, tamano_pagina=5)
        listado = use_case.ejecutar('11111111-1', filtro)

        assert listado.filas == filas
        assert listado.total == 23
        assert listado.contadores == CONTADORES

        consulta_service.listar.assert_called_once()
        rut_scoping, filtro_recibido = consulta_service.listar.call_args.args
        assert rut_scoping == '11111111-1'
        assert filtro_recibido.pagina == 2
        assert filtro_recibido.tamano_pagina == 5
        # Los contadores se piden sin filtro: son globales.
        consulta_service.contadores.assert_called_once_with('11111111-1')

    def test_propaga_el_resumen_de_cotizaciones_de_las_filas(self):
        filas = [_fila(1)]
        use_case, _ = self._use_case(filas=filas, total=1)

        listado = use_case.ejecutar(None, FiltroPanelCotizaciones())

        assert listado.filas[0].cotizaciones[0].company == 'Company'
        assert listado.filas[0].cotizaciones[0].estado == 'VIGENTE'

    @pytest.mark.parametrize(
        'estado',
        [
            'cotizaciones_vigentes',
            'cotizaciones_por_vencer',
            'cotizaciones_vencidas',
            'estudios_pendientes',
            'estudios_emitidos',
        ],
    )
    def test_acepta_los_cinco_estados_del_panel(self, estado):
        use_case, consulta_service = self._use_case()

        use_case.ejecutar(None, FiltroPanelCotizaciones(estado=estado))

        assert consulta_service.listar.call_args.args[1].estado == estado

    def test_estado_invalido_lanza_dato_invalido(self):
        use_case, consulta_service = self._use_case()

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(None, FiltroPanelCotizaciones(estado='lo_que_sea'))

        consulta_service.listar.assert_not_called()

    def test_prioridad_invalida_lanza_dato_invalido(self):
        use_case, consulta_service = self._use_case()

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(None, FiltroPanelCotizaciones(prioridad='media'))

        consulta_service.listar.assert_not_called()

    def test_normaliza_texto_busqueda_y_valores_vacios(self):
        use_case, consulta_service = self._use_case()

        use_case.ejecutar(
            None,
            FiltroPanelCotizaciones(
                texto_busqueda='  torres  ',
                estado='',
                prioridad='',
                rut_ejecutivo='',
            ),
        )

        filtro_recibido = consulta_service.listar.call_args.args[1]
        assert filtro_recibido.texto_busqueda == 'torres'
        assert filtro_recibido.estado is None
        assert filtro_recibido.prioridad is None
        assert filtro_recibido.rut_ejecutivo is None

    def test_normaliza_texto_busqueda_solo_espacios_a_none(self):
        use_case, consulta_service = self._use_case()

        use_case.ejecutar(None, FiltroPanelCotizaciones(texto_busqueda='   '))

        filtro_recibido = consulta_service.listar.call_args.args[1]
        assert filtro_recibido.texto_busqueda is None
