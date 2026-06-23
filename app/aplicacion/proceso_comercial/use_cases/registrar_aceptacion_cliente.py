from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class RegistrarAceptacionClienteUseCase:

    def __init__(self, repositorio_procesos_comerciales: RepositorioProcesosComerciales) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, id_proceso_comercial: int, usuario: Usuario):

        if not self.repositorio_procesos_comerciales.buscar(id_proceso_comercial):
            raise RecursoNoEncontradoException('Proceso comercial no encontrado')

        self.repositorio_procesos_comerciales.registrar_aceptacion_cliente(
            id=id_proceso_comercial,
            rut_usuario=usuario.rut
        )