from datetime import datetime, timezone

from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.archivos import DIRECTORIO_ESTUDIOS_FINALES
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class SubirEstudioComercialUseCase:
    def __init__(
        self,
        repositorio_estudios: RepositorioEstudiosComerciales,
        repositorio_procesos: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso,
        servicio_archivos: ServicioArchivos,
    ):
        self.repositorio_estudios = repositorio_estudios
        self.repositorio_procesos = repositorio_procesos
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas
        self.servicio_archivos = servicio_archivos

    def ejecutar(self, contenido_archivo: bytes, id_solicitud: int, usuario: Usuario) -> tuple[int, str]:

        timestamp_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        nombre_unico = f'estudio_comercial_{id_solicitud}_{timestamp_ms}.pdf'

        self.servicio_archivos.guardar(DIRECTORIO_ESTUDIOS_FINALES, nombre_unico, contenido_archivo)

        id_estudio = self.repositorio_estudios.insertar(
            id_solicitud=id_solicitud, nombre_archivo=nombre_unico, rut_usuario=usuario.rut
        )

        # El estudio cambia el estado del proceso: la alerta de permanencia en
        # el estado anterior deja de ser relevante.
        proceso_comercial = self.repositorio_procesos.buscar_por_solicitud_cotizacion(id_solicitud)

        if proceso_comercial is not None:
            ahora = datetime.now(tz=timezone.utc)
            destinatarios = self.servicio_alertas.marcar_leidas(
                proceso_comercial.id, TIPOS_ALERTA_SLA, ahora
            )

            if destinatarios:
                hub.publicar_desde_hilo(
                    destinatarios,
                    {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
                )

        return id_estudio, nombre_unico