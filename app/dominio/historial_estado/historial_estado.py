from datetime import datetime
from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.usuario.usuario import Usuario


class HistorialEstado:
    
    def __init__(
        self,
        estado: EstadoInformativoProcesoComercial,
        fecha_registro: datetime,
        observacion: str | None,
        registrado_por: Usuario,
        dias_transcurridos: int,
    ):
        self.estado = estado
        self.fecha_registro = fecha_registro
        self.observacion = observacion
        self.registrado_por = registrado_por
        self.dias_transcurridos = dias_transcurridos