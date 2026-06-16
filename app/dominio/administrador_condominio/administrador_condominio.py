class AdministradorCondominio:
    
    def __init__(
        self,
        id: int | None,
        nombre_administrador: str,
        nombre_contacto: str | None,
        telefono: str | None,
        correo: str | None
    ):
        self.id = id
        self.nombre_administrador = nombre_administrador
        self.nombre_contacto = nombre_contacto
        self.telefono = telefono
        self.correo = correo