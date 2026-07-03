from abc import ABC, abstractmethod


class AuthorizationRepository(ABC):
    
    @abstractmethod
    def usuario_puede_ver_prospecto(self, rut_usuario: str, id_prospecto) -> bool:
        pass

    @abstractmethod
    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        pass

    @abstractmethod
    def usuario_puede_gestionar_renovacion(self, rut_usuario: str, numero_poliza: str) -> bool:
        pass

    @abstractmethod
    def usuario_puede_crear_proceso_comercial(self, rut_usuario: str, id_prospecto: int) -> bool:
        pass

    @abstractmethod
    def usuario_puede_solicitar_cotizacion(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        pass

    @abstractmethod
    def usuario_puede_ver_procesos_comerciales(self, rut_usuario: str, id_prospecto: int) -> bool:
        pass

    @abstractmethod
    def usuario_puede_subir_poliza(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        pass

    @abstractmethod
    def usuario_puede_ver_poliza(self, rut_usuario: str, numero_poliza: str) -> bool:
        pass

    @abstractmethod
    def usuario_puede_ver_plan_pago(self, rut_usuario: str, numero_poliza: str) -> bool:
        pass

    @abstractmethod
    def usuario_puede_crear_estudio_comercial(self, rut_usuario: str, id_prospecto: int) -> bool:
        pass