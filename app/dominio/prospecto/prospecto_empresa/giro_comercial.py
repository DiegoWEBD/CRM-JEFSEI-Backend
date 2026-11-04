class GiroComercial:
    def __init__(
        self,
        nombre: str,
        id: int | None = None,
        id_prospecto_empresa: int | None = None
    ):
        self.id = id
        self.id_prospecto_empresa = id_prospecto_empresa
        self.nombre = nombre
