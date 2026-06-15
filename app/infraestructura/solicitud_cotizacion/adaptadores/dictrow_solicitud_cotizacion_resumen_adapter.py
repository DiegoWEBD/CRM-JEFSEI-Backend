from psycopg.rows import DictRow

from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import SolicitudCotizacionResumen


class DictRowSolicitudCotizacionResumenAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_solicitud_cotizacion_resumen(self) -> SolicitudCotizacionResumen:
        return SolicitudCotizacionResumen(
            id=self.row['id'],
            nombre_riesgo=self.row['nombre_riesgo'],
            informacion_completa=self.row['informacion_completa'],
            ejecutivo_comercial=self.row['ejecutivo_comercial'],
            tipo=self.row['tipo'],
            producto=self.row['producto'],
            prioridad=self.row['prioridad'],
            fecha=self.row['fecha'],
            cantidad_cotizaciones=self.row['cantidad_cotizaciones']
        )