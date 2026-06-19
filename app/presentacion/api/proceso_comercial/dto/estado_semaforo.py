from enum import Enum


class EstadoSemaforo(Enum):
    VERDE = 'VERDE'
    AMARILLO = 'AMARILLO'
    ROJO = 'ROJO'
    NO_APLICA = 'NO_APLICA'