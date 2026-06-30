from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.aplicacion.historial_estado.use_cases.obtener_historial_estados_proceso_comercial import ObtenerHistorialEstadosProcesoComercialUseCase
from app.aplicacion.poliza.use_cases.registrar_poliza_a_proceso_comercial import RegistrarPolizaAProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.cerrar_proceso_comercial import CerrarProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.crear_proceso_comercial import CrearProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.obtener_todos_procesos_comerciales import ObtenerTodosProcesosComercialesUseCase
from app.aplicacion.proceso_comercial.use_cases.registrar_aceptacion_cliente import RegistrarAceptacionClienteUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_solicitudes_cotizacion import ObtenerSolicitudesCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import SolicitarCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_recotizacion import SolicitarRecotizacionUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.proceso_comercial.adaptadores.proceso_comercial_json_adapter import ProcesoComercialJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.presentacion.api.historial_estado.dependencias.deps import get_obtener_historial_estados_proceso_comercial_use_case
from app.presentacion.api.historial_estado.mappers.resumen_historial_estado_mapper import ResumenHistorialEstadoMapper
from app.presentacion.api.poliza.dependencias.deps import get_registrar_poliza_a_proceso_comercial_use_case
from app.presentacion.api.proceso_comercial.dependencias.deps import get_cerrar_proceso_comercial_use_case, get_crear_proceso_comercial_use_case, get_obtener_todos_procesos_comerciales_use_case
from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.filtros_procesos_comerciales import FiltrosProcesosComerciales
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial import ReportesProcesoComercialDTO
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import ReportesProcesoComercialCerradoDTO
from app.presentacion.api.proceso_comercial.dto.requests.cerrar_proceso_comercial_request import CerrarProcesoComercialRequest
from app.presentacion.api.proceso_comercial.dto.requests.crear_proceso_comercial_request import CrearProcesoComercialRequest
from app.presentacion.api.proceso_comercial.dto.requests.registrar_poliza_a_proceso_comercial_request import RegistrarPolizaAProcesoComercialRequest
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_obtener_solicitudes_cotizacion_use_case, get_registrar_aceptacion_cliente_use_case, get_solicitar_cotizacion_use_case, get_solicitar_recotizacion_use_case
from app.presentacion.api.solicitud_cotizacion.dto.requests.solicitud_cotizacion_request_union import SolicitudCotizacionRequestUnion

router = APIRouter(prefix='/procesos-comerciales', tags=['ProcesosComerciales'])

@router.post('/reportes', status_code=status.HTTP_200_OK)
def obtener_reportes_procesos_comerciales(
    request: FiltrosProcesosComerciales,
    _ = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES')),
    use_case: ObtenerTodosProcesosComercialesUseCase = Depends(get_obtener_todos_procesos_comerciales_use_case),
    historial_use_case: ObtenerHistorialEstadosProcesoComercialUseCase = Depends(get_obtener_historial_estados_proceso_comercial_use_case)
):
    procesos_comerciales = use_case.ejecutar(request)

    reportes: list[ReportesProcesoComercialDTO | ReportesProcesoComercialCerradoDTO] = []
    total_procesos = len(procesos_comerciales)
    print(total_procesos)
    abiertos = 0
    ganados = 0
    perdidos = 0
    verde = 0
    amarillo = 0
    rojo = 0

    for proceso in procesos_comerciales:
        if not proceso.cerrado:
            historial_estados = historial_use_case.ejecutar(proceso.id)
            historial_por_etapa = ResumenHistorialEstadoMapper(historial_estados).map()
            ingreso_etapa = historial_por_etapa[proceso.estado_actual.etapa.nombre].fecha_entrada_etapa

            if not ingreso_etapa:
                raise BadRequestException('Etapa no identificada')
        
            abiertos += 1

            fecha_actual = datetime.now(timezone.utc)
            fecha_inicio = proceso.estado_actual.fecha_registro
            fecha_ingreso_etapa = datetime.fromisoformat(ingreso_etapa)
            limite = proceso.estado_actual.etapa.dias_limite

            # si no hay SLA definido
            if not fecha_ingreso_etapa or not limite:
                continue

            dias_transcurridos = int((fecha_actual - fecha_ingreso_etapa).total_seconds() / 86400)

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
                fecha_ingreso_etapa=ingreso_etapa,
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


@router.get('/{id}/solicitudes-cotizacion', status_code=status.HTTP_200_OK)
def obtener_solicitudes(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_SOLICITUDES_COTIZACION_PROPIAS', 'VER_SOLICITUDES_COTIZACION_GLOBAL')),
    use_case: ObtenerSolicitudesCotizacionUseCase = Depends(get_obtener_solicitudes_cotizacion_use_case)
):
    solicitudes = use_case.ejecutar(id, usuario)

    return {
        'solicitudes': solicitudes
    }


@router.post('/{id}/aceptacion', status_code=status.HTTP_201_CREATED)
def registrar_aceptacion(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES')),
    use_case: RegistrarAceptacionClienteUseCase = Depends(get_registrar_aceptacion_cliente_use_case)
):
    use_case.ejecutar(id, usuario)

    return {
        'message': 'Propuesta aceptada'
    }


@router.get('/{id}/historial-estado', status_code=status.HTTP_200_OK)
def obtener_historial_estado(
    id: int,
    _: Usuario = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES')),
    use_case: ObtenerHistorialEstadosProcesoComercialUseCase = Depends(get_obtener_historial_estados_proceso_comercial_use_case)
):
    historial = use_case.ejecutar(id)
    historial_por_etapa = ResumenHistorialEstadoMapper(historial).map()

    return {
        'historial': historial_por_etapa
    }

@router.post('/{id}/polizas', status_code=status.HTTP_201_CREATED)
def registrar_poliza(
    id: int,
    request: RegistrarPolizaAProcesoComercialRequest,
    usuario: Usuario = Depends(permisos_requeridos('CARGAR_POLIZAS_PROPIAS', 'CARGAR_POLIZAS_GLOBAL')),
    use_case_registrar_poliza: RegistrarPolizaAProcesoComercialUseCase = Depends(get_registrar_poliza_a_proceso_comercial_use_case)
):
    use_case_registrar_poliza.ejecutar(
        id_proceso_comercial=id,
        numero_poliza=request.numero_poliza,
        tipo=request.tipo,
        id_company=request.id_company,
        prima_neta=request.prima_neta,
        comision_corredora_pct=request.comision_corredora_pct,
        fecha_emision=datetime.fromisoformat(request.fecha_emision),
        inicio_vigencia=datetime.fromisoformat(request.inicio_vigencia),
        fin_vigencia=datetime.fromisoformat(request.fin_vigencia),
        usuario=usuario
    )

    return {
        'message': f'Póliza {request.numero_poliza} registrada'
    }