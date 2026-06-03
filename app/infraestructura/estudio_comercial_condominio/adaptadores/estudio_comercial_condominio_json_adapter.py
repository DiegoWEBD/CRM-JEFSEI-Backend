from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.infraestructura.detalle_estudio_comercial_condominio.adaptadores.detalle_estudio_comercial_condominio_json_adapter import DetalleEstudioComercialCondominioJsonAdapter
from app.presentacion.api.estudio_comercial.dto.estudio_comercial_condominio_json import EstudioComercialCondominioJson


class EstudioComercialCondominioJsonAdapter:

    def __init__(self, estudio: EstudioComercialCondominio) -> None:
        self.estudio = estudio

    def to_json(self) -> EstudioComercialCondominioJson:
        return EstudioComercialCondominioJson(
            cantidad_cuotas=self.estudio.cantidad_cuotas,
            valor_uf=self.estudio.valor_uf,
            detalles=[]
        )