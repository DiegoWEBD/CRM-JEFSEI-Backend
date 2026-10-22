import unicodedata

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.celda_excel import CeldaExcel

# Señales orientativas para sugerir la fila de encabezados y las columnas.
# No son reglas definitivas: el usuario puede seleccionar cualquier columna.
TERMINOS_IDENTIFICADOR = (
    'unidad',
    'unidades',
    'departamento',
    'departamentos',
    'depto',
    'deptos',
    'oficina',
    'oficinas',
    'numero',
    'numeros',
    'nro',
    'n',
    'identificador',
    'identificadores',
    'casa',
    'casas',
    'local',
    'locales',
)

TERMINOS_PRORRATEO = (
    'alicuota',
    'alicuotas',
    'prorrateo',
    'prorrateos',
    'porcentaje',
    'porcentajes',
    'participacion',
    'participaciones',
    'coeficiente',
    'coeficientes',
)

# Máxima cantidad de filas inspeccionadas para sugerir la fila de encabezados.
FILAS_DETECCION = 10


def normalizar_texto_encabezado(texto: str) -> str:
    """Minúsculas, sin acentos ni puntos, y espacios colapsados."""

    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.lower()
    texto = texto.replace('º', '').replace('°', '').replace('.', ' ')
    texto = ' '.join(texto.split())
    return texto.strip()


def _coincide(texto_normalizado: str, terminos: tuple[str, ...]) -> bool:
    for termino in terminos:
        if texto_normalizado == termino:
            return True
        # Los términos cortos solo coinciden exactos, para no confundir
        # "N.º bodega" con el término "n".
        if len(termino) >= 4 and texto_normalizado.startswith(termino + ' '):
            return True
    return False


class SugerenciasEncabezados:
    """Fila de encabezados y columnas candidatas, en numeración de Excel (1-based)."""

    def __init__(
        self,
        fila_encabezados: int | None,
        columna_identificador: int | None,
        columna_prorrateo: int | None,
        columnas_identificador_candidatas: list[int],
        columnas_prorrateo_candidatas: list[int],
    ) -> None:
        self.fila_encabezados = fila_encabezados
        self.columna_identificador = columna_identificador
        self.columna_prorrateo = columna_prorrateo
        self.columnas_identificador_candidatas = columnas_identificador_candidatas
        self.columnas_prorrateo_candidatas = columnas_prorrateo_candidatas

    def to_dict(self) -> dict:
        return {
            'fila_encabezados': self.fila_encabezados,
            'columna_identificador': self.columna_identificador,
            'columna_prorrateo': self.columna_prorrateo,
            'columnas_identificador_candidatas': self.columnas_identificador_candidatas,
            'columnas_prorrateo_candidatas': self.columnas_prorrateo_candidatas,
        }


def detectar_encabezados(filas: list[list[CeldaExcel]]) -> SugerenciasEncabezados:
    """Sugiere fila de encabezados y columnas a partir de coincidencias normalizadas.

    `filas` comienza en la fila 1 de la hoja y cada elemento es una fila de
    celdas en orden de columna (columna 1 en el índice 0).
    """

    coincidencias_identificador: dict[int, list[int]] = {}
    coincidencias_prorrateo: dict[int, list[int]] = {}

    for indice_fila, fila in enumerate(filas[:FILAS_DETECCION]):
        columnas_identificador: list[int] = []
        columnas_prorrateo: list[int] = []

        for indice_columna, celda in enumerate(fila):
            if not isinstance(celda.valor, str):
                continue

            texto = normalizar_texto_encabezado(celda.valor)

            if _coincide(texto, TERMINOS_IDENTIFICADOR):
                columnas_identificador.append(indice_columna + 1)
            if _coincide(texto, TERMINOS_PRORRATEO):
                columnas_prorrateo.append(indice_columna + 1)

        if columnas_identificador:
            coincidencias_identificador[indice_fila + 1] = columnas_identificador
        if columnas_prorrateo:
            coincidencias_prorrateo[indice_fila + 1] = columnas_prorrateo

    filas_candidatas = [
        fila
        for fila in sorted(set(coincidencias_identificador) | set(coincidencias_prorrateo))
        if fila in coincidencias_identificador and fila in coincidencias_prorrateo
    ]

    if filas_candidatas:
        fila_encabezados = filas_candidatas[0]
    else:
        filas_con_algo = sorted(set(coincidencias_identificador) | set(coincidencias_prorrateo))
        fila_encabezados = filas_con_algo[0] if filas_con_algo else None

    if fila_encabezados is None:
        return SugerenciasEncabezados(None, None, None, [], [])

    columnas_identificador = coincidencias_identificador.get(fila_encabezados, [])
    columnas_prorrateo = coincidencias_prorrateo.get(fila_encabezados, [])

    columna_identificador = columnas_identificador[0] if len(columnas_identificador) == 1 else None
    columna_prorrateo = columnas_prorrateo[0] if len(columnas_prorrateo) == 1 else None

    return SugerenciasEncabezados(
        fila_encabezados,
        columna_identificador,
        columna_prorrateo,
        columnas_identificador,
        columnas_prorrateo,
    )
