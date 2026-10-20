from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.deteccion_encabezados import (
    FILAS_DETECCION,
    detectar_encabezados,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.lector_alicuotas_excel import (
    LectorAlicuotasExcel,
)

MAX_CANTIDAD_FILAS_VISTA = 500
MAX_COLUMNAS_VISTA = 100


class AnalizarAlicuotasUseCase:
    """Primer paso del importador: hojas, vista previa y sugerencias."""

    def __init__(self, lector_excel: LectorAlicuotasExcel) -> None:
        self.lector_excel = lector_excel

    def ejecutar(self, contenido: bytes, hoja: str | None = None, inicio: int = 1, cantidad: int = 200) -> dict:
        hojas = self.lector_excel.obtener_hojas(contenido)

        if not hojas:
            raise DatoInvalidoException('El archivo no contiene hojas utilizables')

        if inicio < 1 or cantidad < 1:
            raise DatoInvalidoException('El rango de la vista previa no es válido')

        seleccionada = next((h for h in hojas if h.nombre == hoja), None) if hoja else hojas[0]

        if seleccionada is None:
            raise DatoInvalidoException(f'La hoja "{hoja}" no existe en el archivo')

        if seleccionada.filas < 1 or seleccionada.columnas < 1:
            raise DatoInvalidoException('La hoja seleccionada está vacía')

        columnas_vista = min(seleccionada.columnas, MAX_COLUMNAS_VISTA)
        columnas = list(range(1, columnas_vista + 1))

        fila_desde = min(inicio, seleccionada.filas)
        fila_hasta = min(inicio + cantidad - 1, seleccionada.filas)

        celdas = self.lector_excel.leer_bloque(
            contenido, seleccionada.nombre, fila_desde, fila_hasta, columnas
        )

        filas_deteccion = self.lector_excel.leer_bloque(
            contenido,
            seleccionada.nombre,
            1,
            min(FILAS_DETECCION, seleccionada.filas),
            columnas,
        )
        sugerencias = detectar_encabezados(filas_deteccion)

        return {
            'hojas': [h.to_dict() for h in hojas],
            'hoja_seleccionada': seleccionada.nombre,
            'filas': seleccionada.filas,
            'columnas': seleccionada.columnas,
            'vista_previa': {
                'fila_desde': fila_desde,
                'fila_hasta': fila_hasta,
                'columna_desde': 1,
                'columna_hasta': columnas_vista,
                'celdas': [
                    [
                        {'valor': celda.valor, 'formula_sin_resultado': celda.formula_sin_resultado}
                        for celda in fila
                    ]
                    for fila in celdas
                ],
            },
            'sugerencias': sugerencias.to_dict(),
        }
