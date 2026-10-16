from datetime import datetime, timezone
from uuid import uuid4

from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.cotizacion.cotizacion_factory import CotizacionFactory
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.archivos import DIRECTORIO_COTIZACIONES
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub


class ActualizarCotizacionUseCase:

    def __init__(
        self,
        repositorio_cotizaciones: RepositorioCotizaciones,
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        authorization_service: AuthorizationService,
        servicio_alertas: ServicioAlertasProceso,
        servicio_archivos: ServicioArchivos
    ) -> None:
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_historial = repositorio_historial
        self.authorization_service = authorization_service
        self.servicio_alertas = servicio_alertas
        self.servicio_archivos = servicio_archivos

    def ejecutar(
        self,
        id_cotizacion: int,
        id_solicitud: int,
        rut_usuario: str,
        monto_total_asegurado: float,
        asistencia_afecta: float,
        asistencia_excenta: float,
        id_company: int,
        fecha_emision: str,
        fecha_vencimiento: str,
        tipo: str,
        tasa_afecta: float | None = None,
        tasa_excenta: float | None = None,
        tasa_politica: float | None = None,
        prima_afecta: float | None = None,
        prima_excenta: float | None = None,
        contenido_archivo: bytes | None = None,
        eliminar_archivo: bool = False,
    ):

        # 1. Validar que la solicitud existe

        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud):
            raise RecursoNoEncontradoException('Solicitud no encontrada')

        # 2. Validar permisos (ACTUALIZAR_COTIZACION + ejecutivo asignado)

        if not self.authorization_service.usuario_puede_actualizar_cotizacion(rut_usuario, id_solicitud):
            raise UsuarioNoAutorizadoException

        # 3. Validar que el proceso comercial esté abierto

        proceso = self.repositorio_procesos_comerciales.buscar_por_solicitud_cotizacion(id_solicitud)
        if proceso is None:
            raise RecursoNoEncontradoException('Proceso comercial no encontrado')
        if proceso.cerrado:
            raise ConflictoEnAccionException(
                'No se puede actualizar una cotización de una oportunidad cerrada'
            )

        # 4. Validar que la cotización existe

        cotizacion = self.repositorio_cotizaciones.obtener_por_id(id_cotizacion)

        if cotizacion is None:
            raise RecursoNoEncontradoException('Cotización no encontrada')

        # 5. Resolución de archivo: guardar nuevo, eliminar o mantener

        nombre_archivo_previo = cotizacion.nombre_archivo

        if contenido_archivo is not None:
            nombre_archivo = f'cotizacion_{id_solicitud}_{uuid4().hex}.pdf'
            self.servicio_archivos.guardar(DIRECTORIO_COTIZACIONES, nombre_archivo, contenido_archivo)
            self.servicio_archivos.eliminar(DIRECTORIO_COTIZACIONES, nombre_archivo_previo)
        elif eliminar_archivo:
            self.servicio_archivos.eliminar(DIRECTORIO_COTIZACIONES, nombre_archivo_previo)
            nombre_archivo = None
        else:
            nombre_archivo = nombre_archivo_previo

        # 6. Construir el objeto Cotizacion con recálculo vía CotizacionFactory

        cotizacion = CotizacionFactory.crear(
            monto_total_asegurado=monto_total_asegurado,
            asistencia_afecta=asistencia_afecta,
            asistencia_excenta=asistencia_excenta,
            id_company=id_company,
            fecha_emision=datetime.fromisoformat(fecha_emision),
            fecha_vencimiento=datetime.fromisoformat(fecha_vencimiento),
            tipo=tipo,
            tasa_afecta=tasa_afecta,
            tasa_excenta=tasa_excenta,
            tasa_politica=tasa_politica,
            prima_afecta=prima_afecta,
            prima_excenta=prima_excenta,
            nombre_archivo=nombre_archivo,
        )

        # 7. Actualizar cotización

        self.repositorio_cotizaciones.actualizar(id_cotizacion, cotizacion)

        # 8. Registrar historial + actualizar estado_actual
        ahora = datetime.now(tz=timezone.utc)

        historial = HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso.id,
            codigo_estado='COTIZACION_MODIFICADA',
            rut_registrado_por=rut_usuario,
            fecha=ahora
        )
        self.repositorio_historial.registrar(historial)

        # 9. Marcar alertas SLA del estado anterior como leídas
        
        destinatarios = self.servicio_alertas.marcar_leidas(
            proceso.id, TIPOS_ALERTA_SLA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )