from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio


class ObtenerLineasDeNegocioUseCase:
    
    def __init__(self, repositorio_lineas_negocio: RepositorioLineasNegocio):
        self.repositorio_lineas_negocio = repositorio_lineas_negocio

    def ejecutar(self):
        return self.repositorio_lineas_negocio.obtener_todas()