class EstadoBase:
    def __init__(
        self, 
        codigo: str, 
        nombre: str, 
        dias_limite: int, 
        siguiente_estado: EstadoBase | None = None
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.dias_limite = dias_limite
        self.siguiente_estado = siguiente_estado