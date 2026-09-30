"""Redacción recursiva de datos sensibles antes de persistirlos.

Se aplica a datos_antes, datos_despues, cambios y metadata. La redacción es
defensiva a propósito: aunque un endpoint pase un dict con un JWT adentro, la
auditoría no lo va a guardar.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.dominio.auditoria.campos_sensibles import CAMPOS_SENSIBLES, VALOR_REDACTADO


def _es_sensible(clave: str) -> bool:
    return clave.strip().lower() in CAMPOS_SENSIBLES


def redactar(valor: Any, clave: str | None = None) -> Any:
    """Devuelve una copia serializable con los campos sensibles reemplazados."""
    if clave is not None and _es_sensible(clave):
        return VALOR_REDACTADO

    if isinstance(valor, dict):
        return {k: redactar(v, str(k)) for k, v in valor.items()}

    if isinstance(valor, (list, tuple, set)):
        return [redactar(v) for v in valor]

    if isinstance(valor, (datetime, date)):
        return valor.isoformat()

    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, UUID):
        return str(valor)

    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor

    # Objetos con __dict__: se serializa por atributos en vez de perderlos.
    if hasattr(valor, '__dict__'):
        return redactar(dict(vars(valor)))

    return str(valor)


def serializar(valor: Any) -> str | None:
    """Redacta y serializa a JSON. Pensado para depuración y tests."""
    if valor is None:
        return None
    return json.dumps(redactar(valor), ensure_ascii=False, default=str)


def preparar_json(valor: Any) -> dict | None:
    """Devuelve la estructura ya redactada y lista para el JSONB.

    Si el snapshot excede ``AUDIT_MAX_SNAPSHOT_BYTES`` se reemplaza por un
    marcador en vez de recortarse, para no dejar JSON inválido ni inflar el
    JSONB con un informe completo (§42).
    """
    if valor is None:
        return None

    preparado = redactar(valor)
    if not isinstance(preparado, dict):
        preparado = {'valor': preparado}

    limite = settings.AUDIT_MAX_SNAPSHOT_BYTES
    if limite:
        texto = json.dumps(preparado, ensure_ascii=False, default=str)
        if len(texto.encode('utf-8')) > limite:
            return {
                '__truncado__': True,
                '__bytes_originales__': len(texto.encode('utf-8')),
            }

    return preparado
