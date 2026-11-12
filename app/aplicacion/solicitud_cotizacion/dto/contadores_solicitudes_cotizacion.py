from dataclasses import dataclass


@dataclass
class ContadoresSolicitudesCotizacion:
    informacion_incompleta: int
    listas_para_cotizar: int
    cotizaciones_emitidas: int
    estudios_emitidos: int
