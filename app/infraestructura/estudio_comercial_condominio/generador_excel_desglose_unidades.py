from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.desglose_unidades.desglose_unidad import DesgloseUnidad
from app.dominio.estudio_comercial.desglose_unidades.totales_prima import TotalesPrima
from app.infraestructura.lib.estilo_excel import (
    COLORES_GRUPO,
    COLOR_REFERENCIA,
    COLOR_TOTAL,
    FORMATO_MONTO_CLP,
    FORMATO_MONTO_UF,
    FORMATO_PRORRATEO,
    escribir_celda,
    escribir_encabezado,
    escribir_grupo,
    escribir_linea_informativa,
    escribir_titulo,
)

HOJA_PRORRATEO = 'Prorrateo metros cuadrados'
HOJA_DESGLOSE = 'Desglose cotizaciones'

# Hoja «Prorrateo metros cuadrados»
COLUMNAS_PRORRATEO = (
    'Unidad',
    'Prorrateo (m²)',
    'Monto de reconstrucción (UF)',
    'Monto asegurado sugerido (UF)',
)

# Hoja «Desglose cotizaciones»
COLUMNAS_COMPARTIDAS = (
    'Unidad',
    'Monto asegurado (UF)',
    'Prorrateo por monto asegurado',
)

COLUMNAS_COTIZACION = (
    'Prima bruta (UF)',
    'Valor cuota (UF)',
    'Valor cuota (CLP)',
)

ETIQUETA_TOTALES = 'TOTAL'
ETIQUETA_REFERENCIA = 'TOTALES COTIZACIÓN (referencia)'

FILA_TITULO = 1
FILA_INFORMACION = 2
FILA_RESUMEN = 3
FILA_VACIA = 4

# (cotizacion, totales de referencia, desglose por unidad, cuota referencia UF, cuota referencia CLP)
DetalleDesglose = tuple[Cotizacion, TotalesPrima, list[DesgloseUnidad], float, float]


