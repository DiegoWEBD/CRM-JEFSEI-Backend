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
        codigo_etapa_actual: str,
        cerrado: bool,
        id: int | None = None
    ):
        self.id = id
        self.ejecutivo_comercial = ejecutivo_comercial
        self.ejecutivo_evaluacion = ejecutivo_evaluacion
        self.historial_estados = historial_estados
        self.producto = producto
        self.codigo_etapa_actual = codigo_etapa_actual
        self.cerrado = cerrado