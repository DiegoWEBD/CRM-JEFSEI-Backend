from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.usuario.usuario import Usuario


class AuthorizationService:

    def __init__(self, authorization_repository: AuthorizationRepository):
        self.authorization_repository = authorization_repository

    def usuario_puede_ver_prospecto(self, rut_usuario: str, id_prospecto) -> bool:
        return self.authorization_repository.usuario_puede_ver_prospecto(rut_usuario, id_prospecto)

    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        return self.authorization_repository.usuario_puede_ver_solicitud_cotizacion(rut_usuario, id_solicitud)
    
    def usuario_puede_gestionar_renovacion(self, rut_usuario: str, numero_poliza: str) -> bool:
        return self.authorization_repository.usuario_puede_gestionar_renovacion(rut_usuario, numero_poliza)
    
    def usuario_puede_crear_proceso_comercial(self, usuario: Usuario, id_prospecto: int) -> bool:
        return self.authorization_repository.usuario_puede_crear_proceso_comercial(usuario.rut, id_prospecto)
    
    def usuario_puede_solicitar_cotizacion(self, usuario: Usuario, id_proceso_comercial: int) -> bool:
        return self.authorization_repository.usuario_puede_solicitar_cotizacion(usuario.rut, id_proceso_comercial)
    
    def usuario_puede_ver_procesos_comerciales(self, rut_usuario: str, id_prospecto: int) -> bool:
        return self.authorization_repository.usuario_puede_ver_procesos_comerciales(rut_usuario, id_prospecto)
    
    def usuario_puede_subir_poliza(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        return self.authorization_repository.usuario_puede_subir_poliza(rut_usuario, id_proceso_comercial)
    
    def usuario_puede_ver_poliza(self, rut_usuario: str, numero_poliza: str) -> bool:
        return self.authorization_repository.usuario_puede_ver_poliza(rut_usuario, numero_poliza)