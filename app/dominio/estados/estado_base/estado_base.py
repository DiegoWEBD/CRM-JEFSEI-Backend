class EstadoBase:
    def __init__(
        self, 
        codigo: str, 
        nombre: str, 
        dias_limite: int, 
        accion: str = '',
        siguiente_estado: EstadoBase | None = None
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.dias_limite = dias_limite
        self.accion = accion
        self.siguiente_estado = siguiente_estado