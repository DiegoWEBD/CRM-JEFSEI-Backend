from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


UMBRAL_DIAS_PROXIMO = 5

ZONA_NEGOCIO = ZoneInfo('America/Santiago')


class GenerarAlertaCierreEstimadoUseCase:
    """Alerta de cierre estimado de UN proceso comercial.

    Evalúa la fecha de cierre estimada del proceso y, si corresponde, crea la
    alerta para el ejecutivo comercial asignado. Es la única dueña de la
    lógica de alertas de cierre (umbrales, destinatario, mensajes y
    dedupe_key); el barrido del scheduler y los casos de uso de asignación /
    fecha de cierre delegan aquí.

    No publica en el hub: la publicación es responsabilidad del caso de uso
    llamante, que conoce el conjunto completo de destinatarios a refrescar.
    """

    def __init__(
        self,
        repositorio_procesos: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
    ) -> None:
        self.repositorio_procesos = repositorio_procesos
        self.repositorio_notificaciones = repositorio_notificaciones

    def evaluar(self, proceso: ProcesoComercial, ahora: datetime) -> Notificacion | None:
        """Construye la alerta que corresponde al proceso, o None si no hay."""
        if proceso.cerrado:
            return None

        if proceso.fecha_estimada_cierre is None:
            return None

        rut_destinatario = self._resolver_destinatario(proceso)
        if rut_destinatario is None:
            return None

        # Compara por fecha de calendario en la zona de negocio: la fecha de
        # cierre se guarda a medianoche, por lo que restar instantes perdía un
        # día completo después de la medianoche (p. ej. "faltan 0 días" para un
        # cierre al día siguiente).
        cierre_santiago = proceso.fecha_estimada_cierre.astimezone(ZONA_NEGOCIO)
        ahora_santiago = ahora.astimezone(ZONA_NEGOCIO)
        dias_restantes = (cierre_santiago.date() - ahora_santiago.date()).days

        if dias_restantes > UMBRAL_DIAS_PROXIMO:
            return None

        desc_proceso = self._descripcion_proceso(proceso)

        if dias_restantes >= 0:
            codigo_tipo = 'CIERRE_ESTIMADO_PROXIMO'
            nivel = 'AVISO'
            titulo = 'Cierre estimado próximo'
            mensaje = (
                f'{desc_proceso} tiene fecha de cierre estimada '
                f'el {proceso.fecha_estimada_cierre.strftime("%d/%m/%Y")} '
                f'(faltan {dias_restantes} días).'
            )
        else:
            codigo_tipo = 'FECHA_CIERRE_VENCIDA'
            nivel = 'CRITICO'
            atraso = abs(dias_restantes)
            titulo = 'Fecha de cierre vencida'
            mensaje = (
                f'{desc_proceso} tiene fecha de cierre estimada '
                f'el {proceso.fecha_estimada_cierre.strftime("%d/%m/%Y")} '
                f'({atraso} días de atraso).'
            )

        return Notificacion(
            id=None,
            rut_usuario=rut_destinatario,
            codigo_tipo=codigo_tipo,
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            entidad_tipo='PROCESO_COMERCIAL',
            entidad_id=proceso.id,
            id_prospecto=proceso.id_prospecto,
            dedupe_key=f'{codigo_tipo}:{proceso.id}:{rut_destinatario}:{ahora.isoformat()}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
            leible=False,
        )

    def ejecutar(self, id_proceso_comercial: int, ahora: datetime | None = None) -> Notificacion | None:
        """Genera la alerta del proceso, o None si no corresponde / no se creó."""
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        proceso = self.repositorio_procesos.buscar(id_proceso_comercial)
        if proceso is None:
            return None

        notificacion = self.evaluar(proceso, ahora)
        if notificacion is None:
            return None

        if self.repositorio_notificaciones.registrar(notificacion):
            return notificacion

        return None

    def _resolver_destinatario(self, proceso: ProcesoComercial) -> str | None:
        if proceso.ejecutivo_comercial is None:
            return None
        return proceso.ejecutivo_comercial.rut

    @staticmethod
    def _descripcion_proceso(proceso: ProcesoComercial) -> str:
        return f"La oportunidad '{proceso.producto.nombre}' de {proceso.nombre_cliente}"
