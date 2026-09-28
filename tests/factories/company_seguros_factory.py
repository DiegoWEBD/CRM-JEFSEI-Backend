from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany


def crear_factor_cuotas_mock(
    numero_cuotas: int = 12,
    factor: float = 1.085,
) -> FactorCuotasCompany:
    return FactorCuotasCompany(
        numero_cuotas=numero_cuotas,
        factor=factor,
    )


def crear_company_seguros_mock(
    id: int = 1,
    nombre: str = "Chilena Rev. Seguros",
    factores_cuotas: list[FactorCuotasCompany] | None = None,
    eliminado: bool = False,
) -> CompanySeguros:
    if factores_cuotas is None:
        factores_cuotas = [crear_factor_cuotas_mock()]

    return CompanySeguros(
        id=id,
        nombre=nombre,
        factores_cuotas=factores_cuotas,
        eliminado=eliminado,
    )
