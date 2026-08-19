import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.aplicacion.archivo.use_cases.eliminar_archivo import EliminarArchivoUseCase
from app.aplicacion.archivo.use_cases.obtener_archivo_por_id import ObtenerArchivoPorIdUseCase
from app.aplicacion.archivo.use_cases.obtener_archivos_prospecto import ObtenerArchivosProspectoUseCase
from app.aplicacion.archivo.use_cases.subir_archivo import SubirArchivoUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.archivo.deps import (
    get_eliminar_archivo_use_case,
    get_obtener_archivo_por_id_use_case,
    get_obtener_archivos_prospecto_use_case,
    get_subir_archivo_use_case,
)
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user


router = APIRouter(prefix='/prospectos/{id_prospecto}/archivos', tags=['Archivos'])


TIPOS_PERMITIDOS = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
}

MIME_TO_EXTENSION = {
    'application/pdf': 'pdf',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/msword': 'doc',
}

TAMANO_MAXIMO = 20 * 1024 * 1024


@router.post('/', status_code=status.HTTP_201_CREATED)
def subir_archivo(
    id_prospecto: int,
    archivo: UploadFile = File(...),
    usuario: Usuario = Depends(get_current_user),
    use_case: SubirArchivoUseCase = Depends(get_subir_archivo_use_case)
):
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Tipo de archivo no permitido: {archivo.content_type}'
        )

    contenido = archivo.file.read()

    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='El archivo excede el tamaño máximo de 20 MB'
        )

    extension = MIME_TO_EXTENSION.get(archivo.content_type, 'bin')
    nombre_almacenado = f'prospecto_{id_prospecto}_{uuid4().hex}.{extension}'
    ruta = f'documentos/prospectos/{nombre_almacenado}'

    os.makedirs('documentos/prospectos', exist_ok=True)

    with open(ruta, 'wb') as f:
        f.write(contenido)

    archivo_creado = use_case.ejecutar(
        id_prospecto=id_prospecto,
        nombre_almacenado=nombre_almacenado,
        nombre_original=archivo.filename,
        tipo_contenido=archivo.content_type,
        tamano_bytes=len(contenido),
        rut_usuario=usuario.rut,
    )

    return {
        'id': archivo_creado.id,
        'id_prospecto': id_prospecto,
        'nombre_original': archivo_creado.nombre_original,
        'nombre_almacenado': archivo_creado.nombre_almacenado,
        'message': 'Archivo subido correctamente',
    }


@router.get('/', status_code=status.HTTP_200_OK)
def listar_archivos(
    id_prospecto: int,
    usuario: Usuario = Depends(get_current_user),
    use_case: ObtenerArchivosProspectoUseCase = Depends(get_obtener_archivos_prospecto_use_case)
):
    archivos = use_case.ejecutar(id_prospecto=id_prospecto, rut_usuario=usuario.rut)

    return {
        'archivos': [
            {
                'id': a.id,
                'nombre_original': a.nombre_original,
                'tipo_contenido': a.tipo_contenido,
                'tamano_bytes': a.tamano_bytes,
                'created_at': a.created_at.isoformat() if a.created_at else None,
            }
            for a in archivos
        ]
    }


@router.get('/{id_archivo}', status_code=status.HTTP_200_OK)
def descargar_archivo(
    id_prospecto: int,
    id_archivo: int,
    usuario: Usuario = Depends(get_current_user),
    use_case: ObtenerArchivoPorIdUseCase = Depends(get_obtener_archivo_por_id_use_case)
):
    archivo = use_case.ejecutar(
        id_archivo=id_archivo,
        id_prospecto=id_prospecto,
        rut_usuario=usuario.rut
    )

    ruta = f'documentos/prospectos/{archivo.nombre_almacenado}'

    if not os.path.exists(ruta):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='El archivo no se encuentra en el servidor'
        )

    return FileResponse(
        ruta,
        media_type=archivo.tipo_contenido,
        filename=archivo.nombre_original
    )


@router.delete('/{id_archivo}', status_code=status.HTTP_200_OK)
def eliminar_archivo(
    id_prospecto: int,
    id_archivo: int,
    usuario: Usuario = Depends(get_current_user),
    use_case: EliminarArchivoUseCase = Depends(get_eliminar_archivo_use_case)
):
    nombre_almacenado = use_case.ejecutar(
        id_archivo=id_archivo,
        id_prospecto=id_prospecto,
        rut_usuario=usuario.rut
    )

    ruta = f'documentos/prospectos/{nombre_almacenado}'
    if os.path.exists(ruta):
        os.remove(ruta)

    return {'message': 'Archivo eliminado correctamente'}
