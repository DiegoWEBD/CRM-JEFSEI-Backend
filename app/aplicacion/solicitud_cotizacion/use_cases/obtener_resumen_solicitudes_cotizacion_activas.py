from app.aplicacion.solicitud_cotizacion.dto.filtro_solicitudes_cotizacion import (
    ESTADOS_SOLICITUDES,
    PRIORIDADES_SOLICITUDES,
    FiltroSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.listado_solicitudes_cotizacion import (
    ListadoSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import (
    ConsultaSolicitudesCotizacionService,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException


class ObtenerResumenSolicitudesCotizacionActivasUseCase:

    def __init__(
        self,
        consulta_service: ConsultaSolicitudesCotizacionService,
    ) -> None:
        self.consulta_service = consulta_service

    def ejecutar(
        self,
        rut_scoping: str | None,
        filtro: FiltroSolicitudesCotizacion,
    ) -> ListadoSolicitudesCotizacion:

        filtro = self._normalizar_filtro(filtro)

        solicitudes, total = self.consulta_service.listar(rut_scoping, filtro)
        contadores = self.consulta_service.contadores(rut_scoping)

        return ListadoSolicitudesCotizacion(
            solicitudes=solicitudes,
            total=total,
            contadores=contadores,
        )

    def _normalizar_filtro(self, filtro: FiltroSolicitudesCotizacion) -> FiltroSolicitudesCotizacion:
        texto_busqueda = filtro.texto_busqueda.strip() if filtro.texto_busqueda else None
        estado = filtro.estado or None
        prioridad = filtro.prioridad or None
        rut_usuario = filtro.rut_usuario or None

        if estado is not None and estado not in ESTADOS_SOLICITUDES:
            raise DatoInvalidoException(f'Estado inválido: {estado}')

        if prioridad is not None and prioridad not in PRIORIDADES_SOLICITUDES:
            raise DatoInvalidoException(f'Prioridad inválida: {prioridad}')

        return FiltroSolicitudesCotizacion(
            texto_busqueda=texto_busqueda or None,
            estado=estado,
            prioridad=prioridad,
            rut_usuario=rut_usuario,
            pagina=filtro.pagina,
            tamano_pagina=filtro.tamano_pagina,
        )
