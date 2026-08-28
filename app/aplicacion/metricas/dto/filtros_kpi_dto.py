from dataclasses import dataclass


@dataclass
class FiltrosKpiDto:
    year: int | None = None
    month: int | None = None
    rut_ejecutivo: str | None = None
    id_linea_negocio: int | None = None
    id_producto: int | None = None
    id_sucursal: int | None = None
