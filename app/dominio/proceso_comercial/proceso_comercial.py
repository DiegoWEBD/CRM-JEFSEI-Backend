from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.producto.producto import Producto
from app.dominio.usuario.usuario import Usuario

class ProcesoComercial:
    def __init__(
        self, 
        historial_estados: list[HistorialEstado], 
        ejecutivo_comercial: Usuario | None,
        ejecutivo_evaluacion: Usuario | None,
        producto: Producto,
        codigo_estado_actual: str,
        cerrado: bool,
        id: int | None = None,
        ejecutivo_renovacion: Usuario | None = None,
        asistente_renovacion: Usuario | None = None,
    ):
        self.id = id
        self.ejecutivo_comercial = ejecutivo_comercial
        self.ejecutivo_evaluacion = ejecutivo_evaluacion
        self.ejecutivo_renovacion = ejecutivo_renovacion
        self.asistente_renovacion = asistente_renovacion
        self.historial_estados = historial_estados
        self.producto = producto
        self.codigo_estado_actual = codigo_estado_actual
        self.cerrado = cerrado