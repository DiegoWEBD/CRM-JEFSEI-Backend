import base64

from fastapi import APIRouter, Depends, status

from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import ArmarEstudioComercialCondominioUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.estudio_comercial.deps import get_armar_estudio_comercial_use_case
from app.presentacion.api.estudio_comercial.dto.armar_estudio_comercial_request import ArmarEstudioComercialRequest

router = APIRouter(prefix='/estudio-comercial', tags=['Estudio Comercial'])


@router.post('/', status_code = status.HTTP_201_CREATED)
def armar_estudio_comercial(
    request: ArmarEstudioComercialRequest,
    usuario: Usuario = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    use_case: ArmarEstudioComercialCondominioUseCase = Depends(get_armar_estudio_comercial_use_case)
):
    ruta_archivo = use_case.ejecutar(
        id_prospecto=request.id_prospecto,
        monto_asegurado_actual=request.monto_asegurado_actual,
        con_monto_sugerido=request.con_monto_sugerido,
        infraseguro_primer_ejemplo=request.infraseguro_primer_ejemplo,
        infraseguro_segundo_ejemplo=request.infraseguro_segundo_ejemplo,
        cantidad_cuotas=request.cantidad_cuotas,
        ids_cotizacion=request.ids_cotizacion,
        secciones=request.secciones,
        valor_uf=request.valor_uf,
        usuario=usuario
    )

    with open(ruta_archivo, 'rb') as f:
        archivo_bytes = f.read()
    archivo_base64 = base64.b64encode(archivo_bytes).decode('utf-8')

    return {
        'archivo_base64': archivo_base64,
        'nombre_archivo': f'estudio_comercial_{request.id_prospecto}.docx',
    }