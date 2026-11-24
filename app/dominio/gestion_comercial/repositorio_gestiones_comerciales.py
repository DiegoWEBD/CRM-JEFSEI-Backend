from abc import ABC, abstractmethod

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial


class RepositorioGestionesComerciales(ABC):

    @abstractmethod
    def registrar(
        self,
        tipo: str,
        rut_usuario: str,
        id_prospecto: int,
        titulo: str,
        estado_contacto: str | None,
        observacion: str | None,
        fecha_gestion: str,
    ) -> GestionComercial:
        pass

    @abstractmethod
    def obtener_todas(self, id_prospecto: int | None = None, rut_usuario: str | None = None) -> list[GestionComercial]:
        """Gestiones comerciales. Si se pasa rut_usuario, se limita a los
        prospectos asignados a ese usuario (scoping de permisos PROPIOS)."""
        pass

    @abstractmethod
    def obtener_ultima(self, id_prospecto: int) -> GestionComercial | None:
        pass
