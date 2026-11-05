from abc import ABC, abstractmethod

from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.prospecto_empresa.prospecto_empresa import ProspectoEmpresa
from app.dominio.usuario.usuario import Usuario


class RepositorioProspectos(ABC):
    
    @abstractmethod
    def registrar_prospecto(self, prospecto: Prospecto) -> int:
        pass

    # Retorna el id del cliente
    @abstractmethod
    def crear_cliente(self, prospecto: Prospecto) -> int | None:
        pass

    @abstractmethod
    def registrar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> int:
        pass

    @abstractmethod
    def registrar_prospecto_empresa(self, prospecto: ProspectoEmpresa) -> int:
        pass
    
    @abstractmethod
    def buscar(self, id: int) -> Prospecto | None:
        pass

    @abstractmethod
    def buscar_cliente(self, id_cliente: int) -> Prospecto | None:
        pass

    @abstractmethod
    def buscar_prospecto_condominio(self, id: int) -> ProspectoCondominio | None:
        pass

    @abstractmethod
    def buscar_prospecto_empresa(self, id: int) -> ProspectoEmpresa | None:
        pass

    @abstractmethod
    def crear_prospecto_empresa(self, id_prospecto: int) -> None:
        """Crea la fila de extensión vacía de un prospecto empresa existente
        (se usa al cambiar un prospecto a la línea de Líneas Comerciales)."""
        pass

    @abstractmethod
    def eliminar_prospecto_empresa(self, id_prospecto: int) -> None:
        pass

    @abstractmethod
    def existe_giro_comercial_por_nombre(self, id_prospecto: int, nombre: str) -> bool:
        pass

    @abstractmethod
    def buscar_prospecto_por_nombre(self, nombre: str) -> Prospecto | None:
        pass

    @abstractmethod
    def buscar_prospecto_por_rut(self, rut: str) -> Prospecto | None:
        pass

    @abstractmethod
    def buscar_prospecto_por_proceso_comercial(self, id_proceso: int) -> Prospecto | None:
        pass

    @abstractmethod
    def actualizar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> None:
        pass

    @abstractmethod
    def actualizar_prospecto_empresa(self, prospecto: ProspectoEmpresa) -> None:
        pass

    @abstractmethod
    def asignar_administrador_condominio(self, prospecto: ProspectoCondominio, id_administrador: int) -> None:
        pass

    @abstractmethod
    def actualizar_prospecto(self, prospecto: Prospecto) -> None:
        pass
