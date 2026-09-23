from datetime import datetime, timezone

from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


# Umbral de aviso: al consumir el 70% del plazo la oportunidad queda "próximo a vencer".
UMBRAL_POR_VENCER = 0.70

# Mapa rol_responsable -> campo del proceso que contiene al destinatario.
# Sin fallback: un rol fuera del mapa no genera alerta.
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

        creadas: list[Notificacion] = []

        for proceso in self.repositorio_notificaciones.obtener_procesos_alertables():
            notificacion = self._evaluar(proceso, ahora)

            if notificacion is None:
                continue

            if self.repositorio_notificaciones.registrar(notificacion):
                creadas.append(notificacion)

        return creadas

    def _evaluar(self, proceso: ProcesoAlertableSla, ahora: datetime) -> Notificacion | None:
        if proceso.cerrado:
            return None

        # El límite vive en el ESTADO (nullable): sin límite no hay alerta.
        if proceso.dias_limite is None or proceso.dias_limite <= 0:
            return None

        rut_destinatario = self._resolver_destinatario(proceso)
        if rut_destinatario is None:
            return None

        dias_transcurridos = (ahora - proceso.fecha_ingreso_estado).days
        consumido = dias_transcurridos / proceso.dias_limite

        if consumido < UMBRAL_POR_VENCER:
            return None

        if consumido <= 1.0:
            codigo_tipo = 'SLA_POR_VENCER'
            nivel = 'AVISO'
            titulo = f'Oportunidad próximo al límite en {proceso.nombre_estado}'
            mensaje = (
                f'{self._nombre_proceso(proceso)} lleva {dias_transcurridos} de '
                f'{proceso.dias_limite} días en {proceso.nombre_estado} '
                f'(restan {proceso.dias_limite - dias_transcurridos} días).'
            )
        else:
            codigo_tipo = 'SLA_VENCIDO'
            nivel = 'CRITICO'
            atraso = dias_transcurridos - proceso.dias_limite
            titulo = f'Oportunidad fuera de plazo en {proceso.nombre_estado}'
            mensaje = (
                f'{self._nombre_proceso(proceso)} lleva {dias_transcurridos} de '
                f'{proceso.dias_limite} días en {proceso.nombre_estado} '
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
            entidad_id=proceso.id_proceso_comercial,
            url_destino=f'/oportunidades?id={proceso.id_proceso_comercial}',
            dedupe_key=f'{codigo_tipo}:{proceso.id_proceso_comercial}:{proceso.codigo_estado}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
        )

    def _resolver_destinatario(self, proceso: ProcesoAlertableSla) -> str | None:
        if proceso.rol_responsable is None:
            return None

        campo = CAMPO_POR_ROL.get(proceso.rol_responsable)
        if campo is None:
            return None

        return getattr(proceso, campo, None)

    @staticmethod
    def _nombre_proceso(proceso: ProcesoAlertableSla) -> str:
        if proceso.nombre_prospecto:
            return proceso.nombre_prospecto
        return f'Oportunidad #{proceso.id_proceso_comercial}'
