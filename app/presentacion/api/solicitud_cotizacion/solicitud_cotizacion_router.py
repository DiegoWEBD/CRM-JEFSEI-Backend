import os
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from app.aplicacion.cotizacion.use_cases.obtener_cotizaciones_por_solicitud import ObtenerCotizacionesPorSolicitudUseCase
from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import RegistrarCotizacionASolicitudUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_detalle_solicitud import ObtenerDetalleSolicitudUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import ObtenerResumenSolicitudesCotizacionActivasUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.cotizacion.adaptadores.cotizacion_json_adapter import CotizacionJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.cotizacion.dependencias.deps import get_obtener_cotizaciones_por_solicitud_use_case, get_registrar_cotizacion_a_solicitud_use_case
from app.presentacion.api.estudio_comercial.deps import get_repositorio_estudios
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_obtener_detalle_solicitud_use_case, get_obtener_resumen_solicitudes_cotizacion_activas_use_case, get_solicitar_cotizacion_use_case, get_solicitar_recotizacion_use_case
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import usuario_tiene_permiso
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales


router = APIRouter(prefix='/solicitudes-cotizacion', tags=['SolicitudesCotizacion'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_solicitudes(
    usuario: Usuario = Depends(permisos_requeridos('VER_SOLICITUDES_COTIZACION_PROPIAS', 'VER_SOLICITUDES_COTIZACION_GLOBAL')),
    use_case: ObtenerResumenSolicitudesCotizacionActivasUseCase = Depends(get_obtener_resumen_solicitudes_cotizacion_activas_use_case)
):
    puede_ver_todas = usuario_tiene_permiso('VER_SOLICITUDES_COTIZACION_GLOBAL', usuario)
    solicitudes = []

    rut_usuario = None if puede_ver_todas else usuario.rut
    solicitudes = use_case.ejecutar(rut_usuario)

    return {
        'solicitudes': solicitudes
    }

@router.get('/{id}', status_code=status.HTTP_200_OK)
def obtener_detalle_solicitud(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_SOLICITUDES_COTIZACION_PROPIAS', 'VER_SOLICITUDES_COTIZACION_GLOBAL')),
    use_case: ObtenerDetalleSolicitudUseCase = Depends(get_obtener_detalle_solicitud_use_case)
):
    puede_ver_todas = usuario_tiene_permiso('VER_SOLICITUDES_COTIZACION_GLOBAL', usuario)

    solicitud = use_case.ejecutar(id, usuario)

    return {
        'solicitud': solicitud
    }

      
@router.get('/{id}/cotizaciones', status_code=status.HTTP_200_OK)
def obtener_cotizaciones_por_solicitud(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_COTIZACIONES_GLOBAL', 'VER_COTIZACIONES_PROPIAS')),
    use_case: ObtenerCotizacionesPorSolicitudUseCase = Depends(get_obtener_cotizaciones_por_solicitud_use_case)
):
    rut_usuario = usuario.rut if not usuario_tiene_permiso('VER_COTIZACIONES_GLOBAL', usuario) else None
    cotizaciones = use_case.ejecutar(id, rut_usuario)

    return {
        'cotizaciones': [CotizacionJsonAdapter(cotizacion).to_cotizacion_json() for cotizacion in cotizaciones]
    } 


@router.post('/{id}/cotizaciones', status_code=status.HTTP_201_CREATED)
def registrar_cotizacion_a_solicitud(
    id: int,
    monto_total_asegurado: float = Form(...),
    tasa_afecta: float = Form(...),
    tasa_excenta: float = Form(...),
    tasa_politica: float = Form(...),
    prima_adicional_asistencia: float = Form(...),
    id_company: int = Form(...),
    fecha_emision: str = Form(...),
    fecha_vencimiento: str = Form(...),
    archivo: UploadFile | None = File(None),
    usuario: Usuario = Depends(permisos_requeridos('CARGAR_COTIZACIONES')),
    use_case: RegistrarCotizacionASolicitudUseCase = Depends(get_registrar_cotizacion_a_solicitud_use_case)
):
    nombre_archivo = None

    if archivo is not None:
        if archivo.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail='Solo se permiten archivos PDF')

        extension = 'pdf'
        nombre_unico = f'cotizacion_{id}_{uuid4().hex}.{extension}'
        ruta = f'documentos/cotizaciones/{nombre_unico}'

        os.makedirs('documentos/cotizaciones', exist_ok=True)

        with open(ruta, 'wb') as f:
            f.write(archivo.file.read())

        nombre_archivo = nombre_unico

    use_case.ejecutar(
        rut_usuario=usuario.rut,
        id_solicitud=id,
        monto_total_asegurado=monto_total_asegurado,
        tasa_afecta=tasa_afecta,
        tasa_excenta=tasa_excenta,
        tasa_politica=tasa_politica,
        prima_adicional_asistencia=prima_adicional_asistencia,
        id_company=id_company,
        fecha_emision=datetime.fromisoformat(fecha_emision),
        fecha_vencimiento=datetime.fromisoformat(fecha_vencimiento),
        nombre_archivo=nombre_archivo
    )

    return {
        'message': 'Cotización registrada'
    }


@router.post('/{id}/estudios-comerciales', status_code=status.HTTP_201_CREATED)
def subir_estudio_comercial(
    id: int,
    archivo: UploadFile = File(...),
    usuario = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    if archivo.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail='Solo se permiten archivos PDF')

    from datetime import datetime
    timestamp_ms = int(datetime.now().timestamp() * 1000)
    nombre_unico = f'estudio_comercial_{id}_{timestamp_ms}.pdf'
    ruta = f'documentos/estudios_finales/{nombre_unico}'

    os.makedirs('documentos/estudios_finales', exist_ok=True)

    with open(ruta, 'wb') as f:
        f.write(archivo.file.read())

    id_estudio = repositorio.insertar(id_solicitud=id, nombre_archivo=nombre_unico, rut_usuario=usuario.rut)

    return {
        'id': id_estudio,
        'id_solicitud': id,
        'nombre_archivo': nombre_unico,
        'mensaje': 'Estudio comercial subido correctamente',
    }


@router.get('/{id}/estudios-comerciales', status_code=status.HTTP_200_OK)
def listar_estudios_comerciales(
    id: int,
    _ = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    estudios = repositorio.listar_por_id_solicitud(id)
    return [
        {
            'id': e.id,
            'nombre_archivo': e.nombre_archivo,
        }
        for e in estudios
    ]


@router.get('/{id}/estudios-comerciales/{estudio_id}/archivo', status_code=status.HTTP_200_OK)
def descargar_archivo_estudio(
    id: int,
    estudio_id: int,
    _ = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    estudios = repositorio.listar_por_id_solicitud(id)
    estudio = next((e for e in estudios if e.id == estudio_id), None)
    if estudio is None or estudio.nombre_archivo is None:
        raise HTTPException(status_code=404, detail='Estudio no encontrado')

    ruta = f'documentos/estudios_finales/{estudio.nombre_archivo}'
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail='Archivo no encontrado')

    return FileResponse(ruta, media_type='application/pdf', filename=estudio.nombre_archivo)