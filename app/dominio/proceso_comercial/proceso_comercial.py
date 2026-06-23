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