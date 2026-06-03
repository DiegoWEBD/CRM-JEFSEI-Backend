from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio


class ObtenerLineaNegocioProspectoUseCase:

    def __init__(self, repositorio_lineas_negocio: RepositorioLineasNegocio):
        self.repositorio_lineas_negocio = repositorio_lineas_negocio

    def ejecutar(self, id_prospecto: int) -> LineaNegocio:
        linea_negocio = self.repositorio_lineas_negocio.obtener_linea_negocio_de_prospecto(id_prospecto)

        if linea_negocio is None:
            raise ValueError('Línea de negocio no encontrada')
        
        return linea_negocio