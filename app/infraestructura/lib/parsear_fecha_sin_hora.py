from datetime import datetime
from zoneinfo import ZoneInfo


def parsear_fecha_sin_hora(fecha: str) -> datetime:
    return datetime.fromisoformat(fecha).replace(tzinfo=ZoneInfo('America/Santiago'))