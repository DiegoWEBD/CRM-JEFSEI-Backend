from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.actividad_accidentes_personales.actividad_accidentes_personales import ActividadAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.solicitud_cotizacion_accidentes_personales import SolicitudCotizacionAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_responsabilidad_civil.solicitud_cotizacion_responsabilidad_civil import SolicitudCotizacionResponsabilidadCivil
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_vida_guardia.solicitud_cotizacion_vida_guardia import SolicitudCotizacionVidaGuardia
from app.dominio.usuario.usuario import Usuario


class SolicitarCotizacionUseCase:

    def __init__(
        self, 
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        authorization_service: AuthorizationService,
        repositorio_estados: RepositorioEstadosProcesoComercial,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        servicio_alertas: ServicioAlertasProceso,
    ) -> None:
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.authorization_service = authorization_service
        self.repositorio_estados = repositorio_estados
        self.repositorio_historial = repositorio_historial
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, id_proceso_comercial: int, request: SolicitudCotizacionRequest, usuario: Usuario):

        proceso_comercial = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso_comercial:
            raise RecursoNoEncontradoException('Proceso comercial no encontrado')
        
        if not self.authorization_service.usuario_puede_solicitar_cotizacion(usuario, proceso_comercial.id):
            raise UsuarioNoAutorizadoException    

        nuevo_estado = self.repositorio_estados.obtener_por_codigo('COTIZACION_SOLICITADA_COMPANY')
        
        if not nuevo_estado:
            raise ConflictoEnAccionException('Error al solicitar cotización')

        ahora = datetime.now(tz=timezone.utc)
        solicitud: SolicitudCotizacion

        if request.tipo == 'accidentes_personales':
            if request.actividades is None:
                raise ConflictoEnAccionException('El tipo accidentes_personales requiere el campo actividades')

            actividades: list[ActividadAccidentesPersonales] = []

            for actividad_request in request.actividades:
                actividades.append(ActividadAccidentesPersonales(
                    actividad=actividad_request.actividad,
                    numero_asegurados=actividad_request.numero_asegurados
                ))

            solicitud = SolicitudCotizacionAccidentesPersonales(
                id=None,
                fecha=ahora,
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=False,
                motivo_recotizacion=None,
                actividades=actividades
            )

        elif request.tipo == 'vida_guardia':
            if request.numero_guardias is None:
                raise ConflictoEnAccionException('El tipo vida_guardia requiere el campo numero_guardias')

            solicitud = SolicitudCotizacionVidaGuardia(
                id=None,
                fecha=ahora,
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=False,
                motivo_recotizacion=None,
                numero_guardias=request.numero_guardias
            )

        elif request.tipo == 'rc_condominio':
            if request.actividad_del_condominio is None or request.limite is None:
                raise ConflictoEnAccionException('El tipo rc_condominio requiere los campos actividad_del_condominio y limite')

            solicitud = SolicitudCotizacionResponsabilidadCivil(
                id=None,
                fecha=ahora,
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=False,
                motivo_recotizacion=None,
                actividad_del_condominio=request.actividad_del_condominio,
                limite=request.limite
            )

        else:
            solicitud = SolicitudCotizacion(
                id=None,
                fecha=ahora,
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=False,
                motivo_recotizacion=None,
                monto_asegurado=request.monto_asegurado
            )
            
        self.repositorio_solicitudes_cotizacion.nueva_solicitud(
            solicitud=solicitud,
            id_proceso_comercial=proceso_comercial.id
        )

        proceso_comercial.estado_actual = nuevo_estado

        historial = HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso_comercial.id,
            codigo_estado=nuevo_estado.codigo,
            rut_registrado_por=usuario.rut,
            fecha=ahora
        )

        self.repositorio_procesos_comerciales.guardar(proceso_comercial)
        self.repositorio_historial.registrar(historial)

        # La solicitud cambia el estado del proceso: la alerta de permanencia
        # en el estado anterior deja de ser relevante.
        destinatarios = self.servicio_alertas.marcar_leidas(
            proceso_comercial.id, TIPOS_ALERTA_SLA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )
