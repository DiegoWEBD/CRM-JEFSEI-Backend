from psycopg.rows import DictRow

from app.aplicacion.solicitud_cotizacion.dto.cotizacion_resumen import CotizacionResumen
from app.aplicacion.solicitud_cotizacion.dto.fila_panel_cotizaciones import (
    FilaPanelCotizaciones,
)


class DictRowFilaPanelCotizacionesAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_fila_panel_cotizaciones(self) -> FilaPanelCotizaciones:
        cotizaciones = self.row['cotizaciones'] or []

        return FilaPanelCotizaciones(
            id=self.row['id'],
            id_prospecto=self.row['id_prospecto'],
            id_proceso_comercial=self.row['id_proceso_comercial'],
            cliente=self.row['cliente'],
            linea_seguro=self.row['linea_seguro'],
            ejecutivo_comercial=self.row['ejecutivo_comercial'],
            prioridad=self.row['prioridad'],
            fecha=self.row['fecha'],
            cantidad_cotizaciones=self.row['cantidad_cotizaciones'],
            vencimiento_mas_proximo=self.row['vencimiento_mas_proximo'],
            estado=self.row['estado'],
            tiene_estudio=self.row['tiene_estudio'],
            id_estudio=self.row['id_estudio'],
            cotizaciones=[
                CotizacionResumen(
                    id=cotizacion['id'],
                    company=cotizacion['company'],
                    prima_neta=cotizacion['prima_neta'],
                    prima_bruta=cotizacion['prima_bruta'],
                    fecha_vencimiento=cotizacion['fecha_vencimiento'],
                    estado=cotizacion['estado'],
                )
                for cotizacion in cotizaciones
            ],
        )
