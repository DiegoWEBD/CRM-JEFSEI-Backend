from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoLineasPersonalesUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, id: int, rut_usuario: str | None) -> Prospecto:
        prospecto = self.repositorio_prospectos.buscar(id)

        if prospecto is None or prospecto.id is None:
            raise RecursoNoEncontradoException('No se encontró el prospecto')

        if rut_usuario:
            autorizado = any([
                prospecto.ejecutivo_comercial_asignado and prospecto.ejecutivo_comercial_asignado.rut == rut_usuario,
                prospecto.registrado_por.rut == rut_usuario
            ])

            if not autorizado:

                procesos = self.repositorio_procesos_comerciales.obtener_procesos_comerciales(prospecto.id)

                for proceso in procesos:
                    autorizado = any([
                        proceso.ejecutivo_comercial and proceso.ejecutivo_comercial.rut == rut_usuario,
                        proceso.ejecutivo_evaluacion and proceso.ejecutivo_evaluacion.rut == rut_usuario,
                        proceso.ejecutivo_renovacion and proceso.ejecutivo_renovacion.rut == rut_usuario,
                        proceso.asistente_renovacion and proceso.asistente_renovacion.rut == rut_usuario
                    ])

                    if autorizado:
                        break
        
            if not autorizado:
                raise UsuarioNoAutorizadoException

        return prospecto
    