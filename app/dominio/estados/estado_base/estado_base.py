class EstadoBase:
    def __init__(self, codigo: str, nombre: str, dias_limite: int, codigo_siguiente_estado: str | None):
        self.codigo = codigo
        self.nombre = nombre
        self.dias_limite = dias_limite
        self.codigo_siguiente_estado = codigo_siguiente_estado