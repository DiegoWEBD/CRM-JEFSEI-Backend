from decimal import Decimal, InvalidOperation

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.celda_excel import CeldaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.interpretacion_prorrateo import (
    ResultadoInterpretacionProrrateo,
    interpretar_prorrateo_columna,
    normalizar_prorrateo,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.problema_alicuota import (
    SEVERIDAD_ERROR,
    ProblemaAlicuota,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.validador_alicuotas import (
    es_fila_de_totales,
    normalizar_clave_identificador,
)

ESTADO_VALIDO = 'valido'
ESTADO_ERROR = 'error'
ESTADO_PENDIENTE = 'pendiente'

ERRORES_EXCEL = (
    '#DIV/0!',
    '#N/A',
    '#VALUE!',
    '#REF!',
    '#NUM!',
    '#NULL!',
    '#SPILL!',
    '#CALC!',
    '#GETTING_DATA',
)

CAMPO_IDENTIFICADOR = 'identificador_unidad'
CAMPO_PRORRATEO = 'prorrateo'


class FilaRango:
    """Fila del rango seleccionado con las dos celdas relevantes."""

    def __init__(self, numero_fila: int, celda_identificador: CeldaExcel, celda_prorrateo: CeldaExcel) -> None:
        self.numero_fila = numero_fila
        self.celda_identificador = celda_identificador
        self.celda_prorrateo = celda_prorrateo


class RegistroAlicuotaExtraido:

    def __init__(
        self,
        fila_origen: int,
        identificador_unidad: str,
        prorrateo_original,
        prorrateo: Decimal | None,
        estado: str,
        problemas: list[ProblemaAlicuota],
    ) -> None:
        self.fila_origen = fila_origen
        self.identificador_unidad = identificador_unidad
        self.prorrateo_original = prorrateo_original
        self.prorrateo = prorrateo
        self.estado = estado
        self.problemas = problemas

    def to_dict(self) -> dict:
        return {
            'fila_origen': self.fila_origen,
            'identificador_unidad': self.identificador_unidad,
            'prorrateo_original': self.prorrateo_original,
            'prorrateo': float(self.prorrateo) if self.prorrateo is not None else None,
            'estado': self.estado,
            'problemas': [problema.to_dict() for problema in self.problemas],
        }


class ResultadoExtraccionAlicuotas:

    def __init__(
        self,
        registros: list[RegistroAlicuotaExtraido],
        problemas: list[ProblemaAlicuota],
        interpretacion: ResultadoInterpretacionProrrateo,
        suma_prorrateos: Decimal | None,
        tiene_errores_bloqueantes: bool,
        filas_excluidas: list[int],
    ) -> None:
        self.registros = registros
        self.problemas = problemas
        self.interpretacion = interpretacion
        self.suma_prorrateos = suma_prorrateos
        self.tiene_errores_bloqueantes = tiene_errores_bloqueantes
        self.filas_excluidas = filas_excluidas


def _como_identificador(valor) -> str:
    if valor is None:
        return ''
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def _parsear_prorrateo(celda: CeldaExcel) -> tuple[float | None, str | None]:
    """Devuelve (valor, mensaje_error). No interpreta valores ambiguos."""

    if celda.formula_sin_resultado:
        return None, (
            'La celda contiene una fórmula sin resultado calculado; '
            'proporcione un archivo con los valores calculados'
        )

    valor = celda.valor

    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, 'El valor de prorrateo está vacío'

    if isinstance(valor, bool):
        return None, 'El valor de prorrateo no es numérico'

    if isinstance(valor, (int, float)):
        return float(valor), None

    if isinstance(valor, str):
        texto = valor.strip()

        if texto.upper() in ERRORES_EXCEL:
            return None, f'La celda contiene un error de Excel ({texto})'

        if ',' in texto and '.' not in texto:
            texto = texto.replace(',', '.')

        try:
            return float(Decimal(texto)), None
        except (InvalidOperation, ValueError):
            return None, 'El valor de prorrateo no es numérico'

    return None, 'El valor de prorrateo no es numérico'


def extraer_registros(
    filas: list[FilaRango],
    interpretacion_confirmada: str | None = None,
) -> ResultadoExtraccionAlicuotas:
    """Extrae y valida los registros del rango seleccionado.

    Las filas de totales o subtotales se excluyen de los registros y se
    reportan como error para que el usuario corrija el rango. Los valores de
    prorrateo ambiguos no se normalizan sin confirmación explícita.
    """

    problemas_generales: list[ProblemaAlicuota] = []
    filas_excluidas: list[int] = []
    registros: list[RegistroAlicuotaExtraido] = []
    procesables: list[tuple[FilaRango, RegistroAlicuotaExtraido]] = []

    for fila in filas:
        identificador = _como_identificador(fila.celda_identificador.valor)

        if not identificador.strip():
            registro = RegistroAlicuotaExtraido(
                fila.numero_fila, '', fila.celda_prorrateo.valor, None, ESTADO_ERROR, []
            )
            problema = ProblemaAlicuota(
                fila.numero_fila, CAMPO_IDENTIFICADOR, 'El identificador de la unidad está vacío'
            )
            registro.problemas.append(problema)
            problemas_generales.append(problema)
            registros.append(registro)
            continue

        if es_fila_de_totales(identificador):
            filas_excluidas.append(fila.numero_fila)
            problemas_generales.append(ProblemaAlicuota(
                fila.numero_fila,
                CAMPO_IDENTIFICADOR,
                f'Posible fila de totales o subtotales ("{identificador}"); ajuste el rango de filas',
            ))
            continue

        registro = RegistroAlicuotaExtraido(
            fila.numero_fila, identificador, fila.celda_prorrateo.valor, None, ESTADO_VALIDO, []
        )
        registros.append(registro)
        procesables.append((fila, registro))

    # Identificadores duplicados (normalización conservadora)
    filas_por_clave: dict[str, int] = {}

    for fila, registro in procesables:
        clave = normalizar_clave_identificador(registro.identificador_unidad)

        if clave in filas_por_clave:
            problema = ProblemaAlicuota(
                fila.numero_fila,
                CAMPO_IDENTIFICADOR,
                f'Identificador duplicado (también en la fila {filas_por_clave[clave]})',
            )
            registro.problemas.append(problema)
            problemas_generales.append(problema)
        else:
            filas_por_clave[clave] = fila.numero_fila

    # Prorrateos
    valores: list[float] = []
    formatos: list[str | None] = []

    for fila, registro in procesables:
        valor, error = _parsear_prorrateo(fila.celda_prorrateo)

        if error is not None:
            problema = ProblemaAlicuota(fila.numero_fila, CAMPO_PRORRATEO, error)
            registro.problemas.append(problema)
            problemas_generales.append(problema)
            continue

        if valor < 0:
            problema = ProblemaAlicuota(
                fila.numero_fila, CAMPO_PRORRATEO, 'El valor de prorrateo no puede ser negativo'
            )
            registro.problemas.append(problema)
            problemas_generales.append(problema)
            continue

        registro.prorrateo_original = valor
        valores.append(valor)
        formatos.append(fila.celda_prorrateo.formato_numerico)

    interpretacion = interpretar_prorrateo_columna(valores, formatos, interpretacion_confirmada)

    for _, registro in procesables:
        if registro.problemas:
            registro.estado = ESTADO_ERROR
        elif interpretacion.requiere_confirmacion:
            registro.estado = ESTADO_PENDIENTE
        elif interpretacion.tipo is not None and isinstance(registro.prorrateo_original, (int, float)):
            registro.prorrateo = normalizar_prorrateo(registro.prorrateo_original, interpretacion.tipo)

    if interpretacion.requiere_confirmacion:
        suma_prorrateos = None
    else:
        suma_prorrateos = sum(
            (registro.prorrateo for registro in registros
             if registro.estado == ESTADO_VALIDO and registro.prorrateo is not None),
            Decimal('0'),
        )

    tiene_errores_bloqueantes = any(
        problema.severidad == SEVERIDAD_ERROR for problema in problemas_generales
    )

    return ResultadoExtraccionAlicuotas(
        registros=registros,
        problemas=problemas_generales,
        interpretacion=interpretacion,
        suma_prorrateos=suma_prorrateos,
        tiene_errores_bloqueantes=tiene_errores_bloqueantes,
        filas_excluidas=filas_excluidas,
    )
