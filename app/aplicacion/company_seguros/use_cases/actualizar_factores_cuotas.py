from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException


class ActualizarFactoresCuotasUseCase:
    def __init__(self, repositorio_company_seguros: RepositorioCompanySeguros):
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(self, id_company: int, factores: list[dict]) -> None:
        company = self.repositorio_company_seguros.buscar(id_company)

        if company is None:
            raise RecursoNoEncontradoException("Compañía no encontrada")

        factores_normalizados = [self._validar_factor(factor) for factor in factores]

        numeros_cuotas = [f["numero_cuotas"] for f in factores_normalizados]
        if len(numeros_cuotas) != len(set(numeros_cuotas)):
            raise BadRequestException("Número de cuotas duplicado")

        self.repositorio_company_seguros.reemplazar_factores_cuotas(
            id_company,
            [(f["numero_cuotas"], f["factor"]) for f in factores_normalizados],
        )

    def _validar_factor(self, factor: dict) -> dict:
        numero_cuotas = factor.get("numero_cuotas")
        valor_factor = factor.get("factor")

        if not isinstance(numero_cuotas, int) or isinstance(numero_cuotas, bool) or numero_cuotas < 1:
            raise BadRequestException("El número de cuotas debe ser un entero mayor a 0")

        if not isinstance(valor_factor, (int, float)) or isinstance(valor_factor, bool) or valor_factor <= 0:
            raise BadRequestException("El factor debe ser mayor a 0")

        return {"numero_cuotas": numero_cuotas, "factor": float(valor_factor)}
