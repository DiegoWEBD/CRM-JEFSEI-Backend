from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales


class ObtenerGestionesComercialesUseCase:

    def __init__(self, repositorio: RepositorioGestionesComerciales) -> None:
        self.repositorio = repositorio

    def ejecutar(self, id_prospecto: int | None = None) -> list[GestionComercial]:
        return self.repositorio.obtener_todas(id_prospecto=id_prospecto)
