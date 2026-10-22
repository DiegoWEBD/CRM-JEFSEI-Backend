from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.dto.configuracion_importacion_alicuotas import (
    ConfiguracionImportacionAlicuotas,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.extraccion_alicuotas import (
    FilaRango,
    extraer_registros,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.hoja_excel import HojaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.interpretacion_prorrateo import (
    TIPOS_INTERPRETACION_PRORRATEO,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.lector_alicuotas_excel import (
    LectorAlicuotasExcel,
)


class ValidarAlicuotasUseCase:
    """Extrae, normaliza y valida los registros con la configuración elegida."""

    def __init__(self, lector_excel: LectorAlicuotasExcel) -> None:
        self.lector_excel = lector_excel

    def ejecutar(self, contenido: bytes, configuracion: ConfiguracionImportacionAlicuotas) -> dict:
        hojas = self.lector_excel.obtener_hojas(contenido)
        hoja = next((h for h in hojas if h.nombre == configuracion.hoja), None)

        if hoja is None:
            raise DatoInvalidoException(f'La hoja "{configuracion.hoja}" no existe en el archivo')

        errores = self._validar_configuracion(configuracion, hoja)

        if errores:
            raise DatoInvalidoException('; '.join(errores))

        if (
            configuracion.interpretacion_prorrateo is not None
            and configuracion.interpretacion_prorrateo not in TIPOS_INTERPRETACION_PRORRATEO
        ):
            raise DatoInvalidoException(
                f'Interpretación de prorrateo desconocida: {configuracion.interpretacion_prorrateo}'
            )

        bloque = self.lector_excel.leer_bloque(
            contenido,
            hoja.nombre,
            configuracion.primera_fila,
            configuracion.ultima_fila,
            [configuracion.columna_identificador, configuracion.columna_prorrateo],
        )

        filas = [
            FilaRango(
                numero_fila=configuracion.primera_fila + indice,
                celda_identificador=fila[0],
                celda_prorrateo=fila[1],
            )
            for indice, fila in enumerate(bloque)
        ]

        resultado = extraer_registros(filas, configuracion.interpretacion_prorrateo)

        return {
            'registros': [registro.to_dict() for registro in resultado.registros],
            'cantidad_registros': len(resultado.registros),
            'problemas': [problema.to_dict() for problema in resultado.problemas],
            'tiene_errores_bloqueantes': resultado.tiene_errores_bloqueantes,
            'confirmacion_requerida': resultado.interpretacion.requiere_confirmacion,
            'suma_prorrateos': (
                float(resultado.suma_prorrateos) if resultado.suma_prorrateos is not None else None
            ),
            'interpretacion': resultado.interpretacion.to_dict(),
            'filas_excluidas': resultado.filas_excluidas,
        }

    def _validar_configuracion(
        self, configuracion: ConfiguracionImportacionAlicuotas, hoja: HojaExcel
    ) -> list[str]:
        errores: list[str] = []

        if configuracion.columna_identificador == configuracion.columna_prorrateo:
            errores.append('La columna de identificador y la de prorrateo deben ser distintas')

        if not 1 <= configuracion.columna_identificador <= hoja.columnas:
            errores.append('La columna de identificador está fuera de la hoja')

        if not 1 <= configuracion.columna_prorrateo <= hoja.columnas:
            errores.append('La columna de prorrateo está fuera de la hoja')

        if not 1 <= configuracion.fila_encabezados <= hoja.filas:
            errores.append('La fila de encabezados está fuera de la hoja')

        if configuracion.primera_fila <= configuracion.fila_encabezados:
            errores.append('La primera fila de datos debe ser posterior a la fila de encabezados')

        if configuracion.ultima_fila < configuracion.primera_fila:
            errores.append('El rango de filas no es válido')

        if configuracion.ultima_fila > hoja.filas:
            errores.append('La última fila excede las filas disponibles de la hoja')

        return errores
