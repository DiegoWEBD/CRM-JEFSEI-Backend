from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.core.config import settings


class IniciarSesionUseCase:

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        authentication_service: AuthenticationService,
        servicio_auditoria: ServicioAuditoria,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service
        self.servicio_auditoria = servicio_auditoria

    def execute(self, rut: str, password: str, contexto: ContextoPeticion) -> IniciarSesionResponseDTO | None:
        usuario = self.repositorio_usuarios.buscar(rut)

        credenciales_validas = (
            usuario is not None
            and usuario.password_hash is not None
            and usuario.habilitado
            and not usuario.eliminado
            and self.authentication_service.verificar_password(password, usuario.password_hash)
        )

        if not usuario or not credenciales_validas:
            self.servicio_auditoria.registrar_autenticacion(
                evento=EventoAuditoria.LOGIN_FALLIDO,
                resultado=ResultadoAuditoria.FALLIDO,
                contexto=contexto,
                rut_usuario=rut,
                detalle='Credenciales inválidas',
            )
            return None

        codigo_permisos = list(set(
            permiso.codigo
            for rol in usuario.roles
            for permiso in rol.permisos
        ))

        # Crea sesión + access token + refresh token en una sola operación
        access_token, refresh_token = self.authentication_service.crear_sesion_y_tokens(
            claims={
                "rut": usuario.rut,
                "nombre": usuario.nombre,
                "codigo_roles": [rol.codigo for rol in usuario.roles],
                "nombre_roles": [rol.nombre for rol in usuario.roles],
                "codigo_permisos": codigo_permisos,
            },
            ip=contexto.ip_origen,
            user_agent=contexto.user_agent,
        )

        self.servicio_auditoria.registrar_autenticacion(
            evento=EventoAuditoria.LOGIN_EXITOSO,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=usuario.rut,
            nombre_usuario=usuario.nombre,
        )

        return IniciarSesionResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            usuario=usuario,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
