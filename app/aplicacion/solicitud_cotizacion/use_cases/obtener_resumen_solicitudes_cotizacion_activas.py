from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import SolicitudCotizacionResumen
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import ConsultaSolicitudesCotizacionService
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerResumenSolicitudesCotizacionActivasUseCase:

    def __init__(
        self, 
        consulta_service: ConsultaSolicitudesCotizacionService,
        repositorio_prospectos: RepositorioProspectos
    ) -> None:
        self.consulta_service = consulta_service
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, rut_usuario: str | None) -> list[SolicitudCotizacionResumen]:
        solicitudes = self.consulta_service.obtener_todas(rut_usuario)

        for solicitud in solicitudes:
            prospecto = self.repositorio_prospectos.buscar(solicitud.id_prospecto)

            if not prospecto:
                continue

            campos_faltantes: list[str] = []

            # Campos base del prospecto (llenables por formulario)
            if prospecto.rut_riesgo is None:
                campos_faltantes.append('rut_riesgo')
            if prospecto.telefono_contacto is None:
                campos_faltantes.append('telefono_contacto')
            if prospecto.correo_contacto is None:
                campos_faltantes.append('correo_contacto')
            if prospecto.direccion is None:
                campos_faltantes.append('direccion')
            if prospecto.region is None:
                campos_faltantes.append('region')
            if prospecto.comuna is None:
                campos_faltantes.append('comuna')
            if prospecto.observaciones is None:
                campos_faltantes.append('observaciones')

            # Campos específicos de condominio
            if prospecto.linea_negocio.nombre.lower() == 'condominio':
                condominio = self.repositorio_prospectos.buscar_prospecto_condominio(solicitud.id_prospecto)

                if condominio is not None:
                    if condominio.administrador is None:
                        campos_faltantes.append('administrador')
                    if condominio.uf_por_metro_cuadrado is None:
                        campos_faltantes.append('uf_por_metro_cuadrado')
                    if condominio.porcentaje_depreciacion is None:
                        campos_faltantes.append('porcentaje_depreciacion')
                    if condominio.porcentaje_espacios_comunes is None:
                        campos_faltantes.append('porcentaje_espacios_comunes')
                    if condominio.tiene_locales_comerciales is None:
                        campos_faltantes.append('tiene_locales_comerciales')
                    if condominio.uso_del_condominio is None:
                        campos_faltantes.append('uso_del_condominio')
                    if condominio.materialidad is None:
                        campos_faltantes.append('materialidad')
                    if condominio.clasificacion_preliminar_incendio is None:
                        campos_faltantes.append('clasificacion_preliminar_incendio')
                    if condominio.procesos_productivos is None:
                        campos_faltantes.append('procesos_productivos')
                    if condominio.numero_pisos is None:
                        campos_faltantes.append('numero_pisos')
                    if condominio.numero_torres is None:
                        campos_faltantes.append('numero_torres')
                    if condominio.cantidad_departamentos is None:
                        campos_faltantes.append('cantidad_departamentos')
                    if condominio.cantidad_subterraneos is None:
                        campos_faltantes.append('cantidad_subterraneos')
                    if condominio.tiene_piscina is None:
                        campos_faltantes.append('tiene_piscina')
                    if condominio.ubicacion_piscina is None:
                        campos_faltantes.append('ubicacion_piscina')
                    if condominio.tiene_alarma_incendio is None:
                        campos_faltantes.append('tiene_alarma_incendio')
                    if condominio.tiene_sprinklers is None:
                        campos_faltantes.append('tiene_sprinklers')
                    if condominio.year_construccion is None:
                        campos_faltantes.append('year_construccion')
                    if condominio.metros_cuadrados is None:
                        campos_faltantes.append('metros_cuadrados')

            solicitud.campos_faltantes = campos_faltantes

        return solicitudes