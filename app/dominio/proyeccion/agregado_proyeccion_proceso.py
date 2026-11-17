from dataclasses import dataclass


@dataclass(frozen=True)
class AgregadoProyeccionProceso:
    """Primas de proyección calculadas para un proceso comercial.

    `prima_esperada` es None cuando el proceso no tiene probabilidad de
    cierre (ni del ejecutivo ni del estado), igual que el cálculo
    histórico por proceso.
    """

    prima_cotizada: float
    prima_potencial_estimada: float
    prima_esperada: float | None
