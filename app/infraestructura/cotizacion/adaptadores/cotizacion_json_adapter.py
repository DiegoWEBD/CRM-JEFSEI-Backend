import base64
from datetime import datetime, timezone
import os

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.servicio_estado_cotizacion import (
    calcular_estado_cotizacion,
)
from app.presentacion.api.cotizacion.dto.cotizacion_json import CotizacionJson
from app.presentacion.api.cotizacion.dto.estado_cotizacion import EstadoCotizacion


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

        estado = EstadoCotizacion(
            calcular_estado_cotizacion(
                self.cotizacion.fecha_emision,
                self.cotizacion.fecha_vencimiento,
                datetime.now(tz=timezone.utc),
            )
        )

        return CotizacionJson(
            id=self.cotizacion.id,
            id_company=self.cotizacion.company.id,
            monto_total_asegurado=self.cotizacion.monto_total_asegurado,
            tasa_afecta=self.cotizacion.tasa_afecta,
            tasa_excenta=self.cotizacion.tasa_excenta,
            tasa_politica=self.cotizacion.tasa_politica,
            asistencia_afecta=self.cotizacion.asistencia_afecta,
            asistencia_excenta=self.cotizacion.asistencia_excenta,
            prima_afecta=self.cotizacion.prima_afecta,
            prima_excenta=self.cotizacion.prima_excenta,
            prima_neta=self.cotizacion.prima_neta,
            prima_iva=self.cotizacion.prima_iva,
            prima_bruta=self.cotizacion.prima_bruta,
            company=self.cotizacion.company.nombre,
            fecha_emision=self.cotizacion.fecha_emision.isoformat(),
            fecha_vencimiento=self.cotizacion.fecha_vencimiento.isoformat(),
            estado=estado,
            nombre_archivo=self.cotizacion.nombre_archivo,
            archivo_base64=archivo_base64
        )