import math
from datetime import datetime, time
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from app.aplicacion.auditoria.use_cases.obtener_registros_auditoria import ObtenerRegistrosAuditoriaUseCase
from app.presentacion.api.auditoria.dependencias.deps import get_obtener_registros_auditoria_use_case
from app.presentacion.api.auditoria.dto.filtros_auditoria import FiltrosAuditoria
from app.presentacion.api.auditoria.lib.registro_auditoria_csv import generar_csv_registros_auditoria
from app.presentacion.api.auditoria.mappers.registro_auditoria_mapper import registro_auditoria_a_json
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.dto.deps import get_paginacion_params
from app.presentacion.api.dto.paginacion_params import PaginacionParams

router = APIRouter(prefix='/auditoria', tags=['Auditoria'])

LIMITE_EXPORTACION = 10000


def get_filtros_auditoria(
    categoria: str | None = Query(None),
    evento: str | None = Query(None),
    rut_usuario: str | None = Query(None),
    ip_origen: str | None = Query(None),
    entidad_tipo: str | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
) -> FiltrosAuditoria:
    # Si "fecha_hasta" llega sin hora (medianoche), se interpreta como fin de día.
    if fecha_hasta is not None and fecha_hasta.time() == time(0, 0):
        fecha_hasta = datetime.combine(fecha_hasta.date(), time(23, 59, 59, 999999))

    return FiltrosAuditoria(
        categoria=categoria,
        evento=evento,
        rut_usuario=rut_usuario,
        ip_origen=ip_origen,
        entidad_tipo=entidad_tipo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_registros_auditoria(
    _ = Depends(permisos_requeridos('VER_AUDITORIA')),
    paginacion: PaginacionParams = Depends(get_paginacion_params),
    filtros: FiltrosAuditoria = Depends(get_filtros_auditoria),
    use_case: ObtenerRegistrosAuditoriaUseCase = Depends(get_obtener_registros_auditoria_use_case),
):
    registros, total = use_case.ejecutar_paginado(
        categoria=filtros.categoria,
        evento=filtros.evento,
        rut_usuario=filtros.rut_usuario,
        ip_origen=filtros.ip_origen,
        entidad_tipo=filtros.entidad_tipo,
        fecha_desde=filtros.fecha_desde,
        fecha_hasta=filtros.fecha_hasta,
        texto_busqueda=paginacion.texto_busqueda,
        pagina=paginacion.pagina,
        tamano_pagina=paginacion.tamano_pagina,
    )
    total_paginas = math.ceil(total / paginacion.tamano_pagina) if total > 0 else 1

    return {
        'data': [registro_auditoria_a_json(registro) for registro in registros],
        'total': total,
        'pagina': paginacion.pagina,
        'tamano_pagina': paginacion.tamano_pagina,
        'total_paginas': total_paginas,
    }


@router.get('/exportar', status_code=status.HTTP_200_OK)
def exportar_registros_auditoria(
    _ = Depends(permisos_requeridos('VER_AUDITORIA')),
    texto_busqueda: str | None = Query(None),
    filtros: FiltrosAuditoria = Depends(get_filtros_auditoria),
    use_case: ObtenerRegistrosAuditoriaUseCase = Depends(get_obtener_registros_auditoria_use_case),
):
    registros = use_case.ejecutar_exportacion(
        categoria=filtros.categoria,
        evento=filtros.evento,
        rut_usuario=filtros.rut_usuario,
        ip_origen=filtros.ip_origen,
        entidad_tipo=filtros.entidad_tipo,
        fecha_desde=filtros.fecha_desde,
        fecha_hasta=filtros.fecha_hasta,
        texto_busqueda=texto_busqueda,
        limite=LIMITE_EXPORTACION,
    )

    csv_contenido = generar_csv_registros_auditoria(registros)
    nombre_archivo = f'auditoria_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return Response(
        content=csv_contenido,
        media_type='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="{nombre_archivo}"; '
                                   f'filename*=UTF-8\'\'{quote(nombre_archivo)}'
        },
    )
