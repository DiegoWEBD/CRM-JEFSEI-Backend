import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from app.aplicacion.cotizacion.use_cases.actualizar_cotizacion import ActualizarCotizacionUseCase
from app.aplicacion.cotizacion.use_cases.eliminar_cotizacion import EliminarCotizacionUseCase
from app.aplicacion.cotizacion.use_cases.obtener_cotizaciones_por_solicitud import ObtenerCotizacionesPorSolicitudUseCase
from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import RegistrarCotizacionASolicitudUseCase
from app.aplicacion.evaluacion_proyectos.use_cases.subir_estudio_comercial import SubirEstudioComercialUseCase
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.solicitud_cotizacion.use_cases.eliminar_solicitud_cotizacion import EliminarSolicitudCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_detalle_solicitud import ObtenerDetalleSolicitudUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import ObtenerResumenSolicitudesCotizacionActivasUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_unidades_alicuotas import ObtenerUnidadesAlicuotasUseCase
from app.core.archivos import TAMANO_MAXIMO_ARCHIVO
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.cotizacion.adaptadores.cotizacion_json_adapter import CotizacionJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.cotizacion.dependencias.deps import (
    get_actualizar_cotizacion_use_case,
    get_eliminar_cotizacion_use_case,
    get_obtener_cotizaciones_por_solicitud_use_case,
    get_registrar_cotizacion_a_solicitud_use_case,
    get_subir_estudio_comercial_use_case,
)
from app.presentacion.api.estudio_comercial.deps import get_repositorio_estudios
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_authorization_service, get_eliminar_solicitud_cotizacion_use_case, get_obtener_detalle_solicitud_use_case, get_obtener_resumen_solicitudes_cotizacion_activas_use_case, get_obtener_unidades_alicuotas_use_case
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
    solicitud = use_case.ejecutar(id, usuario)

    return {
        'solicitud': solicitud
    }


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def eliminar_solicitud_cotizacion(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('ELIMINAR_SOLICITUD_COTIZACION')),
    use_case: EliminarSolicitudCotizacionUseCase = Depends(get_eliminar_solicitud_cotizacion_use_case)
):
    use_case.ejecutar(
        id_solicitud=id,
        rut_usuario=usuario.rut,
    )

    return {
        'message': 'Solicitud de cotización eliminada'
    }


@router.get('/{id}/unidades', status_code=status.HTTP_200_OK)
def obtener_unidades_alicuotas(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_SOLICITUDES_COTIZACION_PROPIAS', 'VER_SOLICITUDES_COTIZACION_GLOBAL')),
    use_case: ObtenerUnidadesAlicuotasUseCase = Depends(get_obtener_unidades_alicuotas_use_case)
):
    puede_ver_todas = usuario_tiene_permiso('VER_SOLICITUDES_COTIZACION_GLOBAL', usuario)
    rut_usuario = None if puede_ver_todas else usuario.rut

    unidades = use_case.ejecutar(id, rut_usuario)

    return {
        'unidades': unidades,
        'cantidad': len(unidades)
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
    tipo: str = Form(...),
    monto_total_asegurado: float = Form(...),
    tasa_afecta: float | None = Form(None),
    tasa_excenta: float | None = Form(None),
    tasa_politica: float | None = Form(None),
    prima_afecta: float | None = Form(None),
    prima_excenta: float | None = Form(None),
    asistencia_afecta: float = Form(...),
    asistencia_excenta: float = Form(...),
    id_company: int = Form(...),
    fecha_emision: str = Form(...),
    fecha_vencimiento: str = Form(...),
    archivo: UploadFile | None = File(None),
    usuario: Usuario = Depends(permisos_requeridos('CARGAR_COTIZACIONES')),
    use_case: RegistrarCotizacionASolicitudUseCase = Depends(get_registrar_cotizacion_a_solicitud_use_case)
):
    if tipo not in ('tasa', 'prima'):
        raise HTTPException(status_code=400, detail='Tipo debe ser "tasa" o "prima"')

    if tipo == 'tasa':
        if tasa_afecta is None or tasa_excenta is None or tasa_politica is None:
            raise HTTPException(status_code=400, detail='Cuando tipo es "tasa", se requieren tasa_afecta, tasa_excenta y tasa_politica')
    else:
        if prima_afecta is None or prima_excenta is None:
            raise HTTPException(status_code=400, detail='Cuando tipo es "prima", se requieren prima_afecta y prima_excenta')

    nombre_archivo = None
    contenido_archivo = None

    if archivo is not None:
        if archivo.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail='Solo se permiten archivos PDF')

        contenido_archivo = archivo.file.read()

        if len(contenido_archivo) > TAMANO_MAXIMO_ARCHIVO:
            raise HTTPException(status_code=400, detail='El archivo excede el tamaño máximo de 25 MB')

    use_case.ejecutar(
        rut_usuario=usuario.rut,
        id_solicitud=id,
        monto_total_asegurado=monto_total_asegurado,
        asistencia_afecta=asistencia_afecta,
        asistencia_excenta=asistencia_excenta,
        id_company=id_company,
        fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento,
        tipo=tipo,
        tasa_afecta=tasa_afecta,
        tasa_excenta=tasa_excenta,
        tasa_politica=tasa_politica,
        prima_afecta=prima_afecta,
        prima_excenta=prima_excenta,
        contenido_archivo=contenido_archivo,
    )

    return {
        'message': 'Cotización registrada'
    }


