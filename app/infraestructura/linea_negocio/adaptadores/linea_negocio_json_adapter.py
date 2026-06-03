from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.presentacion.api.linea_negocio.dto.linea_negocio_json import LineaNegocioJson


class LineaNegocioJsonAdapter:

    def __init__(self, linea_negocio: LineaNegocio):
        self.linea_negocio = linea_negocio

    def to_json(self) -> LineaNegocioJson:
        if self.linea_negocio.id is None:
            raise Exception('Línea de negocio inválida')
        
        return LineaNegocioJson(
            id=self.linea_negocio.id,
            nombre=self.linea_negocio.nombre,
            productos=[producto.nombre for producto in self.linea_negocio.productos]
        )