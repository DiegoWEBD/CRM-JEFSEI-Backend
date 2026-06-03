from datetime import datetime


class ComunicadoGerencia:
    def __init__(
        self,
        id: int | None,
        titulo: str,
        descripcion: str,
        prioridad: str,
        fecha: datetime,
        caducidad: datetime,
        nombre_gerente: str
    ):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.prioridad = prioridad
        self.fecha = fecha
        self.caducidad = caducidad
        self.nombre_gerente = nombre_gerente