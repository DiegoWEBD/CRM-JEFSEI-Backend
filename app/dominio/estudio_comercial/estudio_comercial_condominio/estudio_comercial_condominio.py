class EstudioComercialCondominio:

    def __init__(
        self,
        id: int | None,
        id_solicitud: int,
        nombre_archivo: str
    ):
        self.id = id
        self.id_solicitud = id_solicitud
        self.nombre_archivo = nombre_archivo