from app.dominio.estados.estado_base.estado_base import EstadoBase


class EstadoParticular:
    def __init__(
        self, 
        estado_base: EstadoBase, 
        dias_limite_particular: int | None
    ):
        self.estado_base = estado_base
        self.dias_limite_particular = dias_limite_particular