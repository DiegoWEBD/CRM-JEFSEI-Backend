from pydantic import BaseModel


class UnidadAlicuotaCambioRequest(BaseModel):
    """Configuración nueva de una unidad de la alícuota.

    Los campos son opcionales: solo se aplica lo informado en la petición.
    `monto_asegurado_personalizado: null` (explícito) vuelve la unidad al
    monto asegurado sugerido por el sistema.
    """

    id_unidad: int
    descartada: bool | None = None
    monto_asegurado_personalizado: float | None = None


class ActualizarUnidadesAlicuotaRequest(BaseModel):
    """Lote de unidades de la alícuota a modificar en una sola operación."""

    unidades: list[UnidadAlicuotaCambioRequest]
