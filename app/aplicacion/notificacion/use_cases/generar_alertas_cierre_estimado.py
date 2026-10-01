from datetime import datetime, timezone

from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


UMBRAL_DIAS_PROXIMO = 5


class GenerarAlertasCierreEstimadoUseCase:

    def __init__(
        self,
        repositorio_procesos: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
    ) -> None:
        self.repositorio_procesos = repositorio_procesos
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, ahora: datetime | None = None) -> list[Notificacion]:
        if ahora is None:
            ahora = datetime.now(tz=timezone.utc)

        creadas: list[Notificacion] = []

        for proceso in self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=None,
            abiertos=True,
        ):
            notificacion = self._evaluar(proceso, ahora)

            if notificacion is None:
                continue

            if self.repositorio_notificaciones.registrar(notificacion):
                creadas.append(notificacion)

        if creadas:
            hub.publicar_desde_hilo(
                (alerta.rut_usuario for alerta in creadas),
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
            )

        return creadas

    def _evaluar(self, proceso, ahora: datetime) -> Notificacion | None:
        if proceso.cerrado:
            return None

        if proceso.fecha_estimada_cierre is None:
            return None

        rut_destinatario = self._resolver_destinatario(proceso)
        if rut_destinatario is None:
            return None

        dias_restantes = (proceso.fecha_estimada_cierre - ahora).days

        if dias_restantes > UMBRAL_DIAS_PROXIMO:
            return None

        if dias_restantes >= 0:
            codigo_tipo = 'CIERRE_ESTIMADO_PROXIMO'
            nivel = 'AVISO'
            titulo = 'Cierre estimado próximo'
            mensaje = (
                f'{self._nombre_proceso(proceso)} tiene fecha de cierre estimada '
                f'el {proceso.fecha_estimada_cierre.strftime("%d/%m/%Y")} '
                f'(faltan {dias_restantes} días).'
            )
        else:
            codigo_tipo = 'FECHA_CIERRE_VENCIDA'
            nivel = 'CRITICO'
            atraso = abs(dias_restantes)
            titulo = 'Fecha de cierre vencida'
            mensaje = (
                f'{self._nombre_proceso(proceso)} tiene fecha de cierre estimada '
                f'el {proceso.fecha_estimada_cierre.strftime("%d/%m/%Y")} '
                f'({atraso} días de atraso).'
            )

        codigo_estado = proceso.estado_actual.codigo if proceso.estado_actual else ''

        return Notificacion(
            id=None,
            rut_usuario=rut_destinatario,
            codigo_tipo=codigo_tipo,
            nivel=nivel,
            titulo=titulo,
            mensaje=mensaje,
            entidad_tipo='PROCESO_COMERCIAL',
            entidad_id=proceso.id,
            url_destino=f'/oportunidades?id={proceso.id}',
            dedupe_key=f'{codigo_tipo}:{proceso.id}:{codigo_estado}',
            leida=False,
            fecha_leida=None,
            created_at=ahora,
        )

    def _resolver_destinatario(self, proceso) -> str | None:
        if proceso.ejecutivo_comercial is None:
            return None
        return proceso.ejecutivo_comercial.rut

    @staticmethod
    def _nombre_proceso(proceso) -> str:
        if proceso.nombre_cliente:
            return proceso.nombre_cliente
        return f'Oportunidad #{proceso.id}'
