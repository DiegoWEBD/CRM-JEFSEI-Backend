from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class CerrarProcesoComercialUseCase:

    def __init__(
        self, 
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_planes_pago: RepositorioPlanesPago,
        repositorio_polizas: RepositorioPolizas
    ):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_planes_pago = repositorio_planes_pago
        self.repositorio_polizas = repositorio_polizas

    def ejecutar(self, id: int, ganado: bool, observacion: str | None, usuario: Usuario):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')
        
        if proceso.cerrado:
            raise RecursoYaExisteException('La oportunidad ya se encuentra cerrada')
        
        if ganado:
            poliza = self.repositorio_polizas.buscar_por_proceso_comercial(id)

            if not poliza:
                raise ConflictoEnAccionException('La oportunidad debe tener una póliza y un plan de pago para poder cerrarse')

            if not self.repositorio_planes_pago.buscar_plan_pago_poliza(poliza.numero_poliza):
                raise ConflictoEnAccionException('La oportunidad debe tener una póliza y un plan de pago para poder cerrarse')

        self.repositorio_procesos_comerciales.cerrar(
            id=id,
            ganado=ganado,
            observacion=observacion,
            rut_usuario=usuario.rut
        )