from datetime import datetime, timezone

from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


# Umbral de aviso: al consumir el 70% del plazo la oportunidad queda "próximo a vencer".
UMBRAL_POR_VENCER = 0.7

# Mapa rol_responsable -> campo del proceso que contiene al destinatario asignado.
# Roles fuera de este mapa se resuelven vía fan-out (todos los usuarios activos con ese rol).
CAMPO_POR_ROL: dict[str, str] = {
    'EJECUTIVO_COMERCIAL': 'rut_ej_comercial',
    'EJECUTIVO_EVALUACION_PROYECTOS': 'rut_ej_evaluacion',
}


class GenerarAlertasSlaUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, ahora: datetime | None = None) -> list[Notificacion]:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        # Cache de fan-out por rol: se consulta una vez por ejecución.
        self._cache_ruts_por_rol: dict[str, list[str]] = {}

        creadas: list[Notificacion] = []

        for proceso in self.repositorio_notificaciones.obtener_procesos_alertables():
            for notificacion in self._evaluar(proceso, ahora):
                if self.repositorio_notificaciones.registrar(notificacion):
                    creadas.append(notificacion)

        if creadas:
            hub.publicar_desde_hilo(
                (alerta.rut_usuario for alerta in creadas),
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
            )

        return creadas

    def _evaluar(self, proceso: ProcesoAlertableSla, ahora: datetime) -> list[Notificacion]:
        if proceso.cerrado:
            return []

        # El límite vive en el ESTADO (nullable): sin límite no hay alerta.
        if proceso.dias_limite is None or proceso.dias_limite <= 0:
            return []

        # Sin transición principal -> sin destinatario -> sin alerta.
        if proceso.rol_responsable_siguiente is None:
            return []

        destinatarios = self._resolver_destinatarios(proceso)

        if not destinatarios:
            return []

        dias_transcurridos = (ahora - proceso.fecha_ingreso_estado).days
        consumido = dias_transcurridos / proceso.dias_limite

        if consumido < UMBRAL_POR_VENCER:
            return []

        # Texto descriptivo: acción requerida (preferente) o nombre del siguiente estado (fallback).
        desc_siguiente = ''
        if proceso.accion_requerida:
            desc_siguiente = f' — falta {proceso.accion_requerida}'
        elif proceso.nombre_siguiente_estado:
            desc_siguiente = f' — pendiente en {proceso.nombre_siguiente_estado}'

        if consumido <= 1.0:
            codigo_tipo = 'SLA_POR_VENCER'
            nivel = 'AVISO'
            titulo = f'Oportunidad próximo al límite en {proceso.nombre_estado}'
            mensaje = (
                f'{self._nombre_proceso(proceso)} lleva {dias_transcurridos} de '
                f'{proceso.dias_limite} días en {proceso.nombre_estado}'
                f'{desc_siguiente} '
                f'(restan {proceso.dias_limite - dias_transcurridos} días).'
            )
        else:
            codigo_tipo = 'SLA_VENCIDO'
            nivel = 'CRITICO'
            atraso = dias_transcurridos - proceso.dias_limite
            titulo = f'Oportunidad fuera de plazo en {proceso.nombre_estado}'
            mensaje = (
                f'{self._nombre_proceso(proceso)} lleva {dias_transcurridos} de '
                f'{proceso.dias_limite} días en {proceso.nombre_estado}'
                f'{desc_siguiente} '
                f'({atraso} días de atraso).'
            )

        return [
            Notificacion(
                id=None,
                rut_usuario=rut,
                codigo_tipo=codigo_tipo,
                nivel=nivel,
                titulo=titulo,
                mensaje=mensaje,
                entidad_tipo='PROCESO_COMERCIAL',
                entidad_id=proceso.id_proceso_comercial,
                id_prospecto=proceso.id_prospecto,
                dedupe_key=f'{codigo_tipo}:{proceso.id_proceso_comercial}:{proceso.codigo_estado}:{rut}',
                leida=False,
                fecha_leida=None,
                created_at=ahora,
                leible=False,
            )
            for rut in destinatarios
        ]

    def _resolver_destinatarios(self, proceso: ProcesoAlertableSla) -> list[str]:
        """Resuelve los RUTs destinatarios de la alerta.

        El rol consultado es el del SIGUIENTE estado (destino de la transición
        principal del estado actual).  Si el rol tiene asignación por proceso
        (EJECUTIVO_COMERCIAL, EJECUTIVO_EVALUACION_PROYECTOS), se usa el RUT
        asignado.  Para otros roles se hace fan-out a todos los usuarios activos
        con ese rol.
        """
        rol = proceso.rol_responsable_siguiente
        if rol is None:
            return []

        campo = CAMPO_POR_ROL.get(rol)
        if campo is not None:
            rut = getattr(proceso, campo, None)
            return [rut] if rut else []

        # Fan-out: buscar todos los usuarios activos con el rol.
        if rol not in self._cache_ruts_por_rol:
            self._cache_ruts_por_rol = self.repositorio_notificaciones.obtener_ruts_por_roles(
                [rol]
            )
        return self._cache_ruts_por_rol.get(rol, [])

    @staticmethod
    def _nombre_proceso(proceso: ProcesoAlertableSla) -> str:
        if proceso.nombre_prospecto:
            return proceso.nombre_prospecto
        return f'Oportunidad #{proceso.id_proceso_comercial}'
