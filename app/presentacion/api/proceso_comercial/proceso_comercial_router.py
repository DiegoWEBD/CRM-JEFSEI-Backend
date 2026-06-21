from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.aplicacion.proceso_comercial.use_cases.cerrar_proceso_comercial import CerrarProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.crear_proceso_comercial import CrearProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.obtener_todos_procesos_comerciales import ObtenerTodosProcesosComercialesUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto import ObtenerProspectoUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import SolicitarCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_recotizacion import SolicitarRecotizacionUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.proceso_comercial.adaptadores.proceso_comercial_json_adapter import ProcesoComercialJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.presentacion.api.proceso_comercial.dependencias.deps import get_cerrar_proceso_comercial_use_case, get_crear_proceso_comercial_use_case, get_filtros, get_obtener_todos_procesos_comerciales_use_case
from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.filtros_procesos_comerciales import FiltrosProcesosComerciales
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial import ReportesProcesoComercialDTO
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import ReportesProcesoComercialCerradoDTO
from app.presentacion.api.proceso_comercial.dto.requests.cerrar_proceso_comercial_request import CerrarProcesoComercialRequest
from app.presentacion.api.proceso_comercial.dto.requests.crear_proceso_comercial_request import CrearProcesoComercialRequest
from app.presentacion.api.prospecto.dependencias.deps import get_obtener_prospecto_use_case
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_solicitar_cotizacion_use_case, get_solicitar_recotizacion_use_case
from app.presentacion.api.solicitud_cotizacion.dto.requests.solicitud_cotizacion_request_union import SolicitudCotizacionRequestUnion

router = APIRouter(prefix='/procesos-comerciales', tags=['ProcesosComerciales'])

@router.post('/reportes', status_code=status.HTTP_200_OK)
def obtener_reportes_procesos_comerciales(
    request: FiltrosProcesosComerciales,
    _ = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES')),
    use_case: ObtenerTodosProcesosComercialesUseCase = Depends(get_obtener_todos_procesos_comerciales_use_case)
):
    procesos_comerciales = use_case.ejecutar(request)

    reportes: list[ReportesProcesoComercialDTO | ReportesProcesoComercialCerradoDTO] = []
    total_procesos = len(procesos_comerciales)
    abiertos = 0
    ganados = 0
    perdidos = 0
    verde = 0
    amarillo = 0
    rojo = 0

    for proceso in procesos_comerciales:
        if not proceso.cerrado:
            abiertos += 1

            fecha_actual = datetime.now(timezone.utc)
            fecha_inicio = proceso.estado_actual.fecha_registro
            limite = proceso.estado_actual.etapa.dias_limite

            # si no hay SLA definido
            if not fecha_inicio or not limite:
                continue

            dias_transcurridos = int((fecha_actual - fecha_inicio).total_seconds() / 86400)

            porcentaje = dias_transcurridos / limite
            estado_semaforo: EstadoSemaforo
            mensaje_semaforo: str

            if porcentaje < 0.70:
                verde += 1
                estado_semaforo = EstadoSemaforo.VERDE
                mensaje_semaforo = f'Dentro del plazo ({dias_transcurridos} de {limite} días)'

            elif porcentaje <= 1.0:
                amarillo += 1
                estado_semaforo = EstadoSemaforo.AMARILLO
                mensaje_semaforo = f'Próximo a vencer ({dias_transcurridos} de {limite} días)'

            else:
                rojo += 1
                estado_semaforo = EstadoSemaforo.ROJO
                mensaje_semaforo = f'Fuera de plazo (+{dias_transcurridos - limite} días de atraso)'

            reportes.append(ReportesProcesoComercialDTO(
                proceso=ProcesoComercialJsonAdapter(proceso).to_json(),
                fecha_ingreso_etapa=fecha_inicio.isoformat(),
                dias_transcurridos=dias_transcurridos,
                porentaje_sla_consumido=porcentaje,
                estado_semaforo=estado_semaforo,
                dias_restantes=limite - dias_transcurridos,
                dias_atraso=dias_transcurridos-limite,
                mensaje_semaforo=mensaje_semaforo
            ))

        elif proceso.estado_actual.codigo == 'GANADO':
            ganados += 1
            reportes.append(ReportesProcesoComercialCerradoDTO(
                proceso=ProcesoComercialJsonAdapter(proceso).to_json(),
                estado_semaforo=EstadoSemaforo.NO_APLICA
            ))
            
        elif proceso.estado_actual.codigo == 'PERDIDO':
            perdidos += 1
            reportes.append(ReportesProcesoComercialCerradoDTO(
                proceso=ProcesoComercialJsonAdapter(proceso).to_json(),
                estado_semaforo=EstadoSemaforo.NO_APLICA
            ))


    return reportes

@router.post('/{id}/cerrar')
def cerrar_proceso_comercial(
    id: int,
    request: CerrarProcesoComercialRequest,
    usuario = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES')),
    use_case: CerrarProcesoComercialUseCase = Depends(get_cerrar_proceso_comercial_use_case)
):
    use_case.ejecutar(
        id=id,
        ganado=request.ganado,
        observacion=request.observacion,
        usuario=usuario
    )

    return {
        'message': f'Oportunidad {'ganada' if request.ganado else 'perdida'}'
    }

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_proceso_comercial(
    request: CrearProcesoComercialRequest,
    usuario: Usuario = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES', 'ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS')),
    use_case: CrearProcesoComercialUseCase = Depends(get_crear_proceso_comercial_use_case)
):
    proceso = use_case.ejecutar(
        tipo=request.tipo,
        id_prospecto=request.id_prospecto,
        usuario=usuario
    )

    return {
        'message': 'Oportunidad comercial creada',
        'oportunidad': proceso
    }

@router.post('/{id}/solicitudes-cotizacion', status_code=status.HTTP_201_CREATED)
def solicitar_cotizacion(
    id: int,
    request: SolicitudCotizacionRequestUnion,
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
    use_case: SolicitarCotizacionUseCase = Depends(get_solicitar_cotizacion_use_case)
):
    use_case.ejecutar(id, request, usuario)

    return {
        'message': 'Solicitud de cotización registrada'
    }

@router.post('/{id}/solicitudes-cotizacion/recotizacion', status_code=status.HTTP_201_CREATED)
def solicitar_recotizacion(
    id: int,
    request: SolicitudCotizacionRequestUnion,
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
    use_case: SolicitarRecotizacionUseCase = Depends(get_solicitar_recotizacion_use_case)
):
    if request.motivo_recotizacion is None:
        raise BadRequestException('Debe indicar motivo_recotizacion')

    use_case.ejecutar(
        request=request,
        id_proceso_comercial=id,
        usuario=usuario
    )

    return {
        'message': 'Recotización solicitada'
    }