@router.put('/{id_solicitud}/cotizaciones/{id_cotizacion}', status_code=status.HTTP_200_OK)
def actualizar_cotizacion(
    id_solicitud: int,
    id_cotizacion: int,
    tipo: str = Form(...),
    monto_total_asegurado: float = Form(...),
    tasa_afecta: float | None = Form(None),
    tasa_excenta: float | None = Form(None),
    tasa_politica: float | None = Form(None),
    prima_afecta: float | None = Form(None),
    prima_excenta: float | None = Form(None),
    asistencia_afecta: float = Form(...),
    asistencia_excenta: float = Form(...),
    id_company: int = Form(...),
    fecha_emision: str = Form(...),
    fecha_vencimiento: str = Form(...),
    archivo: UploadFile | None = File(None),
    eliminar_archivo: str = Form('false'),
    usuario: Usuario = Depends(permisos_requeridos('ACTUALIZAR_COTIZACION')),
    use_case: ActualizarCotizacionUseCase = Depends(get_actualizar_cotizacion_use_case)
):
    if tipo not in ('tasa', 'prima'):
        raise HTTPException(status_code=400, detail='Tipo debe ser "tasa" o "prima"')

    if tipo == 'tasa':
        if tasa_afecta is None or tasa_excenta is None or tasa_politica is None:
            raise HTTPException(status_code=400, detail='Cuando tipo es "tasa", se requieren tasa_afecta, tasa_excenta y tasa_politica')
    else:
        if prima_afecta is None or prima_excenta is None:
            raise HTTPException(status_code=400, detail='Cuando tipo es "prima", se requieren prima_afecta y prima_excenta')

    contenido_archivo = None

    if archivo is not None:
        if archivo.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail='Solo se permiten archivos PDF')

        contenido_archivo = archivo.file.read()

        if len(contenido_archivo) > TAMANO_MAXIMO_ARCHIVO:
            raise HTTPException(status_code=400, detail='El archivo excede el tamaño máximo de 25 MB')

    use_case.ejecutar(
        id_cotizacion=id_cotizacion,
        id_solicitud=id_solicitud,
        rut_usuario=usuario.rut,
        monto_total_asegurado=monto_total_asegurado,
        asistencia_afecta=asistencia_afecta,
        asistencia_excenta=asistencia_excenta,
        id_company=id_company,
        fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento,
        tipo=tipo,
        tasa_afecta=tasa_afecta,
        tasa_excenta=tasa_excenta,
        tasa_politica=tasa_politica,
        prima_afecta=prima_afecta,
        prima_excenta=prima_excenta,
        contenido_archivo=contenido_archivo,
        eliminar_archivo=eliminar_archivo.lower() == 'true',
    )

    return {
        'message': 'Cotización actualizada'
    }


@router.delete('/{id_solicitud}/cotizaciones/{id_cotizacion}', status_code=status.HTTP_200_OK)
def eliminar_cotizacion(
    id_solicitud: int,
    id_cotizacion: int,
    usuario: Usuario = Depends(permisos_requeridos('ELIMINAR_COTIZACION')),
    use_case: EliminarCotizacionUseCase = Depends(get_eliminar_cotizacion_use_case)
):
    use_case.ejecutar(
        id_cotizacion=id_cotizacion,
        id_solicitud=id_solicitud,
        rut_usuario=usuario.rut,
    )

    return {
        'message': 'Cotización eliminada'
    }


@router.post('/{id}/estudios-comerciales', status_code=status.HTTP_201_CREATED)
def subir_estudio_comercial(
    id: int,
    archivo: UploadFile = File(...),
    usuario = Depends(permisos_requeridos('SUBIR_ESTUDIO_COMERCIAL')),
    use_case: SubirEstudioComercialUseCase = Depends(get_subir_estudio_comercial_use_case)
):
    if archivo.content_type != 'application/pdf':
        raise BadRequestException('Solo se permiten archivos PDF')

    contenido = archivo.file.read()

    if len(contenido) > TAMANO_MAXIMO_ARCHIVO:
        raise BadRequestException('El archivo excede el tamaño máximo de 25 MB')

    # La validación leyó el stream completo; hay que rebobinarlo para que el
    # use case pueda escribirlo sin recibir un archivo vacío.
    archivo.file.seek(0)
    contenido_archivo = archivo.file.read()

    id_estudio, nombre_unico = use_case.ejecutar(contenido_archivo=contenido_archivo, id_solicitud=id, usuario=usuario)

    return {
        'id': id_estudio,
        'id_solicitud': id,
        'nombre_archivo': nombre_unico,
        'mensaje': 'Estudio comercial subido correctamente',
    }


@router.get('/{id}/estudios-comerciales', status_code=status.HTTP_200_OK)
def listar_estudios_comerciales(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_ESTUDIOS_COMERCIALES_PROPIOS', 'VER_ESTUDIOS_COMERCIALES_TODOS')),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    if not authorization_service.usuario_puede_ver_estudios_comerciales(usuario.rut, id):
        raise UsuarioNoAutorizadoException

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
    usuario: Usuario = Depends(permisos_requeridos('VER_ESTUDIOS_COMERCIALES_PROPIOS', 'VER_ESTUDIOS_COMERCIALES_TODOS')),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    if not authorization_service.usuario_puede_descargar_estudio_comercial(usuario.rut, id):
        raise UsuarioNoAutorizadoException

    estudios = repositorio.listar_por_id_solicitud(id)
    estudio = next((e for e in estudios if e.id == estudio_id), None)
    if estudio is None or estudio.nombre_archivo is None:
        raise HTTPException(status_code=404, detail='Estudio no encontrado')

    ruta = f'documentos/estudios_finales/{estudio.nombre_archivo}'
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail='Archivo no encontrado')

    return FileResponse(ruta, media_type='application/pdf', filename=estudio.nombre_archivo)