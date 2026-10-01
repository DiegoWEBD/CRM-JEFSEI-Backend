import json
import logging
import time
import uuid

from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.core.config import settings
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from app.infraestructura.auditoria.descripciones.construir_descripcion import construir_descripcion_accion
from app.infraestructura.auditoria.descripciones.resolvedor_nombres import ResolvedorNombres
from app.infraestructura.auditoria.repositorio_auditoria_postgres import RepositorioAuditoriaPostgres
from app.infraestructura.auditoria.resolucion_ip import resolver_ip_origen

logger = logging.getLogger('auditoria')

METODOS_AUDITADOS = {'POST', 'PUT', 'PATCH', 'DELETE'}

# Los eventos de autenticación se registran explícitamente en el flujo de
# login/logout; auditarlos también aquí duplicaría registros.
PREFIJOS_EXCLUIDOS = ('/auth/',)

# Peticiones que mutan por método pero no por significado: son consultas
# (p. ej. el reporte filtrado de procesos comerciales) y solo ensucian la
# bitácora.
RUTAS_NO_AUDITADAS = {'/procesos-comerciales/reportes'}

# Cuerpo observado solo para describir la acción; nunca se almacena el body
# crudo y se descarta si excede el tope (p. ej. subidas de archivos).
MAX_BYTES_BODY = 64 * 1024

EVENTO_POR_METODO = {
    'PUT': EventoAuditoria.ACTUALIZAR,
    'PATCH': EventoAuditoria.ACTUALIZAR,
    'DELETE': EventoAuditoria.ELIMINAR,
}


def clasificar_evento(metodo: str, ruta: str) -> str:
    if metodo in EVENTO_POR_METODO:
        return EVENTO_POR_METODO[metodo]

    segmentos = [segmento for segmento in ruta.split('/') if segmento]
    if metodo == 'POST' and len(segmentos) == 1:
        return EventoAuditoria.CREAR

    return EventoAuditoria.EJECUTAR_ACCION


def parsear_entidad(ruta: str) -> tuple[str | None, str | None]:
    segmentos = [segmento for segmento in ruta.split('/') if segmento]
    if not segmentos:
        return None, None

    entidad_tipo = segmentos[0]
    entidad_id = segmentos[1] if len(segmentos) > 1 else None
    return entidad_tipo, entidad_id


def parsear_body_json(headers: Headers, cuerpo: bytes, truncado: bool) -> dict | None:
    if truncado or not cuerpo:
        return None

    content_type = headers.get('content-type', '')
    if 'application/json' not in content_type:
        return None

    try:
        datos = json.loads(cuerpo.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return None

    return datos if isinstance(datos, dict) else None


class MiddlewareAuditoria:
    """Registra todo cambio de estado (POST/PUT/PATCH/DELETE) en RegistroAuditoria.

    La escritura ocurre tras responder, en el threadpool y con la identidad
    resuelta por get_current_user (scope['state']['usuario']). El body se
    observa al pasar para construir la descripción humana de la acción, sin
    almacenarse nunca. Nunca interrumpe la respuesta aunque la auditoría falle.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.servicio_auditoria = ServicioAuditoria(RepositorioAuditoriaPostgres())
        self.resolvedor_nombres = ResolvedorNombres()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        ruta = scope.get('path', '')
        metodo = scope.get('method', '')

        # Toda petición recibe id_peticion (trazabilidad extremo a extremo) y
        # el id se ecoa en la respuesta; solo las mutaciones que no son de
        # autenticación generan registro de auditoría.
        id_peticion = headers.get('x-request-id') or uuid.uuid4().hex
        scope.setdefault('state', {})['id_peticion'] = id_peticion

        auditar = (
            settings.CRM_AUDITORIA_HABILITADA
            and metodo in METODOS_AUDITADOS
            and not ruta.startswith(PREFIJOS_EXCLUIDOS)
            and ruta.rstrip('/') not in RUTAS_NO_AUDITADAS
        )

        cuerpo = bytearray()
        cuerpo_truncado = False

        if auditar:
            receive_original = receive

            async def receive_observado() -> Message:
                nonlocal cuerpo_truncado
                mensaje = await receive_original()
                if mensaje['type'] == 'http.request' and not cuerpo_truncado:
                    fragmento = mensaje.get('body', b'') or b''
                    if len(cuerpo) + len(fragmento) > MAX_BYTES_BODY:
                        cuerpo_truncado = True
                        cuerpo.clear()
                    else:
                        cuerpo.extend(fragmento)
                return mensaje

            receive = receive_observado

        status_code = 500
        inicio = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message['type'] == 'http.response.start':
                status_code = message['status']
                MutableHeaders(scope=message)['X-Request-ID'] = id_peticion
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Las redirecciones 3xx (p. ej. /prospectos -> /prospectos/) son
            # plomería de transporte: la petición ya auditada es la que realmente
            # ejecuta la acción, con usuario y estado finales.
            if auditar and not (300 <= status_code < 400):
                duracion_ms = int((time.perf_counter() - inicio) * 1000)
                body = parsear_body_json(headers, bytes(cuerpo), cuerpo_truncado)
                await run_in_threadpool(
                    self._registrar_evento,
                    scope, headers, metodo, ruta, status_code, duracion_ms, id_peticion, body,
                )

    def _registrar_evento(
        self,
        scope: Scope,
        headers: Headers,
        metodo: str,
        ruta: str,
        status_code: int,
        duracion_ms: int,
        id_peticion: str,
        body: dict | None,
    ) -> None:
        try:
            usuario = scope.get('state', {}).get('usuario')
            entidad_tipo, entidad_id = parsear_entidad(ruta)
            rut_usuario = getattr(usuario, 'rut', None)
            contexto = ContextoPeticion(
                ip_origen=resolver_ip_origen(headers, scope.get('client', (None,))[0]),
                user_agent=headers.get('user-agent'),
                id_peticion=id_peticion,
            )
            evento_heuristico = clasificar_evento(metodo, ruta)
            evento, descripcion = construir_descripcion_accion(
                metodo=metodo,
                ruta=ruta,
                evento_heuristico=evento_heuristico,
                actor=rut_usuario,
                body=body,
                resolvedor=self.resolvedor_nombres,
            )

            self.servicio_auditoria.registrar_accion_negocio(
                evento=evento,
                resultado=ResultadoAuditoria.EXITO if status_code < 400 else ResultadoAuditoria.FALLIDO,
                contexto=contexto,
                estado_http=status_code,
                rut_usuario=rut_usuario,
                nombre_usuario=getattr(usuario, 'nombre', None),
                metodo=metodo,
                ruta=ruta,
                entidad_tipo=entidad_tipo,
                entidad_id=entidad_id,
                duracion_ms=duracion_ms,
                detalle=descripcion,
            )
        except Exception:
            logger.exception('No se pudo auditar la petición %s %s', metodo, ruta)
