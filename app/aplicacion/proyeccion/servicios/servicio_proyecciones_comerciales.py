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

    def prima_cotizada_total(self, procesos: list[ProcesoComercial]) -> float:
        """Suma de la prima cotizada de cada oportunidad.

        Delega en `prima_cotizada` (solo cotizaciones vigentes).
        """
        return round(
            sum(self.prima_cotizada(proceso) for proceso in procesos),
            ServicioProyeccionesComerciales.DECIMALES,
        )

    def prima_potencial_estimada_total(self, procesos: list[ProcesoComercial]) -> float:
        """Suma de la prima potencial estimada de cada oportunidad.

        Delega en `prima_potencial_estimada`.
        """
        return round(
            sum(self.prima_potencial_estimada(proceso) for proceso in procesos),
            ServicioProyeccionesComerciales.DECIMALES,
        )

    def prima_esperada_total(self, procesos: list[ProcesoComercial]) -> float:
        """Suma de la prima esperada de cada oportunidad.

        Delega en `prima_esperada`; las oportunidades sin probabilidad de
        cierre no aportan (el método devuelve None).
        """
        total = 0

        for proceso in procesos:
            esperada = self.prima_esperada(proceso)

            if esperada is not None:
                total += esperada

        return round(total, ServicioProyeccionesComerciales.DECIMALES)

    def proyeccion_prima_esperada_por_mes(
        self, procesos: list[ProcesoComercial]
    ) -> list[dict]:
        """Prima esperada agrupada por mes de la fecha estimada de cierre.

        Solo se incluyen los meses con al menos una oportunidad, en orden
        ascendente. Las oportunidades sin fecha estimada de cierre o sin
        prima esperada no aportan. Delega en `prima_esperada`.
        """
        por_mes: dict[str, float] = {}

        for proceso in procesos:
            if proceso.fecha_estimada_cierre is None:
                continue

            esperada = self.prima_esperada(proceso)

            if esperada is None:
                continue

            mes = proceso.fecha_estimada_cierre.strftime('%Y-%m')
            por_mes[mes] = por_mes.get(mes, 0) + esperada

        return [
            {
                'mes': mes,
                'prima_esperada': round(total, ServicioProyeccionesComerciales.DECIMALES),
            }
            for mes, total in sorted(por_mes.items())
        ]