from fastapi import UploadFile
from datetime import datetime, timezone
import os

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.usuario.usuario import Usuario


class SubirEstudioComercialUseCase:
    def __init__(
        self,
        repositorio_estudios: RepositorioEstudiosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso,
    ):
        self.repositorio_estudios = repositorio_estudios
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, archivo: UploadFile, id_solicitud: int,usuario: Usuario) -> tuple[int, str]:
        
        timestamp_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        nombre_unico = f'estudio_comercial_{id_solicitud}_{timestamp_ms}.pdf'
        ruta = f'documentos/estudios_finales/{nombre_unico}'
    
        os.makedirs('documentos/estudios_finales', exist_ok=True)
    
        with open(ruta, 'wb') as f:
            f.write(archivo.file.read())
    
        id_estudio, id_proceso_comercial = self.repositorio_estudios.insertar(
            id_solicitud=id_solicitud, nombre_archivo=nombre_unico, rut_usuario=usuario.rut
        )

        # El estudio cambia el estado del proceso: la alerta de permanencia en
        # el estado anterior deja de ser relevante.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(
            id_proceso_comercial, TIPOS_ALERTA_SLA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )

        return id_estudio, nombre_unico
