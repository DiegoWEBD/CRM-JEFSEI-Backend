from pydantic import BaseModel


class ConfiguracionImportacionAlicuotas(BaseModel):
    """Configuración de mapeo elegida por el usuario sobre la hoja del Excel."""

    hoja: str
    fila_encabezados: int
    columna_identificador: int
    columna_prorrateo: int
    primera_fila: int
    ultima_fila: int
    interpretacion_prorrateo: str | None = None
