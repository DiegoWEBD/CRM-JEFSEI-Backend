from app.dominio.riesgo_cobertura.tipo_riesgo_cobertura.tipo_riesgo_cobertura import TipoRiesgoCobertura


class RiesgoCobertura:

    def __init__(
        self,
        id: int,
        tipo_riesgo_cobertura: TipoRiesgoCobertura,
        nombre: str,
        descripcion: str
    ):
        self.id = id
        self.tipo_riesgo_cobertura = tipo_riesgo_cobertura
        self.nombre = nombre
        self.descripcion = descripcion