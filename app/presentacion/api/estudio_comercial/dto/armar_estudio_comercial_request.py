from pydantic import BaseModel


class ArmarEstudioComercialRequest(BaseModel):
    monto_asegurado_actual: float
    infraseguro_primer_ejemplo: float
    infraseguro_segundo_ejemplo: float
    metros_cuadrados_construidos: float
    valor_uf_por_metro_cuadrado: float
    porcentaje_depreciacion: float
    cantidad_cuotas: int
    porcentaje_bienes_espacios_comunes: float