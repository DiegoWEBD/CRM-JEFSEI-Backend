from abc import ABC, abstractmethod
from datetime import datetime

from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial


class RepositorioProcesosComerciales(ABC):
    
    @abstractmethod
    def nuevo(self, tipo: str, id_prospecto: int, rut_usuario: str) -> int | None:
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
    def buscar(self, id: int) -> ProcesoComercial | None:
        pass

    @abstractmethod
    def buscar_por_solicitud_cotizacion(self, id_solicitud: int) -> ProcesoComercial | None:
        """Proceso comercial asociado a la solicitud de cotización.

        None si la solicitud no existe o no tiene proceso asociado.
        """
        pass

    @abstractmethod
    def obtener_procesos_comerciales(self, id_prospecto: int | None = None, abiertos: bool | None = None) -> list[ProcesoComercial]:
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
    def cerrar(self, id: int, ganado: bool, observacion: str | None, rut_usuario: str):
        pass

    @abstractmethod
    def actualizar_fecha_estimada_cierre(self, id: int, fecha: datetime | None):
        pass

    @abstractmethod
    def actualizar_probabilidad_cierre_ejecutivo(self, id: int, probabilidad: float | None):
        pass

    @abstractmethod
    def cambiar_estado_manual(
        self,
        id: int,
        codigo_estado_destino: str,
        observacion: str | None,
        rut_usuario: str,
    ):
        """Cambia el estado del proceso validando la transición manual."""
        pass

    @abstractmethod
    def actualizar(self, proceso: ProcesoComercial):
        pass