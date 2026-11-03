"""Cálculo y formato del SLA con precisión de horas (días decimales).

El transcurrido se mide en horas calendario (24/7) y se expresa como fracción
decimal de un día (ej: 13 h = 0.5417 días).  Nunca se trunca a días enteros
para calcular el consumo del plazo; el redondeo hacia abajo sólo se aplica al
momento de formatear el texto visible ('0 días 13 h').
"""

import math
from datetime import datetime

SEGUNDOS_POR_DIA = 86400.0
HORAS_POR_DIA = 24


def dias_decimales(desde: datetime, hasta: datetime) -> float:
    """Días transcurridos entre dos instantes como decimal (fracción de día)."""
    return (hasta - desde).total_seconds() / SEGUNDOS_POR_DIA


def formatear_dias_horas(valor: float | None) -> str:
    """Convierte días decimales a texto legible: '0 días 13 h'.

    - Días y horas se redondean hacia abajo (nunca promete tiempo de más).
    - Con horas en 0 se omite esa parte: '1 día', '10 días'.
    - `None` se muestra como '—'.
    """
    if valor is None:
        return '—'

    total_horas = math.floor(valor * HORAS_POR_DIA)
    dias, horas = divmod(total_horas, HORAS_POR_DIA)
    etiqueta_dias = f'{dias} {"día" if dias == 1 else "días"}'

    if horas == 0:
        return etiqueta_dias

    return f'{etiqueta_dias} {horas} h'
