from enum import Enum

class EstadoPoliza(Enum):
    REGISTRADA = 'REGISTRADA'
    VIGENTE = 'VIGENTE'
    POR_VENCER = 'POR_VENCER'
    VENCIDA = 'VENCIDA'
    CANCELADA = 'CANCELADA'