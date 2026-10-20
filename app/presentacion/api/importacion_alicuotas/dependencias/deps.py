from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.analizar_alicuotas import (
    AnalizarAlicuotasUseCase,
)
from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.validar_alicuotas import (
    ValidarAlicuotasUseCase,
)
from app.infraestructura.solicitud_cotizacion.lector_excel_openpyxl import LectorExcelOpenpyxl


def get_analizar_alicuotas_use_case():
    return AnalizarAlicuotasUseCase(lector_excel=LectorExcelOpenpyxl())


def get_validar_alicuotas_use_case():
    return ValidarAlicuotasUseCase(lector_excel=LectorExcelOpenpyxl())
