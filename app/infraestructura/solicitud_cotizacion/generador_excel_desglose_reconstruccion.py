from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad


FORMATO_MONTO = '#,##0.00'
FORMATO_PRORRATEO = '0.000000000'

HOJA_DESGLOSE = 'Desglose reconstrucción'

COLUMNAS = (
    'Unidad',
    'Prorrateo alícuota',
    'Prorrateo por monto asegurado',
    'Monto de reconstrucción (UF)',
    'Monto asegurado sugerido (UF)',
)

COLOR_GRUPO = 'FFF2CC'


class GeneradorExcelDesgloseReconstruccion:
    """Genera el Excel con el desglose de reconstrucción por unidad de una oportunidad.

    Una fila por unidad (prorrateos, monto de reconstrucción y monto asegurado
    sugerido) más una fila de totales.
    """

    def __init__(self, carpeta_base: str = 'documentos/estudios') -> None:
        self.carpeta_base = Path(carpeta_base)

    def generar(self, id_proceso_comercial: int, desglose: list[DesgloseReconstruccionUnidad]) -> str:
        nombre = f'desglose_reconstruccion_oportunidad_{id_proceso_comercial}'
        carpeta = self.carpeta_base / nombre
        carpeta.mkdir(parents=True, exist_ok=True)

        libro = Workbook()
        hoja = libro.active
        hoja.title = HOJA_DESGLOSE

        self.__escribir_grupo(hoja)
        self.__escribir_encabezados(hoja)

        fila = 3
        for indice, unidad in enumerate(desglose):
            self.__escribir_fila_unidad(hoja, fila + indice, unidad)

        self.__escribir_fila_totales(hoja, fila + len(desglose), desglose)

        ruta = carpeta / f'{nombre}.xlsx'
        libro.save(ruta)

        return str(ruta)

    def __escribir_grupo(self, hoja) -> None:
        celda = hoja.cell(row=1, column=1, value='Desglose de reconstrucción por unidad')
        hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLUMNAS))
        celda.font = Font(bold=True)
        celda.alignment = Alignment(horizontal='center')
        celda.fill = PatternFill(fill_type='solid', fgColor=COLOR_GRUPO)

    def __escribir_encabezados(self, hoja) -> None:
        for columna, encabezado in enumerate(COLUMNAS, start=1):
            celda = hoja.cell(row=2, column=columna, value=encabezado)
            celda.font = Font(bold=True)
            celda.alignment = Alignment(horizontal='center')

        for columna in range(1, len(COLUMNAS) + 1):
            hoja.column_dimensions[get_column_letter(columna)].width = 24

    def __escribir_fila_unidad(self, hoja, fila: int, unidad: DesgloseReconstruccionUnidad) -> None:
        valores = [
            unidad.identificador_unidad,
            unidad.prorrateo,
            unidad.prorrateo_pago,
            unidad.monto_reconstruccion,
            unidad.monto_asegurado_sugerido,
        ]
        formatos = [None, FORMATO_PRORRATEO, FORMATO_PRORRATEO, FORMATO_MONTO, FORMATO_MONTO]

        self.__escribir_fila(hoja, fila, valores, formatos)

    def __escribir_fila_totales(self, hoja, fila: int, desglose: list[DesgloseReconstruccionUnidad]) -> None:
        valores = [
            'TOTAL',
            round(sum(unidad.prorrateo for unidad in desglose), 9),
            round(sum(unidad.prorrateo_pago for unidad in desglose), 9),
            round(sum(unidad.monto_reconstruccion for unidad in desglose), 2),
            round(sum(unidad.monto_asegurado_sugerido for unidad in desglose), 2),
        ]
        formatos = [None, FORMATO_PRORRATEO, FORMATO_PRORRATEO, FORMATO_MONTO, FORMATO_MONTO]

        self.__escribir_fila(hoja, fila, valores, formatos, negrita=True)

    def __escribir_fila(self, hoja, fila: int, valores: list, formatos: list, negrita: bool = False) -> None:
        for columna, (valor, formato) in enumerate(zip(valores, formatos), start=1):
            celda = hoja.cell(row=fila, column=columna, value=valor)

            if negrita:
                celda.font = Font(bold=True)

            if formato is not None:
                celda.number_format = formato
