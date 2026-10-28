from datetime import datetime

from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.producto.producto import Producto
from app.dominio.usuario.usuario import Usuario

class ProcesoComercial:
    def __init__(
        self, 
        id: int,
        ejecutivo_comercial: Usuario | None,
        ejecutivo_evaluacion: Usuario | None,
        id_prospecto: int,
        nombre_cliente: str,
        producto: Producto,
        estado_actual: EstadoInformativoProcesoComercial,
        cerrado: bool,
        ejecutivo_renovacion: Usuario | None = None,
        asistente_renovacion: Usuario | None = None,
        fecha_estimada_cierre: datetime | None = None,
        probabilidad_cierre_ejecutivo: float | None = None,
        prima_cotizada: float | None = None,
        prima_potencial_estimada: float | None = None,
        prima_esperada: float | None = None,
        renovacion: bool = False,
        descartado: bool = False,
        motivo_cierre: str | None = None,
        fecha_cierre: datetime | None = None,
        fecha_apertura: datetime | None = None,
        monto_asegurado_actual: float | None = None,
        nombre_excel_alicuota: str | None = None,
    ):
        self.id = id
        self.ejecutivo_comercial = ejecutivo_comercial
        self.ejecutivo_evaluacion = ejecutivo_evaluacion
        self.ejecutivo_renovacion = ejecutivo_renovacion
        self.asistente_renovacion = asistente_renovacion
        self.producto = producto
        self.estado_actual = estado_actual
        self.cerrado = cerrado
        self.nombre_cliente = nombre_cliente
        self.id_prospecto = id_prospecto
        self.fecha_estimada_cierre = fecha_estimada_cierre
        self.probabilidad_cierre_ejecutivo = probabilidad_cierre_ejecutivo
        self.prima_cotizada = prima_cotizada
        self.prima_potencial_estimada = prima_potencial_estimada
        self.prima_esperada = prima_esperada
        self.renovacion = renovacion
        self.descartado = descartado
        self.motivo_cierre = motivo_cierre
        self.fecha_cierre = fecha_cierre
        self.fecha_apertura = fecha_apertura
        self.monto_asegurado_actual = monto_asegurado_actual
        self.nombre_excel_alicuota = nombre_excel_alicuota