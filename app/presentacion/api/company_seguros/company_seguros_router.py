import math

from fastapi import APIRouter, Depends, status

from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import ActualizarFactoresCuotasUseCase
from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import ActualizarNombreCompanyUseCase
from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase
from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase
from app.aplicacion.company_seguros.use_cases.obtener_companies_paginadas import ObtenerCompaniesSegurosPaginadasUseCase
from app.infraestructura.company_seguros.adaptadores.company_seguros_json_adapter import CompanySegurosJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.company_seguros.deps import (
    get_actualizar_factores_cuotas_use_case,
    get_actualizar_nombre_company_use_case,
    get_crear_company_use_case,
    get_eliminar_company_use_case,
    get_obtener_companies_seguros_paginadas_use_case,
)
from app.presentacion.api.company_seguros.dto.actualizar_factores_cuotas_request import ActualizarFactoresCuotasRequest
from app.presentacion.api.company_seguros.dto.company_request import (
    ActualizarCompanyRequest,
    CrearCompanyRequest,
)
from app.presentacion.api.dto.deps import get_paginacion_params
from app.presentacion.api.dto.paginacion_params import PaginacionParams


router = APIRouter(prefix="/companies-seguros", tags=["Companies Seguros"])


@router.get("/", status_code=status.HTTP_200_OK)
def obtener_companies_seguros(
    paginacion: PaginacionParams = Depends(get_paginacion_params),
    use_case: ObtenerCompaniesSegurosPaginadasUseCase = Depends(get_obtener_companies_seguros_paginadas_use_case)
):
    companies_seguros, total = use_case.ejecutar(
        texto_busqueda=paginacion.texto_busqueda,
        pagina=paginacion.pagina,
        tamano_pagina=paginacion.tamano_pagina,
    )

    total_paginas = math.ceil(total / paginacion.tamano_pagina) if total > 0 else 1

    return {
        'data': [CompanySegurosJsonAdapter(company).to_json() for company in companies_seguros],
        'total': total,
        'pagina': paginacion.pagina,
        'tamano_pagina': paginacion.tamano_pagina,
        'total_paginas': total_paginas,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_company(
    request: CrearCompanyRequest,
    _ = Depends(permisos_requeridos('ADMINISTRAR_COMPANIES')),
    use_case: CrearCompanyUseCase = Depends(get_crear_company_use_case)
):
    company = use_case.ejecutar(nombre=request.nombre)

    return {
        'message': 'Compañía registrada correctamente',
        'data': CompanySegurosJsonAdapter(company).to_json(),
    }


@router.put('/{id}', status_code=status.HTTP_200_OK)
def actualizar_company(
    id: int,
    request: ActualizarCompanyRequest,
    _ = Depends(permisos_requeridos('ADMINISTRAR_COMPANIES')),
    use_case: ActualizarNombreCompanyUseCase = Depends(get_actualizar_nombre_company_use_case)
):
    use_case.ejecutar(id=id, nombre=request.nombre)

    return {
        'message': 'Compañía actualizada correctamente'
    }


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def eliminar_company(
    id: int,
    _ = Depends(permisos_requeridos('ADMINISTRAR_COMPANIES')),
    use_case: EliminarCompanyUseCase = Depends(get_eliminar_company_use_case)
):
    use_case.ejecutar(id=id)

    return {
        'message': 'Compañía eliminada correctamente'
    }


@router.put('/{id}/factores-cuotas', status_code=status.HTTP_200_OK)
def actualizar_factores_cuotas(
    id: int,
    request: ActualizarFactoresCuotasRequest,
    _ = Depends(permisos_requeridos('ADMINISTRAR_COMPANIES')),
    use_case: ActualizarFactoresCuotasUseCase = Depends(get_actualizar_factores_cuotas_use_case)
):
    use_case.ejecutar(
        id_company=id,
        factores=[f.model_dump() for f in request.factores],
    )

    return {
        'message': 'Factores de cuotas actualizados correctamente'
    }
