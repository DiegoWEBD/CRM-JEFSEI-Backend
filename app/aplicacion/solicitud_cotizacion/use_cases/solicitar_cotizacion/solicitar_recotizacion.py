from datetime import datetime
from typing import cast

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_accidentes_personales_request.solicitud_cotizacion_accidentes_personales_request import SolicitudCotizacionAccidentesPersonalesRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_responsabilidad_civil_request import SolicitudCotizacionResponsabilidadCivilRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_unidades_request import SolicitudCotizacionUnidadesRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_vida_guardia_request import SolicitudCotizacionVidaGuardiaRequest
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.actividad_accidentes_personales.actividad_accidentes_personales import ActividadAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.solicitud_cotizacion_accidentes_personales import SolicitudCotizacionAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_responsabilidad_civil.solicitud_cotizacion_responsabilidad_civil import SolicitudCotizacionResponsabilidadCivil
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.solicitud_cotizacion_unidades import SolicitudCotizacionUnidades
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_vida_guardia.solicitud_cotizacion_vida_guardia import SolicitudCotizacionVidaGuardia
from app.dominio.usuario.usuario import Usuario


class SolicitarRecotizacionUseCase:

    def __init__(self, repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion) -> None:
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion

    def ejecutar(self, request: SolicitudCotizacionRequest, id_solicitud_original: int, usuario: Usuario):

        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud_original):
            raise RecursoNoEncontradoException('Solicitud original no encontrada')

        solicitud: SolicitudCotizacion

        if request.tipo == 'accidentes_personales':
            request = cast(SolicitudCotizacionAccidentesPersonalesRequest, request)

            actividades: list[ActividadAccidentesPersonales] = []

            for actividad_request in request.actividades:
                actividades.append(ActividadAccidentesPersonales(
                    actividad=actividad_request.actividad,
                    numero_asegurados=actividad_request.numero_asegurados
                ))

            solicitud = SolicitudCotizacionAccidentesPersonales(
                id=None,
                fecha=datetime.now(),
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
            request = cast(SolicitudCotizacionUnidadesRequest, request)

            solicitud = SolicitudCotizacionUnidades(
                id=None,
                fecha=datetime.now(),
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
            print('VIDA GUARDIA')
            request = cast(SolicitudCotizacionVidaGuardiaRequest, request)
            print(request)

            solicitud = SolicitudCotizacionVidaGuardia(
                id=None,
                fecha=datetime.now(),
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
            request = cast(SolicitudCotizacionResponsabilidadCivilRequest, request)

            solicitud = SolicitudCotizacionResponsabilidadCivil(
                id=None,
                fecha=datetime.now(),
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
                fecha=datetime.now(),
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
            id_solicitud_original=id_solicitud_original,
            registrado_por=usuario
        )