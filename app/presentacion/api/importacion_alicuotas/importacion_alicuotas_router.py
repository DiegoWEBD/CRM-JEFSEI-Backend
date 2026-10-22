from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import ValidationError

from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.analizar_alicuotas import (
    AnalizarAlicuotasUseCase,
)
from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.dto.configuracion_importacion_alicuotas import (
    ConfiguracionImportacionAlicuotas,
)
from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.validar_alicuotas import (
    ValidarAlicuotasUseCase,
)
from app.core.archivos import TAMANO_MAXIMO_ARCHIVO
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.importacion_alicuotas.dependencias.deps import (
    get_analizar_alicuotas_use_case,
    get_validar_alicuotas_use_case,
)

router = APIRouter(prefix='/importacion-alicuotas', tags=['ImportacionAlicuotas'])

EXTENSION_PERMITIDA = '.xlsx'
FIRMA_ZIP = b'PK'
MENSAJE_TAMANO_MAXIMO = 'El archivo excede el tamaño máximo de 25 MB'


def _leer_archivo_excel(archivo: UploadFile) -> bytes:
    """Valida el archivo subido sin confiar en la extensión ni en el MIME.

    Se comprueba la extensión, el tamaño, la firma real del contenido
    (los .xlsx son archivos ZIP) y que openpyxl pueda abrirlo.
    """

    nombre = (archivo.filename or '').strip()

    if not nombre.lower().endswith(EXTENSION_PERMITIDA):
        raise DatoInvalidoException('Solo se permiten archivos Excel (.xlsx)')

    contenido = archivo.file.read()

    if not contenido:
        raise DatoInvalidoException('El archivo está vacío')

    if len(contenido) > TAMANO_MAXIMO_ARCHIVO:
        raise DatoInvalidoException(MENSAJE_TAMANO_MAXIMO)

    if not contenido.startswith(FIRMA_ZIP):
        raise DatoInvalidoException('El archivo no tiene el contenido de un libro de Excel (.xlsx)')

    return contenido


@router.post('/analizar', status_code=status.HTTP_200_OK)
def analizar_alicuotas(
    archivo: UploadFile = File(...),
    hoja: str | None = Form(None),
    inicio: int = Form(1),
    cantidad: int = Form(200),
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
    use_case: AnalizarAlicuotasUseCase = Depends(get_analizar_alicuotas_use_case),
):
    contenido = _leer_archivo_excel(archivo)

    return use_case.ejecutar(contenido=contenido, hoja=hoja, inicio=inicio, cantidad=cantidad)


@router.post('/validar', status_code=status.HTTP_200_OK)
def validar_alicuotas(
    archivo: UploadFile = File(...),
    configuracion: str = Form(...),
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
    use_case: ValidarAlicuotasUseCase = Depends(get_validar_alicuotas_use_case),
):
    contenido = _leer_archivo_excel(archivo)

    try:
        configuracion_alicuotas = ConfiguracionImportacionAlicuotas.model_validate_json(configuracion)
    except ValidationError as exc:
        raise DatoInvalidoException('La configuración de importación no es válida') from exc

    return use_case.ejecutar(contenido=contenido, configuracion=configuracion_alicuotas)
