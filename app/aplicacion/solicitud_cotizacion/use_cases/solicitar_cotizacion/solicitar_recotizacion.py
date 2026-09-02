from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.actividad_accidentes_personales.actividad_accidentes_personales import ActividadAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.solicitud_cotizacion_accidentes_personales import SolicitudCotizacionAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_responsabilidad_civil.solicitud_cotizacion_responsabilidad_civil import SolicitudCotizacionResponsabilidadCivil
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.solicitud_cotizacion_unidades import SolicitudCotizacionUnidades
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_vida_guardia.solicitud_cotizacion_vida_guardia import SolicitudCotizacionVidaGuardia
from app.dominio.usuario.usuario import Usuario


class SolicitarRecotizacionUseCase:

    def __init__(
        self, 
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.authorization_service = authorization_service

    def ejecutar(self, request: SolicitudCotizacionRequest, id_proceso_comercial: int, usuario: Usuario):

        proceso_comercial = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso_comercial:
            raise RecursoNoEncontradoException('Proceso comercial no encontrado')
        
        if not self.authorization_service.usuario_puede_solicitar_cotizacion(usuario, proceso_comercial.id):
            raise UsuarioNoAutorizadoException    

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
                fecha=datetime.now(tz=timezone.utc),
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=True,
                motivo_recotizacion=request.motivo_recotizacion,
                actividades=actividades
            )

        elif request.tipo == 'unidades':
            if request.monto_asegurado_total is None or request.nombre_excel is None:
                raise ConflictoEnAccionException('El tipo unidades requiere los campos monto_asegurado_total y nombre_excel')

            solicitud = SolicitudCotizacionUnidades(
                id=None,
                fecha=datetime.now(tz=timezone.utc),
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=True,
                motivo_recotizacion=request.motivo_recotizacion,
                monto_asegurado_total=request.monto_asegurado_total,
                nombre_excel=request.nombre_excel
            )

        elif request.tipo == 'vida_guardia':
            if request.numero_guardias is None:
                raise ConflictoEnAccionException('El tipo vida_guardia requiere el campo numero_guardias')

            solicitud = SolicitudCotizacionVidaGuardia(
                id=None,
                fecha=datetime.now(tz=timezone.utc),
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=True,
                motivo_recotizacion=request.motivo_recotizacion,
                numero_guardias=request.numero_guardias
            )

        elif request.tipo == 'rc_condominio':
            if request.actividad_del_condominio is None or request.limite is None:
                raise ConflictoEnAccionException('El tipo rc_condominio requiere los campos actividad_del_condominio y limite')

            solicitud = SolicitudCotizacionResponsabilidadCivil(
                id=None,
                fecha=datetime.now(tz=timezone.utc),
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=True,
                motivo_recotizacion=request.motivo_recotizacion,
                actividad_del_condominio=request.actividad_del_condominio,
                limite=request.limite
            )

        else:
            solicitud = SolicitudCotizacion(
                id=None,
                fecha=datetime.now(tz=timezone.utc),
                nombre_riesgo='',
                informacion_completa=False,
                rut_ejecutivo_comercial=usuario.rut,
                nombre_ejecutivo_comercial=usuario.rut,
                prioridad=request.prioridad,
                observaciones=request.observaciones,
                tipo=request.tipo,
                producto='',
                recotizacion=True,
                motivo_recotizacion=request.motivo_recotizacion
            )
            
        self.repositorio_solicitudes_cotizacion.registrar_solicitud_recotizacion(
            solicitud=solicitud,
            id_proceso_comercial=proceso_comercial.id,
            registrado_por=usuario
        )
