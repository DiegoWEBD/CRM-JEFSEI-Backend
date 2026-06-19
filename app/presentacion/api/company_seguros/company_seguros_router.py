from fastapi import APIRouter, Depends, status

from app.aplicacion.company_seguros.use_cases.obtener_todas_las_companies_seguros import ObtenerTodasLasCompaniesSegurosUseCase
from app.presentacion.api.company_seguros.deps import get_obtener_todas_las_companies_seguros_use_case


router = APIRouter(prefix="/companies-seguros", tags=["Companies Seguros"])

@router.get("/", status_code=status.HTTP_200_OK)
def obtener_companies_seguros(
    use_case: ObtenerTodasLasCompaniesSegurosUseCase = Depends(get_obtener_todas_las_companies_seguros_use_case)
):
    companies_seguros = use_case.ejecutar()

    return {
        "companies_seguros": companies_seguros
    }
