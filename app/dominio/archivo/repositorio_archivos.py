from abc import ABC, abstractmethod
from app.dominio.archivo.archivo import Archivo


class RepositorioArchivos(ABC):

    @abstractmethod
    def insertar(
        self,
        id_prospecto: int,
        nombre_almacenado: str,
        nombre_original: str,
        tipo_contenido: str,
        tamano_bytes: int,
        rut_subido_por: str
    ) -> Archivo:
        pass

    @abstractmethod
    def listar_por_prospecto(self, id_prospecto: int) -> list[Archivo]:
        pass

    @abstractmethod
    def obtener_por_id(self, id_archivo: int) -> Archivo | None:
        pass

    @abstractmethod
    def eliminar(self, id_archivo: int) -> bool:
        pass

    @abstractmethod
    def existe_nombre_almacenado(self, id_prospecto: int, nombre_almacenado: str) -> bool:
        pass
