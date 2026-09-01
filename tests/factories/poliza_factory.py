from datetime import datetime, timezone


def crear_poliza_dict(
    id: int = 1,
    numero: str = "POL-001",
    id_proceso_comercial: int | None = None,
    id_company_seguros: int = 1,
    id_producto: int = 1,
    id_linea_negocio: int = 1,
    estado: str = "VIGENTE",
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    prima_anual: float = 1000.0,
    monto_asegurado: float = 100000.0,
) -> dict:
    if fecha_inicio is None:
        fecha_inicio = datetime.now(tz=timezone.utc)
    if fecha_fin is None:
        fecha_fin = datetime.now(tz=timezone.utc)
    return {
        "id": id,
        "numero": numero,
        "id_proceso_comercial": id_proceso_comercial,
        "id_company_seguros": id_company_seguros,
        "id_producto": id_producto,
        "id_linea_negocio": id_linea_negocio,
        "estado": estado,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "prima_anual": prima_anual,
        "monto_asegurado": monto_asegurado,
    }
