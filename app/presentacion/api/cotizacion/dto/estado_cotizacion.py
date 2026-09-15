from enum import Enum

class EstadoCotizacion(Enum):
    REGISTRADA = 'REGISTRADA'
    VIGENTE = 'VIGENTE'
    POR_VENCER = 'POR_VENCER'
    VENCIDA = 'VENCIDA'