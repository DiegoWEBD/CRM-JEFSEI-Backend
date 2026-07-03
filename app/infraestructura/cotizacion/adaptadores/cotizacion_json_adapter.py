import base64
import os

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.presentacion.api.cotizacion.dto.cotizacion_json import CotizacionJson


class CotizacionJsonAdapter:

    RUTA_BASE = 'documentos/cotizaciones'

    def __init__(self, cotizacion: Cotizacion) -> None:
        self.cotizacion = cotizacion

    def to_cotizacion_json(self) -> CotizacionJson:

        if self.cotizacion.id is None:
            raise Exception('Cotización inválida, indique id')

        archivo_base64 = None

        if self.cotizacion.nombre_archivo:
            ruta = os.path.join(self.RUTA_BASE, self.cotizacion.nombre_archivo)
            if os.path.exists(ruta):
                with open(ruta, 'rb') as f:
                    archivo_bytes = f.read()
                archivo_base64 = base64.b64encode(archivo_bytes).decode('utf-8')

        return CotizacionJson(
            id=self.cotizacion.id,
            monto_total_asegurado=self.cotizacion.monto_total_asegurado,
            tasa_afecta=self.cotizacion.tasa_afecta,
            tasa_excenta=self.cotizacion.tasa_excenta,
            tasa_politica=self.cotizacion.tasa_politica,
            prima_adicional_asistencia=self.cotizacion.prima_adicional_asistencia,
            company=self.cotizacion.company.nombre,
            fecha_emision=self.cotizacion.fecha_emision.isoformat(),
            fecha_vencimiento=self.cotizacion.fecha_vencimiento.isoformat(),
            nombre_archivo=self.cotizacion.nombre_archivo,
            archivo_base64=archivo_base64
        )