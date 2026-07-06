from abc import ABC, abstractmethod
from datetime import datetime

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
        fecha_gestion: datetime,
    ) -> GestionComercial:
        pass

    @abstractmethod
    def obtener_todas(self, id_prospecto: int | None = None) -> list[GestionComercial]:
        pass

    @abstractmethod
    def obtener_ultima(self, id_prospecto: int) -> GestionComercial | None:
        pass
