from datetime import datetime, timezone

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion


class ServicioProyeccionesComerciales:

    DECIMALES = 2

    def __init__(
        self,
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_cotizaciones: RepositorioCotizaciones
    ):
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_cotizaciones = repositorio_cotizaciones

    def prima_cotizada(self, proceso: ProcesoComercial) -> float:
        prima = 0
        solicitudes = self.repositorio_solicitudes_cotizacion.obtener_solicitudes(proceso.id)

        for solicitud in solicitudes:
            if not solicitud.id:
                continue

            cotizaciones = self.repositorio_cotizaciones.obtener_por_solicitud(solicitud.id)

            for cotizacion in cotizaciones:
                if cotizacion.fecha_vencimiento < datetime.now(tz=timezone.utc):
                    continue

                prima += cotizacion.prima_neta

        return round(prima, ServicioProyeccionesComerciales.DECIMALES)

    def prima_potencial_estimada(self, proceso: ProcesoComercial) -> float:
        prima = 0
        vigentes = 0
        solicitudes = self.repositorio_solicitudes_cotizacion.obtener_solicitudes(proceso.id)

        for solicitud in solicitudes:
            if not solicitud.id:
                continue

            cotizaciones = self.repositorio_cotizaciones.obtener_por_solicitud(solicitud.id)

            for cotizacion in cotizaciones:
                if cotizacion.fecha_vencimiento < datetime.now(tz=timezone.utc):
                    continue

                vigentes += 1
                prima += cotizacion.prima_neta
                
        prima /= vigentes if vigentes > 0 else 1

        return round(prima, ServicioProyeccionesComerciales.DECIMALES)

    def prima_esperada(self, proceso: ProcesoComercial) -> float | None:
        probabilidad_cierre = proceso.probabilidad_cierre_ejecutivo

        if probabilidad_cierre is None:
            probabilidad_cierre = proceso.estado_actual.probabilidad_cierre

        if probabilidad_cierre is None:
            return None

        return round(self.prima_potencial_estimada(proceso) * probabilidad_cierre, ServicioProyeccionesComerciales.DECIMALES)