from app.dominio.comuna.comuna import Comuna
from app.presentacion.api.comuna.dto.comuna_json import ComunaJson


class ComunaJsonAdapter:

    def __init__(self, comuna: Comuna):
        self.comuna = comuna

    def to_json(self) -> ComunaJson:
        
        if self.comuna.id is None:
            raise Exception('Comuna inválida')
        
        return ComunaJson(
            id=self.comuna.id,
            nombre=self.comuna.nombre
        )