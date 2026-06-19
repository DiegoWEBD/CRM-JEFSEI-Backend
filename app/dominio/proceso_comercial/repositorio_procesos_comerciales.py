from abc import ABC, abstractmethod

from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial


class RepositorioProcesosComerciales(ABC):
    
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