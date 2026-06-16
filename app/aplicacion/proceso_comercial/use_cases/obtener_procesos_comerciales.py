from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


class ObtenerProcesosComercialesUseCase:

    def __init__(self, repositorio_procesos_comerciales: RepositorioProcesosComerciales):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, id_prospecto: int) -> list[ProcesoComercial]:
        return self.repositorio_procesos_comerciales.obtener_procesos_comerciales(id_prospecto)