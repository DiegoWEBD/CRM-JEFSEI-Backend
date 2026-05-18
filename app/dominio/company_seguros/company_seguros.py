from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany
from app.dominio.riesgo_cobertura.riesgo_cobertura import RiesgoCobertura


class CompanySeguros:
    def __init__(
        self, 
        id: int, 
        nombre: str, 
        url_logo: str,
        factores_cuotas: list[FactorCuotasCompany],
        coberturas: list[RiesgoCobertura]
    ):
        self.id = id
        self.nombre = nombre
        self.url_logo = url_logo
        self.factores_cuotas = factores_cuotas
        self.coberturas = coberturas