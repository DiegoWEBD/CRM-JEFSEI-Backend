class Contacto:

    def __init__(
        self,
        id: int | None,
        id_prospecto: int,
        nombre: str,
        telefono: str | None,
        correo: str | None,
        cargo: str | None
    ):
        self.id = id
        self.id_prospecto = id_prospecto
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.cargo = cargo