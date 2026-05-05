from app.dominio.estados.estado_base.estado_base import EstadoBase
from datetime import datetime

class EstadoParticular:
    def __init__(
        self, 
        estado_base: EstadoBase, 
        fecha_resgistro: datetime, 
        dias_limite_particular: int | None,
        dias_transcurridos: int
    ):
        self.estado_base = estado_base
        self.fecha_resgistro = fecha_resgistro
        self.dias_limite_particular = dias_limite_particular
        self.dias_transcurridos = dias_transcurridos