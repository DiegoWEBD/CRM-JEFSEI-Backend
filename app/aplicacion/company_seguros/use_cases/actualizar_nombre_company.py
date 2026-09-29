from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException


class ActualizarNombreCompanyUseCase:
    def __init__(self, repositorio_company_seguros: RepositorioCompanySeguros):
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(self, id: int, nombre: str) -> None:
        company = self.repositorio_company_seguros.buscar(id)

        if company is None:
            raise RecursoNoEncontradoException("Compañía no encontrada")

        if not nombre or not nombre.strip():
            raise BadRequestException("El nombre de la compañía es obligatorio")

        nombre_limpio = nombre.strip()

        if self.repositorio_company_seguros.existe_por_nombre(nombre_limpio, id_excluir=id):
            raise RecursoYaExisteException("Ya existe una compañía con ese nombre")

        self.repositorio_company_seguros.actualizar_nombre(id, nombre_limpio)
