from datetime import datetime


class GestionComercial:
    def __init__(
        self,
        id: int,
        tipo: str,
        rut_usuario: str,
        nombre_ejecutivo: str | None,
        id_prospecto: int,
        nombre_cliente: str | None,
        titulo: str,
        estado_contacto: str | None,
        observacion: str | None,
        created_at: datetime,
        fecha_gestion: datetime,
    ) -> None:
        self.id = id
        self.tipo = tipo
        self.rut_usuario = rut_usuario
        self.nombre_ejecutivo = nombre_ejecutivo
        self.id_prospecto = id_prospecto
        self.nombre_cliente = nombre_cliente
        self.titulo = titulo
        self.estado_contacto = estado_contacto
        self.observacion = observacion
        self.created_at = created_at
        self.fecha_gestion = fecha_gestion
