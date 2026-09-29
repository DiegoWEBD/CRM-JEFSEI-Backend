from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany
from app.dominio.riesgo_cobertura.riesgo_cobertura import RiesgoCobertura


class CompanySeguros:
    def __init__(
        self, 
        id: int, 
        nombre: str, 
        factores_cuotas: list[FactorCuotasCompany] | None = None,
        coberturas: list[RiesgoCobertura] | None = None,
        eliminado: bool = False
    ):
        self.id = id
        self.nombre = nombre
        self.factores_cuotas = factores_cuotas if factores_cuotas is not None else []
        self.coberturas = coberturas if coberturas is not None else []
        self.eliminado = eliminado

    def esta_eliminada(self) -> bool:
        return self.eliminado

    def marcar_eliminada(self) -> None:
        self.eliminado = True
