import uuid
from datetime import datetime, timedelta, timezone

from psycopg import Connection
from psycopg.rows import DictRow

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
from app.aplicacion.auditoria.audit_service import AuditService
from app.core.config import settings
from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento
from app.dominio.auditoria.repositorio_sesiones import RepositorioSesiones
from app.dominio.auditoria.sesion import Sesion
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios

# RUCkimoto del motivo de fallo. Un evento que distinguiera "usuario no existe"
# de "contraseña incorrecta" permitiría enumerar cuentas válidas (§17).
MOTIVO_CREDENCIALES = 'INVALID_CREDENTIALS'


class IniciarSesionUseCase:

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        authentication_service: AuthenticationService,
        repositorio_sesiones: RepositorioSesiones | None = None,
        audit_service: AuditService | None = None,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service
        self.repositorio_sesiones = repositorio_sesiones
        self.audit_service = audit_service

    def execute(
        self,
        rut: str,
        password: str,
        scope: dict | None = None,
        conn: Connection[DictRow] | None = None,
    ) -> IniciarSesionResponseDTO | None:
        usuario = self.repositorio_usuarios.buscar(rut)

        # Todos los casos de fallo colapsan en el mismo retorno: el endpoint
        # responde siempre 401 "Credenciales inválidas" y el evento de auditoría
        # registra el mismo motivo genérico.
        if not usuario or not usuario.password_hash or not usuario.habilitado or usuario.eliminado:
            self._auditar_fallo(rut, scope, conn)
            return None

        if not self.authentication_service.verificar_password(password, usuario.password_hash):
            self._auditar_fallo(rut, scope, conn)
            return None

        codigo_permisos = list(set(
            permiso.codigo
            for rol in usuario.roles
            for permiso in rol.permisos
        ))

        id_sesion = str(uuid.uuid4())
        ahora = datetime.now(timezone.utc)
        claims = {
            "rut": usuario.rut,
            "nombre": usuario.nombre,
            "codigo_roles": [rol.codigo for rol in usuario.roles],
            "nombre_roles": [rol.nombre for rol in usuario.roles],
            "codigo_permisos": codigo_permisos,
        }

        token = self.authentication_service.crear_access_token_de_sesion(claims, id_sesion)
        refresh_token = self.authentication_service.crear_refresh_token(id_sesion)

        self._persistir_sesion(id_sesion, usuario, refresh_token, scope, ahora, conn)
        self._auditar_exito(usuario.rut, id_sesion, scope, conn)

        return IniciarSesionResponseDTO(
            access_token=token,
            refresh_token=refresh_token,
            id_sesion=id_sesion,
            usuario=usuario,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    # --- Sesión ---

    def _persistir_sesion(
        self,
        id_sesion: str,
        usuario,
        refresh_token: str,
        scope: dict | None,
        ahora: datetime,
        conn: Connection[DictRow] | None,
    ) -> None:
        if not self.repositorio_sesiones:
            return

        contexto = self.audit_service.contexto_de(scope) if self.audit_service else None
        expiracion = ahora + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        sesion = Sesion(
            id=id_sesion,
            rut_usuario=usuario.rut,
            fecha_creacion=ahora,
            fecha_expiracion=expiracion,
            ip_origen=contexto.ip_origen if contexto else None,
            user_agent=contexto.user_agent if contexto else None,
            device_id=contexto.device_id if contexto else None,
        )
        self.repositorio_sesiones.crear(sesion, conn=conn)
        # Sólo se guarda el hash: un dump de la base no debe servir para
        # suplantar una sesión.
        self.repositorio_sesiones.crear_refresh_token(
            id_sesion,
            self.authentication_service.hashear_refresh_token(refresh_token),
            expiracion,
            conn=conn,
        )

    # --- Auditoría ---

    def _scope_con_usuario(
        self,
        scope: dict | None,
        rut_usuario: str,
        id_sesion: str,
    ) -> dict | None:
        if not self.audit_service:
            return scope
        return self.audit_service.con_usuario(scope, rut_usuario, id_sesion)

    def _auditar_exito(
        self,
        rut_usuario: str,
        id_sesion: str,
        scope: dict | None,
        conn: Connection[DictRow] | None,
    ) -> None:
        if not self.audit_service:
            return
        # El contexto del middleware todavía no conoce al usuario (recién se
        # acaba de autenticar), así que se enriquece con el RUT y la sesión.
        scope = self._scope_con_usuario(scope, rut_usuario, id_sesion)
        self.audit_service.log(
            event_type=TipoEvento.LOGIN_SUCCESS,
            category=Categoria.AUTHENTICATION,
            result=Resultado.SUCCESS,
            scope=self._scope_con_usuario(scope, rut_usuario, id_sesion),
            description='Inicio de sesión correcto',
            conn=conn,
        )
        self.audit_service.log(
            event_type=TipoEvento.SESSION_CREATED,
            category=Categoria.SESSION,
            result=Resultado.SUCCESS,
            scope=self._scope_con_usuario(scope, rut_usuario, id_sesion),
            description='Sesión creada',
            resource_type='Sesion',
            resource_id=id_sesion,
            conn=conn,
        )

    def _auditar_fallo(
        self,
        rut: str,
        scope: dict | None,
        conn: Connection[DictRow] | None,
    ) -> None:
        if not self.audit_service:
            return
        self.audit_service.log(
            event_type=TipoEvento.LOGIN_FAILED,
            category=Categoria.AUTHENTICATION,
            result=Resultado.FAILED,
            scope=scope,
            description=MOTIVO_CREDENCIALES,
            error_code=MOTIVO_CREDENCIALES,
            # El RUT ingresado se guarda en metadata, no como rut_usuario: si el
            # usuario no existe o está deshabilitado, la identidad del actor es
            # desconocida y no debe quedar como si fuera válida.
            metadata={'rut_ingresado': rut},
            conn=conn,
        )
