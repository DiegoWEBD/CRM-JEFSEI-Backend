from datetime import datetime

# Cuántos días antes del vencimiento pasa a estado POR_VENCER.
INTERVALO_VENCIMIENTO_DIAS = 10


def calcular_estado_cotizacion(
    fecha_emision: datetime,
    fecha_vencimiento: datetime,
    ahora: datetime,
) -> str:
    """
    Clasifica una cotización según sus fechas relativas a `ahora`.

    Devuelve uno de los valores de EstadoCotizacion: 'REGISTRADA' si aún no se
    emite, 'POR_VENCER' si vence dentro de INTERVALO_VENCIMIENTO_DIAS días,
    'VIGENTE' si vence más allá de ese plazo y 'VENCIDA' si ya venció.
    """
    if fecha_emision > ahora:
        return 'REGISTRADA'

    if (
        fecha_vencimiento > ahora
        and (fecha_vencimiento - ahora).days <= INTERVALO_VENCIMIENTO_DIAS
    ):
        return 'POR_VENCER'

    if fecha_emision <= ahora and fecha_vencimiento > ahora:
        return 'VIGENTE'

    return 'VENCIDA'
