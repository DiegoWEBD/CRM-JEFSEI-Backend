from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AuthorizationService:

    def __init__(
        self,
        authorization_repository: AuthorizationRepository,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios
    ):
        self.authorization_repository = authorization_repository
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

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
    
    def usuario_puede_ver_plan_pago(self, rut_usuario: str, numero_poliza: str) -> bool:
        return self.authorization_repository.usuario_puede_ver_plan_pago(rut_usuario, numero_poliza)
    
    def usuario_puede_crear_estudio_comercial(self, rut_usuario: str, id_prospecto: int) -> bool:
        return self.authorization_repository.usuario_puede_crear_estudio_comercial(rut_usuario, id_prospecto)

    def usuario_puede_actualizar_poliza(self, rut_usuario: str, numero_poliza: str) -> bool:
        return self.authorization_repository.usuario_puede_actualizar_poliza(rut_usuario, numero_poliza)

    def usuario_puede_actualizar_fecha_estimada_cierre(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        return self.authorization_repository.usuario_puede_actualizar_fecha_estimada_cierre(rut_usuario, id_proceso_comercial)

    def usuario_puede_actualizar_probabilidad_cierre(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        return self.authorization_repository.usuario_puede_actualizar_probabilidad_cierre(rut_usuario, id_proceso_comercial)

    def usuario_puede_eliminar_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        return self.authorization_repository.usuario_puede_eliminar_cotizacion(rut_usuario, id_solicitud)

    def usuario_puede_actualizar_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        return self.authorization_repository.usuario_puede_actualizar_cotizacion(rut_usuario, id_solicitud)

    def usuario_puede_eliminar_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        return self.authorization_repository.usuario_puede_eliminar_solicitud_cotizacion(rut_usuario, id_solicitud)

    def usuario_puede_ver_solicitudes_cotizacion(self, usuario: Usuario, id_proceso_comercial: int) -> bool:
        if self.repositorio_usuarios.usuario_tiene_permiso(usuario, 'VER_SOLICITUDES_COTIZACION_GLOBAL'):
            return True

        if not self.repositorio_usuarios.usuario_tiene_permiso(usuario, 'VER_SOLICITUDES_COTIZACION_PROPIAS'):
            return False

        prospecto = self.repositorio_prospectos.buscar_prospecto_por_proceso_comercial(id_proceso_comercial)

        if not prospecto:
            return False

        return any([
            prospecto.ejecutivo_comercial_asignado.rut == usuario.rut if prospecto.ejecutivo_comercial_asignado else False,
            prospecto.ejecutivo_evaluacion_asignado.rut == usuario.rut if prospecto.ejecutivo_evaluacion_asignado else False
        ])