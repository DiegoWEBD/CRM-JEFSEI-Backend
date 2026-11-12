from app.aplicacion.solicitud_cotizacion.dto.filtro_panel_cotizaciones import (
    ESTADOS_PANEL_COTIZACIONES,
    PRIORIDADES_PANEL_COTIZACIONES,
    FiltroPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.listado_panel_cotizaciones import (
    ListadoPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_service import (
    ConsultaPanelCotizacionesService,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException


class ObtenerPanelCotizacionesUseCase:

    def __init__(
        self,
        consulta_service: ConsultaPanelCotizacionesService,
    ) -> None:
        self.consulta_service = consulta_service

    def ejecutar(
        self,
        rut_scoping: str | None,
        filtro: FiltroPanelCotizaciones,
    ) -> ListadoPanelCotizaciones:
        filtro = self._normalizar_filtro(filtro)

        filas, total = self.consulta_service.listar(rut_scoping, filtro)
        # Contadores globales: el servicio los calcula antes de aplicar
        # cualquier filtro, solo respetando el scope por permisos.
        contadores = self.consulta_service.contadores(rut_scoping)

        return ListadoPanelCotizaciones(
            filas=filas,
            total=total,
            contadores=contadores,
        )

    def _normalizar_filtro(
        self,
        filtro: FiltroPanelCotizaciones,
    ) -> FiltroPanelCotizaciones:
        texto_busqueda = filtro.texto_busqueda.strip() if filtro.texto_busqueda else None
        estado = filtro.estado or None
        prioridad = filtro.prioridad or None
        rut_ejecutivo = filtro.rut_ejecutivo or None

        if estado is not None and estado not in ESTADOS_PANEL_COTIZACIONES:
            raise DatoInvalidoException(f'Estado inválido: {estado}')

        if prioridad is not None and prioridad not in PRIORIDADES_PANEL_COTIZACIONES:
            raise DatoInvalidoException(f'Prioridad inválida: {prioridad}')

        return FiltroPanelCotizaciones(
            texto_busqueda=texto_busqueda or None,
            estado=estado,
            prioridad=prioridad,
            rut_ejecutivo=rut_ejecutivo,
            pagina=filtro.pagina,
            tamano_pagina=filtro.tamano_pagina,
        )
