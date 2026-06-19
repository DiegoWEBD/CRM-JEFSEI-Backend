import base64

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import ArmarEstudioComercialCondominioUseCase
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.estudio_comercial.deps import get_armar_estudio_comercial_use_case, get_repositorio_estudios
from app.presentacion.api.estudio_comercial.dto.armar_estudio_comercial_request import ArmarEstudioComercialRequest

router = APIRouter(prefix="/estudio-comercial", tags=["Estudio Comercial"])

@router.get("/", status_code = status.HTTP_200_OK)
def listar_estudios(
    prospecto_id: int = Query(...),
    _ = Depends(permisos_requeridos('LISTAR_ESTUDIOS_COMERCIALES')),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    try:
        #estudios = repositorio.listar_por_id_prospecto(prospecto_id)
        estudios = []
        return estudios
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/{id_estudio}/archivo", status_code = status.HTTP_200_OK)
def subir_archivo_estudio(
    id_estudio: int,
    archivo: UploadFile = File(...),
    _ = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    repositorio: RepositorioEstudiosComerciales = Depends(get_repositorio_estudios)
):
    try:
        ruta_destino = f'app/infraestructura/templates/estudios/{id_estudio}_{archivo.filename}'

        with open(ruta_destino, 'wb') as f:
            f.write(archivo.file.read())

        repositorio.actualizar_ruta_archivo(id_estudio, ruta_destino)

        return {'mensaje': 'Archivo subido correctamente', 'ruta': ruta_destino}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/", status_code = status.HTTP_201_CREATED)
def armar_estudio_comercial(
    request: ArmarEstudioComercialRequest,
    usuario: Usuario = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    use_case: ArmarEstudioComercialCondominioUseCase = Depends(get_armar_estudio_comercial_use_case)
):
    try:
        estudio_comercial, id_estudio, ruta_archivo = use_case.ejecutar(
            id_prospecto=request.id_prospecto,
            infraseguro_primer_ejemplo=request.infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=request.infraseguro_segundo_ejemplo,
            cantidad_cuotas=request.cantidad_cuotas,
            ids_cotizacion=request.ids_cotizacion,
            usuario=usuario,
        )

        with open(ruta_archivo, 'rb') as f:
            archivo_bytes = f.read()
        archivo_base64 = base64.b64encode(archivo_bytes).decode('utf-8')

        return {
            "estudio_comercial": estudio_comercial,
            "archivo_base64": archivo_base64,
            "nombre_archivo": f'estudio_comercial_{request.id_prospecto}.docx',
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )