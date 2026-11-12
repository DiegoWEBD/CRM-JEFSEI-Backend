from dataclasses import dataclass

ESTADOS_SOLICITUDES = (
    'informacion_incompleta',
    'listas_para_cotizar',
    'cotizaciones_emitidas',
    'estudios_emitidos',
)

PRIORIDADES_SOLICITUDES = ('normal', 'alta')


@dataclass
class FiltroSolicitudesCotizacion:
    texto_busqueda: str | None = None
    estado: str | None = None
    prioridad: str | None = None
    rut_usuario: str | None = None
    pagina: int = 1
    tamano_pagina: int = 10
