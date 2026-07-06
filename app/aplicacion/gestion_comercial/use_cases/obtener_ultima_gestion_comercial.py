from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales


class ObtenerUltimaGestionComercialUseCase:

    def __init__(self, repositorio: RepositorioGestionesComerciales) -> None:
        self.repositorio = repositorio

    def ejecutar(self, id_prospecto: int) -> GestionComercial | None:
        return self.repositorio.obtener_ultima(id_prospecto=id_prospecto)
