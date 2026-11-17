from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class ObtenerProcesosComercialesUseCase:

    def __init__(
        self, 
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_proyecciones: RepositorioProyeccionesComerciales
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_proyecciones = repositorio_proyecciones

    def ejecutar(
        self, 
        id_prospecto: int, 
        usuario: Usuario, 
        abiertos: bool | None = None,
    ) -> list[ProcesoComercial]:

        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto or not prospecto.id:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        puede_ver_todos = self.repositorio_usuarios.usuario_tiene_permiso(usuario, 'ADMINISTRAR_PROCESOS_COMERCIALES')
        
        if not puede_ver_todos and not self.authorization_service.usuario_puede_ver_procesos_comerciales(usuario.rut, prospecto.id):
            raise UsuarioNoAutorizadoException

        if puede_ver_todos:
            renovaciones = None

        else:
            ver_oportunidades_comerciales = any([
                prospecto.ejecutivo_comercial_asignado and prospecto.ejecutivo_comercial_asignado.rut == usuario.rut,
                prospecto.ejecutivo_evaluacion_asignado and prospecto.ejecutivo_evaluacion_asignado.rut == usuario.rut,
            ])

            ver_oportunidades_renovacion = any([
                prospecto.ejecutivo_renovacion_asignado and prospecto.ejecutivo_renovacion_asignado.rut == usuario.rut,
                prospecto.asistente_renovacion_asignado and prospecto.asistente_renovacion_asignado.rut == usuario.rut,
            ])

            if ver_oportunidades_comerciales and ver_oportunidades_renovacion:
                renovaciones = None

            elif ver_oportunidades_comerciales:
                renovaciones = False

            # El servicio de autorización ya ha validado que el usuario puede ver al menos un tipo de proceso, por lo que no es necesario lanzar excepción si no puede ver ninguno.
            else:
                renovaciones = True

        procesos = self.repositorio_procesos_comerciales.obtener_procesos_comerciales(prospecto.id, abiertos, renovaciones)

        agregados = self.repositorio_proyecciones.agregados_por_proceso(
            [proceso.id for proceso in procesos]
        )

        for proceso in procesos:
            agregado = agregados.get(proceso.id)

            if agregado is None:
                probabilidad = proceso.probabilidad_cierre_ejecutivo

                if probabilidad is None:
                    probabilidad = proceso.estado_actual.probabilidad_cierre

                proceso.prima_cotizada = 0
                proceso.prima_potencial_estimada = 0
                proceso.prima_esperada = 0 if probabilidad is not None else None
                continue

            proceso.prima_cotizada = agregado.prima_cotizada
            proceso.prima_potencial_estimada = agregado.prima_potencial_estimada
            proceso.prima_esperada = agregado.prima_esperada

        return procesos