from abc import ABC, abstractmethod
from datetime import datetime

from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial


class RepositorioProcesosComerciales(ABC):
    
    @abstractmethod
    def guardar(self, proceso: ProcesoComercial, es_nuevo: bool = False) -> ProcesoComercial:
        pass

    @abstractmethod
    def nuevo_renovacion(self, numero_poliza_base: str, rut_usuario: str) -> int | None:
        """Crea el proceso comercial de renovación de la póliza base.

        Nace en OPORTUNIDAD_CREADA con el mismo prospecto y producto de la
        póliza base, y registra la fila en ProcesoComercialRenovacion.
        """
        pass

    @abstractmethod
    def buscar_renovacion_por_poliza_base(self, numero_poliza_base: str) -> int | None:
        """Id del proceso comercial de renovación de la póliza base.

        None si la póliza no tiene proceso de renovación iniciado.
        """
        pass

    @abstractmethod
    def obtener_poliza_base_renovacion(self, id_proceso: int) -> str | None:
        """Número de la póliza base del proceso comercial de renovación.

        None si el proceso no es de renovación (no tiene fila en
        ProcesoComercialRenovacion). Es el lookup inverso de
        buscar_renovacion_por_poliza_base: se usa al descartar una
        oportunidad de renovación para re-evaluar las alertas de su póliza.
        """
        pass

    @abstractmethod
    def buscar(self, id: int) -> ProcesoComercial | None:
        pass

    @abstractmethod
    def buscar_por_solicitud_cotizacion(self, id_solicitud: int) -> ProcesoComercial | None:
        """Proceso comercial asociado a la solicitud de cotización.

        None si la solicitud no existe o no tiene proceso asociado.
        """
        pass

    @abstractmethod
    def obtener_procesos_comerciales(
        self, 
        id_prospecto: int | None = None, 
        abiertos: bool | None = None,
        renovaciones: bool | None = None,
    ) -> list[ProcesoComercial]:
        pass

    @abstractmethod
    def obtener_todos(
        self,
        texto_busqueda: str | None,
        ejecutivos: list[str] | None,
        etapas: list[str] | None,
        estados_comerciales: list[str] | None,
        estado_semaforo: list[str] | None,
        estado_proceso: str | None,
        cerrado: bool | None,
        fecha_ingreso_etapa_desde: str | None,
        fecha_ingreso_etapa_hasta: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> dict:
        pass

    @abstractmethod
    def actualizar_fecha_estimada_cierre(self, id: int, fecha: datetime | None):
        pass

    @abstractmethod
    def actualizar_probabilidad_cierre_ejecutivo(self, id: int, probabilidad: float | None):
        pass