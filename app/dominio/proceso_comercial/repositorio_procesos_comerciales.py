from abc import ABC, abstractmethod

from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial


class RepositorioProcesosComerciales(ABC):
    
    @abstractmethod
    def nuevo(self, tipo: str, id_prospecto: int, rut_usuario: str) -> int | None:
        pass

    @abstractmethod
    def buscar(self, id: int) -> ProcesoComercial | None:
        pass

    @abstractmethod
    def obtener_procesos_comerciales(self, id_prospecto: int) -> list[ProcesoComercial]:
        pass

    @abstractmethod
    def obtener_todos(
        self,
        texto_busqueda: str | None,
        ejecutivos: list[str] | None,
        etapas: list[str] | None,
        cerrado: bool | None,
        fecha_ingreso_etapa_desde: str | None,
        fecha_ingreso_etapa_hasta: str | None,
    ) -> list[ProcesoComercial]:
        pass

    @abstractmethod
    def cerrar(self, id: int, ganado: bool, observacion: str | None, rut_usuario: str):
        pass