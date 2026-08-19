class Archivo:

    def __init__(
        self,
        id: int | None,
        id_prospecto: int,
        nombre_almacenado: str,
        nombre_original: str,
        tipo_contenido: str,
        tamano_bytes: int,
        rut_subido_por: str,
        created_at=None
    ):
        self.id = id
        self.id_prospecto = id_prospecto
        self.nombre_almacenado = nombre_almacenado
        self.nombre_original = nombre_original
        self.tipo_contenido = tipo_contenido
        self.tamano_bytes = tamano_bytes
        self.rut_subido_por = rut_subido_por
        self.created_at = created_at
