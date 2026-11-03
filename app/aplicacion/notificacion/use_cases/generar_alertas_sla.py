import math
from datetime import datetime, timezone

from app.aplicacion.notificacion.notificacion_factory import NotificacionFactory
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import (
    ROL_EJECUTIVO_COMERCIAL,
    ROL_EJECUTIVO_EVALUACION_PROYECTOS,
)
from app.dominio.sla.formato_sla import dias_decimales, formatear_dias_horas


# Umbral de aviso: al consumir el 70% del plazo la oportunidad queda "próximo a vencer".
UMBRAL_POR_VENCER = 0.7

# Tramos de las alertas de permanencia en estado: 70 (aviso previo), 100 (al
# vencer) y luego un recordatorio nuevo cada 30% de consumo adicional
# (130, 160, 190, ...).
TRAMO_POR_VENCER = 70
TRAMO_VENCIDO = 100
PASO_RECORDATORIO_PORCENTAJE = 30

# Mapa rol_responsable -> campo del proceso que contiene al destinatario asignado.
# Roles fuera de este mapa se resuelven vía fan-out (todos los usuarios activos con ese rol).
CAMPO_POR_ROL: dict[str, str] = {
    ROL_EJECUTIVO_COMERCIAL: 'rut_ej_comercial',
    ROL_EJECUTIVO_EVALUACION_PROYECTOS: 'rut_ej_evaluacion',
}


class GenerarAlertasSlaUseCase:

    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso,
    ) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, ahora: datetime | None = None) -> list[Notificacion]:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        # Cache de fan-out por rol: se consulta una vez por ejecución.
        self._cache_ruts_por_rol: dict[str, list[str]] = {}

        creadas: list[Notificacion] = []
        resueltas: list[str] = []

        for proceso in self.repositorio_notificaciones.obtener_procesos_alertables():
            alertas = self._evaluar(proceso, ahora)

            for notificacion in alertas:
                if self.repositorio_notificaciones.registrar(notificacion):
                    creadas.append(notificacion)

            # Escalonamiento: la alerta del tramo actual deja superadas a las
            # anteriores del proceso (aviso de "próximo a vencer" y tramos de
            # vencimiento menores), que se marcan leídas.  Solo aplica una vez
            # vencido: el aviso de "próximo a vencer" no tiene anteriores.
            if alertas and any(n.codigo_tipo == 'SLA_VENCIDO' for n in alertas):
                resueltas.extend(
                    self.servicio_alertas.marcar_leidas_sla_anteriores(
                        proceso.id_proceso_comercial,
                        {notificacion.dedupe_key for notificacion in alertas},
                        ahora,
                    )
                )

        if creadas:
            for alerta in creadas:
                if not alerta.rut_usuario:
                    continue

                hub.publicar_desde_hilo(
                    [alerta.rut_usuario],
                    {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
                )

        if resueltas:
            hub.publicar_desde_hilo(
                resueltas,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )

        return creadas

    def _evaluar(self, proceso: ProcesoAlertableSla, ahora: datetime) -> list[Notificacion]:
        if proceso.cerrado:
            return []

        # El límite vive en la TRANSICIÓN PRINCIPAL del estado (nullable):
        # sin límite no hay alerta.
        if proceso.dias_limite is None or proceso.dias_limite <= 0:
            return []

        # Sin transición principal -> sin destinatario -> sin alerta.
        if proceso.rol_responsable_siguiente is None:
            return []

        destinatarios = self._resolver_destinatarios(proceso)

        if not destinatarios:
            return []

        # Transcurrido con precisión de horas (días decimales, 24/7): el consumo
        # del plazo se evalúa sobre la fracción real, sin truncar a días enteros.
        dias_transcurridos = dias_decimales(proceso.fecha_ingreso_estado, ahora)
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
            tramo = TRAMO_POR_VENCER
            nivel = 'AVISO'
            titulo = f'Oportunidad próximo al límite en {proceso.nombre_estado}'
            mensaje = (
                f'{self._nombre_proceso(proceso)} lleva '
                f'{formatear_dias_horas(dias_transcurridos)} de '
                f'{formatear_dias_horas(proceso.dias_limite)} en {proceso.nombre_estado}'
                f'{desc_siguiente} '
                f'(restan {formatear_dias_horas(proceso.dias_limite - dias_transcurridos)}).'
            )
        else:
            codigo_tipo = 'SLA_VENCIDO'
            tramo = self._tramo_vencido(consumido)
            nivel = 'CRITICO'
            atraso = dias_transcurridos - proceso.dias_limite

            if tramo == TRAMO_VENCIDO:
                titulo = f'Oportunidad fuera de plazo en {proceso.nombre_estado}'
                mensaje = (
                    f'{self._nombre_proceso(proceso)} lleva '
                    f'{formatear_dias_horas(dias_transcurridos)} de '
                    f'{formatear_dias_horas(proceso.dias_limite)} en {proceso.nombre_estado}'
                    f'{desc_siguiente} '
                    f'(+{formatear_dias_horas(atraso)} de atraso).'
                )
            else:
                # Recordatorio de un tramo posterior (130, 160, ...): el texto
                # se basta solo, ya que la alerta del tramo anterior quedó
                # leída.  El porcentaje es el consumo real (como el % Consumido
                # del panel), no el tramo del recordatorio.
                titulo = f'Oportunidad sigue fuera de plazo en {proceso.nombre_estado}'
                mensaje = (
                    f'{self._nombre_proceso(proceso)} lleva '
                    f'{formatear_dias_horas(dias_transcurridos)} de '
                    f'{formatear_dias_horas(proceso.dias_limite)} en {proceso.nombre_estado}'
                    f'{desc_siguiente} '
                    f'(va por el {self._porcentaje_entero(consumido)}% del plazo, '
                    f'+{formatear_dias_horas(atraso)} de atraso).'
                )

        return [
            NotificacionFactory.crear_alerta_sla(
                rut_usuario=rut,
                codigo_tipo=codigo_tipo,
                tramo=tramo,
                nivel=nivel,
                titulo=titulo,
                mensaje=mensaje,
                id_proceso_comercial=proceso.id_proceso_comercial,
                id_prospecto=proceso.id_prospecto,
                codigo_estado=proceso.codigo_estado,
                ahora=ahora,
            )
            for rut in destinatarios
        ]

    @staticmethod
    def _tramo_vencido(consumido: float) -> int:
        """Tramo de recordatorio alcanzado: 100 y luego cada 30% adicional.

        Un consumo exacto de 130% debe caer en el tramo 130: el epsilon
        absorbe el error de coma flotante en los límites (p. ej. 1.3 puede
        calcularse como 1.2999...).
        """
        pasos = math.floor(
            (consumido * 100 - TRAMO_VENCIDO) / PASO_RECORDATORIO_PORCENTAJE + 1e-9
        )
        return TRAMO_VENCIDO + PASO_RECORDATORIO_PORCENTAJE * pasos

    @staticmethod
    def _porcentaje_entero(consumido: float) -> int:
        """Porcentaje del plazo consumido, redondeado a entero half-up.

        El mismo redondeo que el % Consumido del panel (toFixed() del
        frontend), para que la notificación y el panel muestren siempre
        la misma cifra.  Python round() usa banker's rounding y podría
        diferir en un punto en los casos .5.
        """
        return math.floor(consumido * 100 + 0.5)

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
        return f"La oportunidad '{proceso.nombre_producto}' de {proceso.nombre_prospecto}"
