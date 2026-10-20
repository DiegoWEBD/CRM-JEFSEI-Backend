import math
import unicodedata

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.problema_alicuota import (
    SEVERIDAD_ERROR,
    ProblemaAlicuota,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota

# Palabras que delatan filas de totales o subtotales dentro del rango.
TERMINOS_FILA_TOTAL = (
    'total',
    'totales',
    'total general',
    'totales generales',
    'suma',
    'sumatoria',
    'subtotal',
    'subtotales',
)


def normalizar_clave_identificador(identificador: str) -> str:
    """Normalización conservadora para comparar identificadores.

    Solo colapsa espacios y unifica mayúsculas: no altera el identificador
    que se muestra ni se persiste.
    """

    texto = unicodedata.normalize('NFD', identificador)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return ' '.join(texto.split()).casefold()


def es_fila_de_totales(identificador: str) -> bool:
    clave = normalizar_clave_identificador(identificador)
    return clave in TERMINOS_FILA_TOTAL


def validar_unidades(unidades: list[UnidadAlicuota]) -> list[ProblemaAlicuota]:
    """Valida las unidades listas para persistir (reconfirmación del servidor)."""

    problemas: list[ProblemaAlicuota] = []

    if not unidades:
        problemas.append(ProblemaAlicuota(None, 'unidades', 'No hay unidades importables'))
        return problemas

    filas_por_clave: dict[str, int] = {}

    for unidad in unidades:
        identificador = unidad.identificador_unidad

        if not identificador or not identificador.strip():
            problemas.append(ProblemaAlicuota(
                unidad.fila_origen,
                'identificador_unidad',
                'El identificador de la unidad está vacío',
            ))
            continue

        clave = normalizar_clave_identificador(identificador)

        if clave in filas_por_clave:
            problemas.append(ProblemaAlicuota(
                unidad.fila_origen,
                'identificador_unidad',
                f'Identificador duplicado (también en la fila {filas_por_clave[clave]})',
            ))
        else:
            filas_por_clave[clave] = unidad.fila_origen

        if (
            unidad.prorrateo is None
            or not math.isfinite(unidad.prorrateo)
            or unidad.prorrateo < 0
            or unidad.prorrateo > 1
        ):
            problemas.append(ProblemaAlicuota(
                unidad.fila_origen,
                'prorrateo',
                'El prorrateo debe ser una fracción decimal entre 0 y 1',
            ))

        if unidad.fila_origen is None or unidad.fila_origen < 1:
            problemas.append(ProblemaAlicuota(
                unidad.fila_origen,
                'fila_origen',
                'La fila de origen no es válida',
            ))

    return problemas
