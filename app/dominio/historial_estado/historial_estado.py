from datetime import datetime
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.usuario.usuario import Usuario


class HistorialEstado:
    
    def __init__(
        self,
        estado_anterior: EstadoParticular | None,
        estado_actual: EstadoParticular,
        fecha_registro: datetime,
        motivo_cambio: str | None,
        cambiado_por: Usuario,
        dias_transcurridos = int,
    ):
        self.estado_anterior = estado_anterior
        self.estado_actual = estado_actual
        self.fecha_registro = fecha_registro
        self.motivo_cambio = motivo_cambio
        self.cambiado_por = cambiado_por
        self.dias_transcurridos = dias_transcurridos