from app.dominio.authorization.authorizacion_repository import AuthorizationRepository


class AuthorizationService:

    def __init__(self, authorization_repository: AuthorizationRepository):
        self.authorization_repository = authorization_repository

    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        return self.authorization_repository.usuario_puede_ver_solicitud_cotizacion(rut_usuario, id_solicitud)
    
    def usuario_puede_gestionar_renovacion(self, rut_usuario: str, numero_poliza: str) -> bool:
        return self.authorization_repository.usuario_puede_gestionar_renovacion(rut_usuario, numero_poliza)