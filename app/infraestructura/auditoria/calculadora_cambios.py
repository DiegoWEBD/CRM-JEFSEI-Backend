"""Cálculo del diff entre el estado anterior y el posterior de un UPDATE (§35).

El diff es lo que permite reconstruir la modificación leyendo una sola fila, sin
guardar dos copias completas del recurso.
"""

from typing import Any

from app.infraestructura.auditoria.redactador import redactar

# Campos técnicos que cambian solos en cada escritura y no aportan a una
# investigación: guardarlos llenaría el diff de ruido.
CAMPOS_TECNICOS_IGNORADOS: frozenset[str] = frozenset({
    'created_at',
    'createdAt',
    'updated_at',
    'updatedAt',
    'fecha_actualizacion',
    'ultima_actualizacion',
})


def calculate_changes(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    ignorar: frozenset[str] = CAMPOS_TECNICOS_IGNORADOS,
) -> dict[str, Any]:
    """Devuelve ``{campo: {"antes": ..., "despues": ...}}`` sólo con lo que cambió.

    Redacta antes de comparar, para que un campo sensible no aparezca ni
    siquiera en el diff.
    """
    if before is None and after is None:
        return {}

    antes = redactar(before or {})
    despues = redactar(after or {})

    if not isinstance(antes, dict) or not isinstance(despues, dict):
        return {}

    cambios: dict[str, Any] = {}

    for campo in set(antes) | set(despues):
        if campo in ignorar:
            continue
        valor_antes = antes.get(campo)
        valor_despues = despues.get(campo)
        if valor_antes != valor_despues:
            cambios[campo] = {'antes': valor_antes, 'despues': valor_despues}

    return cambios
