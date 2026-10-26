from pydantic import BaseModel


class ActualizarUnidadAlicuotaRequest(BaseModel):
    """Configuración de procesamiento de una unidad de la alícuota.

    Los campos son opcionales: solo se aplica lo informado en la petición.
    `monto_asegurado_personalizado: null` (explícito) vuelve la unidad al
    monto asegurado sugerido por el sistema.
    """

    descartada: bool | None = None
    monto_asegurado_personalizado: float | None = None
