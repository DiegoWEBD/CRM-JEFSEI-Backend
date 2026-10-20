from decimal import Decimal

from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException

# Representaciones posibles del prorrateo en el archivo original.
#
# - porcentaje_excel: celda con formato de porcentaje de Excel; almacena la
#   fracción (0,0085) y muestra 0,85 %.
# - valor_porcentual: número que representa directamente el porcentaje
#   (0,85 significa 0,85 %).
# - fraccion_decimal: fracción decimal del todo (0,0085 significa 0,85 %).
#
# El valor normalizado siempre es un porcentaje: 0,85 representa 0,85 %.
PORCENTAJE_EXCEL = 'porcentaje_excel'
VALOR_PORCENTUAL = 'valor_porcentual'
FRACCION_DECIMAL = 'fraccion_decimal'

TIPOS_INTERPRETACION_PRORRATEO = (PORCENTAJE_EXCEL, VALOR_PORCENTUAL, FRACCION_DECIMAL)

# Una fracción decimal de un todo no puede superar 1. Por encima de este
# umbral los valores solo pueden ser porcentaje directo.
LIMITE_FRACCION_DECIMAL = Decimal('1.01')

# Umbral para sugerir fracción decimal cuando la suma se acerca a 1.
TOLERANCIA_SUMA_UNO = Decimal('0.01')

# Por debajo de este valor individual la lectura como fracción es plausible.
UMBRAL_VALOR_PEQUENO = Decimal('0.01')


class ResultadoInterpretacionProrrateo:

    def __init__(self, tipo: str | None, requiere_confirmacion: bool, motivo: str | None = None) -> None:
        self.tipo = tipo
        self.requiere_confirmacion = requiere_confirmacion
        self.motivo = motivo

    def to_dict(self) -> dict:
        return {
            'tipo': self.tipo,
            'requiere_confirmacion': self.requiere_confirmacion,
            'motivo': self.motivo,
        }


def normalizar_prorrateo(valor: float, tipo: str) -> Decimal:
    """Devuelve el prorrateo como porcentaje (0,85 representa 0,85 %)."""

    if tipo not in TIPOS_INTERPRETACION_PRORRATEO:
        raise DatoInvalidoException(f'Interpretación de prorrateo desconocida: {tipo}')

    numero = Decimal(str(valor))

    if tipo in (PORCENTAJE_EXCEL, FRACCION_DECIMAL):
        return numero * 100

    return numero


def interpretar_prorrateo_columna(
    valores: list[float],
    formatos: list[str | None],
    interpretacion_confirmada: str | None = None,
) -> ResultadoInterpretacionProrrateo:
    """Interpreta la representación usada por la columna de prorrateo.

    Nunca asume en silencio una conversión: si el contexto no es concluyente
    devuelve `requiere_confirmacion=True` y el usuario debe confirmar la
    interpretación antes de normalizar.
    """

    if interpretacion_confirmada is not None:
        if interpretacion_confirmada not in TIPOS_INTERPRETACION_PRORRATEO:
            raise DatoInvalidoException(
                f'Interpretación de prorrateo desconocida: {interpretacion_confirmada}'
            )

        return ResultadoInterpretacionProrrateo(
            interpretacion_confirmada,
            False,
            'Interpretación confirmada por el usuario',
        )

    if not valores:
        return ResultadoInterpretacionProrrateo(None, False, 'No hay valores de prorrateo para interpretar')

    if formatos and all(f is not None and '%' in f for f in formatos):
        return ResultadoInterpretacionProrrateo(
            PORCENTAJE_EXCEL,
            False,
            'Las celdas usan formato de porcentaje de Excel',
        )

    suma = sum((Decimal(str(v)) for v in valores), Decimal('0'))

    if suma > LIMITE_FRACCION_DECIMAL:
        return ResultadoInterpretacionProrrateo(
            VALOR_PORCENTUAL,
            False,
            'La suma de los valores supera 1: no pueden ser fracciones de un todo',
        )

    if abs(suma - Decimal('1')) <= TOLERANCIA_SUMA_UNO:
        sugerido = FRACCION_DECIMAL
    elif max(Decimal(str(v)) for v in valores) < UMBRAL_VALOR_PEQUENO:
        sugerido = FRACCION_DECIMAL
    else:
        sugerido = VALOR_PORCENTUAL

    return ResultadoInterpretacionProrrateo(
        sugerido,
        True,
        'Interpretación ambigua: confirme si los valores son porcentaje directo '
        '(0,85 = 0,85 %) o fracción decimal (0,0085 = 0,85 %)',
    )