class GeneradorExcelDesgloseUnidades:
    """Genera el Excel con el desglose por unidad de las cotizaciones de una solicitud.

    Dos hojas: «Prorrateo metros cuadrados» (alícuota, monto de reconstrucción y
    monto asegurado sugerido por unidad) y «Desglose cotizaciones» (monto
    asegurado, prorrateo por monto asegurado y, por cada cotización, la prima
    bruta repartida junto al valor de la cuota en UF y en pesos de cada unidad).
    """

    def __init__(self, carpeta_base: str = 'documentos/estudios') -> None:
        self.carpeta_base = Path(carpeta_base)

    def generar(
        self,
        id_solicitud: int,
        datos: list[DetalleDesglose],
        encabezado: dict,
    ) -> str:
        nombre = f'desglose_unidades_solicitud_{id_solicitud}'
        carpeta = self.carpeta_base / nombre
        carpeta.mkdir(parents=True, exist_ok=True)

        libro = Workbook()

        hoja_prorrateo = libro.active
        hoja_prorrateo.title = HOJA_PRORRATEO
        self.__armar_hoja_prorrateo(hoja_prorrateo, datos, encabezado)

        hoja_desglose = libro.create_sheet(HOJA_DESGLOSE)
        self.__armar_hoja_desglose(hoja_desglose, datos, encabezado)

        ruta = carpeta / f'{nombre}.xlsx'
        libro.save(ruta)

        return str(ruta)

    # ------------------------------------------------------------------
    # Hoja «Prorrateo metros cuadrados»
    # ------------------------------------------------------------------

    def __armar_hoja_prorrateo(self, hoja, datos: list[DetalleDesglose], encabezado: dict) -> None:
        cantidad_columnas = len(COLUMNAS_PRORRATEO)
        self.__escribir_bloque_encabezado(hoja, encabezado, cantidad_columnas)

        fila_encabezados = FILA_VACIA + 1
        for columna, texto in enumerate(COLUMNAS_PRORRATEO, start=1):
            escribir_encabezado(hoja, fila_encabezados, columna, texto)

        unidades = datos[0][2] if datos else []
        fila = fila_encabezados + 1

        for indice, unidad in enumerate(unidades):
            self.__escribir_fila_prorrateo(hoja, fila + indice, unidad, indice)

        self.__escribir_totales_prorrateo(hoja, fila + len(unidades), unidades)

        hoja.freeze_panes = hoja.cell(row=fila_encabezados + 1, column=1)
        self.__ajustar_anchos(hoja, cantidad_columnas, (18, 18, 26, 26))

    def __escribir_fila_prorrateo(self, hoja, fila: int, unidad: DesgloseUnidad, indice: int) -> None:
        relleno = 'F7F9FC' if indice % 2 == 0 else None

        escribir_celda(hoja, fila, 1, unidad.identificador_unidad, negrita=True, color_relleno=relleno)
        escribir_celda(hoja, fila, 2, unidad.prorrateo, FORMATO_PRORRATEO, color_relleno=relleno)
        escribir_celda(hoja, fila, 3, unidad.monto_reconstruccion, FORMATO_MONTO_UF, color_relleno=relleno)
        escribir_celda(hoja, fila, 4, unidad.monto_asegurado_sugerido, FORMATO_MONTO_UF, color_relleno=relleno)

    def __escribir_totales_prorrateo(self, hoja, fila: int, unidades: list[DesgloseUnidad]) -> None:
        escribir_celda(hoja, fila, 1, ETIQUETA_TOTALES, negrita=True, color_relleno=COLOR_TOTAL)
        escribir_celda(
            hoja, fila, 2, round(sum(u.prorrateo or 0.0 for u in unidades), 9),
            FORMATO_PRORRATEO, negrita=True, color_relleno=COLOR_TOTAL,
        )
        escribir_celda(
            hoja, fila, 3, round(sum(u.monto_reconstruccion or 0.0 for u in unidades), 2),
            FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_TOTAL,
        )
        escribir_celda(
            hoja, fila, 4, round(sum(u.monto_asegurado_sugerido or 0.0 for u in unidades), 2),
            FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_TOTAL,
        )

    # ------------------------------------------------------------------
    # Hoja «Desglose cotizaciones»
    # ------------------------------------------------------------------

    def __armar_hoja_desglose(self, hoja, datos: list[DetalleDesglose], encabezado: dict) -> None:
        cantidad_compartidas = len(COLUMNAS_COMPARTIDAS)
        cantidad_columnas = cantidad_compartidas + len(datos) * len(COLUMNAS_COTIZACION)

        self.__escribir_bloque_encabezado(hoja, encabezado, cantidad_columnas)

        fila_grupos = FILA_VACIA + 1
        fila_encabezados = fila_grupos + 1

        escribir_grupo(
            hoja, fila_grupos, 1, cantidad_compartidas, 'Unidades', COLORES_GRUPO[0]
        )

        for indice, (cotizacion, _, _, _, _) in enumerate(datos):
            inicio = cantidad_compartidas + 1 + indice * len(COLUMNAS_COTIZACION)
            fin = inicio + len(COLUMNAS_COTIZACION) - 1
            escribir_grupo(
                hoja,
                fila_grupos,
                inicio,
                fin,
                cotizacion.company.nombre.upper(),
                COLORES_GRUPO[(indice + 1) % len(COLORES_GRUPO)],
            )

        encabezados = list(COLUMNAS_COMPARTIDAS)
        for _ in datos:
            encabezados.extend(COLUMNAS_COTIZACION)

        for columna, texto in enumerate(encabezados, start=1):
            escribir_encabezado(hoja, fila_encabezados, columna, texto)

        unidades = datos[0][2] if datos else []
        fila = fila_encabezados + 1

        for indice, unidad in enumerate(unidades):
            filas_cotizacion = [desglose[indice] for _, _, desglose, _, _ in datos]
            self.__escribir_fila_unidad(hoja, fila + indice, unidad, filas_cotizacion, indice)

        fila_totales = fila + len(unidades)
        self.__escribir_fila_totales(hoja, fila_totales, datos)
        self.__escribir_fila_referencia(hoja, fila_totales + 1, datos)

        hoja.freeze_panes = hoja.cell(row=fila_encabezados + 1, column=1)
        self.__ajustar_anchos(hoja, cantidad_columnas, (18, 22, 26))

    def __escribir_fila_unidad(
        self,
        hoja,
        fila: int,
        unidad: DesgloseUnidad,
        filas_cotizacion: list[DesgloseUnidad],
        indice: int,
    ) -> None:
        relleno = 'F7F9FC' if indice % 2 == 0 else None

        escribir_celda(hoja, fila, 1, unidad.identificador_unidad, negrita=True, color_relleno=relleno)
        escribir_celda(hoja, fila, 2, unidad.monto_asegurado_sugerido, FORMATO_MONTO_UF, color_relleno=relleno)
        escribir_celda(hoja, fila, 3, unidad.prorrateo_pago, FORMATO_PRORRATEO, color_relleno=relleno)

        columna = len(COLUMNAS_COMPARTIDAS) + 1
        for fila_cotizacion in filas_cotizacion:
            escribir_celda(hoja, fila, columna, fila_cotizacion.prima_bruta, FORMATO_MONTO_UF, color_relleno=relleno)
            escribir_celda(hoja, fila, columna + 1, fila_cotizacion.valor_cuota_uf, FORMATO_MONTO_UF, color_relleno=relleno)
            escribir_celda(hoja, fila, columna + 2, fila_cotizacion.valor_cuota_pesos, FORMATO_MONTO_CLP, color_relleno=relleno)
            columna += len(COLUMNAS_COTIZACION)

    def __escribir_fila_totales(self, hoja, fila: int, datos: list[DetalleDesglose]) -> None:
        unidades = datos[0][2] if datos else []

        escribir_celda(hoja, fila, 1, ETIQUETA_TOTALES, negrita=True, color_relleno=COLOR_TOTAL)
        escribir_celda(
            hoja, fila, 2, round(sum(u.monto_asegurado_sugerido or 0.0 for u in unidades), 2),
            FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_TOTAL,
        )
        escribir_celda(
            hoja, fila, 3, round(sum(u.prorrateo_pago or 0.0 for u in unidades), 9),
            FORMATO_PRORRATEO, negrita=True, color_relleno=COLOR_TOTAL,
        )

        columna = len(COLUMNAS_COMPARTIDAS) + 1
        for _, _, desglose, _, _ in datos:
            escribir_celda(
                hoja, fila, columna, round(sum(u.prima_bruta for u in desglose), 2),
                FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_TOTAL,
            )
            escribir_celda(
                hoja, fila, columna + 1, round(sum(u.valor_cuota_uf or 0.0 for u in desglose), 2),
                FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_TOTAL,
            )
            escribir_celda(
                hoja, fila, columna + 2, sum(u.valor_cuota_pesos or 0 for u in desglose),
                FORMATO_MONTO_CLP, negrita=True, color_relleno=COLOR_TOTAL,
            )
            columna += len(COLUMNAS_COTIZACION)

    def __escribir_fila_referencia(self, hoja, fila: int, datos: list[DetalleDesglose]) -> None:
        for columna in range(1, len(COLUMNAS_COMPARTIDAS) + 1):
            escribir_celda(
                hoja, fila, columna,
                ETIQUETA_REFERENCIA if columna == 1 else None,
                negrita=True, color_relleno=COLOR_REFERENCIA,
            )

        columna = len(COLUMNAS_COMPARTIDAS) + 1
        for _, totales, _, cuota_referencia_uf, cuota_referencia_pesos in datos:
            escribir_celda(
                hoja, fila, columna, totales.prima_bruta,
                FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_REFERENCIA,
            )
            escribir_celda(
                hoja, fila, columna + 1, cuota_referencia_uf,
                FORMATO_MONTO_UF, negrita=True, color_relleno=COLOR_REFERENCIA,
            )
            escribir_celda(
                hoja, fila, columna + 2, cuota_referencia_pesos,
                FORMATO_MONTO_CLP, negrita=True, color_relleno=COLOR_REFERENCIA,
            )
            columna += len(COLUMNAS_COTIZACION)

    # ------------------------------------------------------------------
    # Comunes
    # ------------------------------------------------------------------

    def __escribir_bloque_encabezado(self, hoja, encabezado: dict, cantidad_columnas: int) -> None:
        escribir_titulo(hoja, FILA_TITULO, 'Desglose por unidad', cantidad_columnas)

        cliente = encabezado.get('cliente') or '—'
        id_solicitud = encabezado.get('id_solicitud')
        fecha = encabezado.get('fecha')
        texto_fecha = fecha.strftime('%d-%m-%Y') if isinstance(fecha, datetime) else str(fecha or '—')

        escribir_linea_informativa(
            hoja,
            FILA_INFORMACION,
            f'Cliente: {cliente}   ·   Solicitud N° {id_solicitud}   ·   Generado: {texto_fecha}',
            cantidad_columnas,
        )

        escribir_linea_informativa(
            hoja,
            FILA_RESUMEN,
            (
                f'Unidades: {encabezado.get("cantidad_unidades", 0)}'
                f'   ·   Monto asegurado sugerido total: {self.__numero(encabezado.get("monto_asegurado_sugerido_total"))} UF'
                f'   ·   Cuotas: {encabezado.get("cantidad_cuotas", 0)}'
                f'   ·   Valor UF: ${self.__numero(encabezado.get("valor_uf"), decimales=0)}'
            ),
            cantidad_columnas,
        )

    @staticmethod
    def __numero(valor, decimales: int = 2) -> str:
        if valor is None:
            return '—'
        return f'{valor:,.{decimales}f}'.replace(',', '.')

    @staticmethod
    def __ajustar_anchos(hoja, cantidad_columnas: int, anchos: tuple[int, ...]) -> None:
        for columna in range(1, cantidad_columnas + 1):
            hoja.column_dimensions[get_column_letter(columna)].width = anchos[
                min(columna - 1, len(anchos) - 1)
            ]
