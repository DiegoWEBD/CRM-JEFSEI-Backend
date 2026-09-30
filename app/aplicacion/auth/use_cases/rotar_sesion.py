from datetime import datetime, timedelta, timezone

from psycopg import Connection
from psycopg.rows import DictRow

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auth.dtos.sesion_response_dto import RotarSesionResponseDTO
from app.aplicacion.auditoria.audit_service import AuditService
from app.core.config import settings
from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento
from app.dominio.auditoria.repositorio_sesiones import RepositorioSesiones, TokenRotadoInvalido
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class RotarSesionUseCase:

    def __init__(
        self,
        repositorio_sesiones: RepositorioSesiones,
        repositorio_usuarios: RepositorioUsuarios,
        authentication_service: AuthenticationService,
        audit_service: AuditService | None = None,
    ) -> None:
        self.repositorio_sesiones = repositorio_sesiones
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service
        self.audit_service = audit_service

    def execute(
        self,
        refresh_token: str,
        scope: dict | None = None,
        conn: Connection[DictRow] | None = None,
    ) -> RotarSesionResponseDTO:
        if not refresh_token:
            raise TokenRotadoInvalido('TOKEN_AUSENTE')

        token_hash = self.authentication_service.hashear_refresh_token(refresh_token)
        fila = self.repositorio_sesiones.obtener_refresh_token_por_hash(token_hash, conn=conn)

        if not fila:
            raise TokenRotadoInvalido('TOKEN_DESCONOCIDO')

        ahora = datetime.now(timezone.utc)

        if fila['fecha_expiracion'] <= ahora:
            raise TokenRotadoInvalido('TOKEN_EXPIRADO')

        sesion = self.repositorio_sesiones.obtener_por_id(str(fila['id_sesion']))

        if sesion is None:
            raise TokenRotadoInvalido('SESION_INEXISTENTE')

        if sesion.esta_revocada():
            self._auditar(
                TipoEvento.SESSION_REVOKED, Resultado.DENIED, sesion.rut_usuario,
                sesion.id, 'Intento de refresh sobre una sesión revocada', scope, conn,
                error_code='SESSION_REVOKED',
            )
            raise TokenRotadoInvalido('SESION_REVOCADA')

        if sesion.esta_vencida(ahora):
            self._auditar(
                TipoEvento.SESSION_EXPIRED, Resultado.FAILED, sesion.rut_usuario,
                sesion.id, 'La sesión expiró antes de refrescar el token', scope, conn,
                error_code='SESSION_EXPIRED',
            )
            raise TokenRotadoInvalido('SESION_EXPIRADA')

        if fila['usado']:
            # Token ya canjeado. Puede ser una rotación duplicada legítima (el
            # BFF dispara llamadas en paralelo) o un robo. La caché de rotación
            # distingue los dos casos: si la rotación original aún está dentro
            # de la ventana de gracia, se devuelve ese mismo par.
            desde_cache = self._desde_cache(token_hash)
            if desde_cache is not None:
                return desde_cache

            # Fuera de la ventana: se asume robo y se cae la sesión completa.
            self.repositorio_sesiones.revocar(
                sesion.id, 'REFRESH_TOKEN_REUTILIZADO', conn=conn
            )
            self.repositorio_sesiones.revocar_refresh_tokens_de_sesion(sesion.id, conn=conn)
            self._auditar(
                TipoEvento.SESSION_REUSE_DETECTED, Resultado.DENIED, sesion.rut_usuario,
                sesion.id,
                'Refresh token reutilizado fuera de la ventana de gracia: '
                'la sesión fue revocada por posible robo',
                scope, conn, error_code='REFRESH_TOKEN_REUTILIZADO',
            )
            raise TokenRotadoInvalido('REFRESH_TOKEN_REUTILIZADO', revocar_sesion=True)

        return self._rotar(fila, sesion, token_hash, ahora, scope, conn)

    def _rotar(
        self,
        fila: dict,
        sesion,
        token_hash: str,
        ahora: datetime,
        scope: dict | None,
        conn: Connection[DictRow] | None,
    ) -> RotarSesionResponseDTO:
        usuario = self.repositorio_usuarios.buscar(sesion.rut_usuario)

        if not usuario or not usuario.habilitado or usuario.eliminado:
            self.repositorio_sesiones.revocar(
                sesion.id, 'USUARIO_NO_HABILITADO', conn=conn
            )
            raise TokenRotadoInvalido('USUARIO_NO_HABILITADO')

        claims = {
            'rut': usuario.rut,
            'nombre': usuario.nombre,
            'codigo_roles': [rol.codigo for rol in usuario.roles],
            'nombre_roles': [rol.nombre for rol in usuario.roles],
            'codigo_permisos': list(set(
                permiso.codigo
                for rol in usuario.roles
                for permiso in rol.permisos
            )),
        }
        access_token = self.authentication_service.crear_access_token_de_sesion(
            claims, sesion.id
        )
        nuevo_refresh = self.authentication_service.crear_refresh_token(sesion.id)

        self.repositorio_sesiones.marcar_refresh_token_usado(str(fila['id']), conn=conn)
        self.repositorio_sesiones.revocar_refresh_tokens_older_than(
            sesion.id, self.repositorio_sesiones.crear_refresh_token(
                sesion.id,
                self.authentication_service.hashear_refresh_token(nuevo_refresh),
                ahora + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
                conn=conn,
            ),
            conn=conn,
        )
        self.repositorio_sesiones.registrar_uso(sesion.id, conn=conn)

        respuesta = RotarSesionResponseDTO(
            access_token=access_token,
            refresh_token=nuevo_refresh,
            id_sesion=sesion.id,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        self._cache_rotacion().guardar(token_hash, respuesta)

        self._auditar(
            TipoEvento.SESSION_REFRESHED, Resultado.SUCCESS, sesion.rut_usuario,
            sesion.id, 'Rotación de token de sesión', scope, conn,
        )
        return respuesta

    def _desde_cache(self, token_hash: str) -> RotarSesionResponseDTO | None:
        cache = self._cache_rotacion()
        if cache is None:
            return None
        valor = cache.obtener(token_hash)
        return valor if isinstance(valor, RotarSesionResponseDTO) else None

    @staticmethod
    def _cache_rotacion():
        from app.infraestructura.auditoria.cache_rotacion import cache_rotacion
        return cache_rotacion

    def _auditar(
        self,
        tipo: TipoEvento,
        resultado: Resultado,
        rut_usuario: str,
        id_sesion: str,
        descripcion: str,
        scope: dict | None,
        conn: Connection[DictRow] | None,
        error_code: str | None = None,
    ) -> None:
        if not self.audit_service:
            return
        scope = self.audit_service.con_usuario(scope, rut_usuario, id_sesion)
        self.audit_service.log(
            event_type=tipo,
            category=Categoria.SESSION,
            result=resultado,
            scope=scope,
            description=descripcion,
            resource_type='Sesion',
            resource_id=id_sesion,
            error_code=error_code,
            conn=conn,
        )
