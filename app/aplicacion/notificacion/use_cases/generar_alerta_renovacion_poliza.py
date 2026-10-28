from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from app.aplicacion.notificacion.notificacion_factory import NotificacionFactory
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.poliza_alertable_renovacion import PolizaAlertableRenovacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import ROL_EJECUTIVO_RENOVACION

DIAS_ANTICIPACION_GESTION = 20

ZONA_NEGOCIO = ZoneInfo('America/Santiago')


class GenerarAlertaRenovacionPolizaUseCase:
    """Alertas de renovación de UNA póliza.

    Evalúa el fin de vigencia de la póliza y construye las alertas que
    correspondan para los responsables de renovación del cliente. Es la única
    dueña de la lógica de alertas de renovación (hitos, niveles,
    destinatarios, mensajes y dedupe_key); el barrido del scheduler delega
    aquí.

    No registra ni publica: solo construye las alertas. El registro es
    idempotente gracias a la dedupe_key estable y la publicación en el hub la
    hace el caso de uso llamante, que conoce el conjunto completo de
    destinatarios a refrescar.
    """

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones
        self._cache_ruts_renovacion: list[str] | None = None

    def evaluar(self, poliza: PolizaAlertableRenovacion, ahora: datetime) -> list[Notificacion]:
        """Construye las alertas de renovación que corresponden a la póliza."""
        if poliza.tiene_proceso_renovacion:
            return []

        destinatarios = self._resolver_destinatarios(poliza)

        if not destinatarios:
            return []

        # Compara y formatea por día de calendario en la zona de negocio: el
        # fin de vigencia es una fecha (medianoche en America/Santiago), pero
        # el instante guardado puede caer en el día siguiente en UTC (p. ej.
        # 2026-08-30 00:00+00 es el 29-08 en Santiago).
        fin_santiago = poliza.fin_vigencia.astimezone(ZONA_NEGOCIO)
        ahora_santiago = ahora.astimezone(ZONA_NEGOCIO)

        fecha_cotizacion = fin_santiago - relativedelta(months=2)
        fecha_gestion = fin_santiago - timedelta(days=DIAS_ANTICIPACION_GESTION)
        fecha_vencimiento = fin_santiago.strftime('%d-%m-%Y')

        alertas: list[Notificacion] = []

        if ahora_santiago >= fecha_cotizacion:
            alertas.extend(self._crear_alertas(
                poliza=poliza,
                destinatarios=destinatarios,
                codigo_tipo='RENOVACION_COTIZACION_PENDIENTE',
                nivel='AVISO',
                titulo='Iniciar cotización de renovación',
                mensaje=(
                    f'El día {fecha_vencimiento} vence la póliza {poliza.numero_poliza}, '
                    'por lo que debe comenzar a cotizar para su renovación'
                ),
                ahora=ahora,
            ))

        if ahora_santiago >= fecha_gestion:
            alertas.extend(self._crear_alertas(
                poliza=poliza,
                destinatarios=destinatarios,
                codigo_tipo='RENOVACION_GESTION_PENDIENTE',
                nivel='AVISO',
                titulo='Gestionar renovación',
                mensaje=(
                    f'El día {fecha_vencimiento} vence la póliza {poliza.numero_poliza}, '
                    'por lo que debe gestionar su renovación'
                ),
                ahora=ahora,
            ))

        if ahora_santiago >= fin_santiago:
            alertas.extend(self._crear_alertas(
                poliza=poliza,
                destinatarios=destinatarios,
                codigo_tipo='RENOVACION_POLIZA_VENCIDA',
                nivel='CRITICO',
                titulo='Póliza vencida sin renovación',
                mensaje=(
                    f'La póliza {poliza.numero_poliza} venció el {fecha_vencimiento} '
                    'y no tiene un proceso de renovación iniciado'
                ),
                ahora=ahora,
            ))

        return alertas

    def _crear_alertas(
        self,
        poliza: PolizaAlertableRenovacion,
        destinatarios: list[str],
        codigo_tipo: str,
        nivel: str,
        titulo: str,
        mensaje: str,
        ahora: datetime,
    ) -> list[Notificacion]:
        return [
            NotificacionFactory.crear_alerta_renovacion(
                rut_usuario=rut,
                codigo_tipo=codigo_tipo,
                nivel=nivel,
                titulo=titulo,
                mensaje=mensaje,
                numero_poliza=poliza.numero_poliza,
                fin_vigencia=poliza.fin_vigencia,
                id_prospecto=poliza.id_prospecto,
                ahora=ahora,
            )
            for rut in destinatarios
        ]

    def _resolver_destinatarios(self, poliza: PolizaAlertableRenovacion) -> list[str]:
        """Ejecutivo y asistente de renovación asignados al cliente.

        Si el cliente no tiene ninguno asignado, cae al fan-out por rol
        EJECUTIVO_RENOVACION: una póliza vencida no puede quedar sin alertar.
        """
        asignados = {
            rut for rut in (poliza.rut_ej_renovacion, poliza.rut_as_renovacion) if rut
        }

        if asignados:
            return sorted(asignados)

        if self._cache_ruts_renovacion is None:
            self._cache_ruts_renovacion = self.repositorio_notificaciones.obtener_ruts_por_roles(
                [ROL_EJECUTIVO_RENOVACION]
            ).get(ROL_EJECUTIVO_RENOVACION, [])

        return list(self._cache_ruts_renovacion)
