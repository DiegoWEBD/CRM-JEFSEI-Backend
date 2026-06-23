from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class CerrarProcesoComercialUseCase:

    def __init__(self, repositorio_procesos_comerciales: RepositorioProcesosComerciales):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, id: int, ganado: bool, observacion: str | None, usuario: Usuario):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')
        
        if proceso.cerrado:
            raise Exception('La oportunidad ya se encuentra cerrada')

        self.repositorio_procesos_comerciales.cerrar(
            id=id,
            ganado=ganado,
            observacion=observacion,
            rut_usuario=usuario.rut
        )