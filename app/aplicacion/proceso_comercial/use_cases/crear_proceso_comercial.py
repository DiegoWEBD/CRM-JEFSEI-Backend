from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class CrearProcesoComercialUseCase:

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_productos: RepositorioProducto,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales
    ) -> None:
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_productos = repositorio_productos
        self.repositorio_historial = repositorio_historial

    def ejecutar(self, tipo: str, id_prospecto: int, usuario: Usuario) -> ProcesoComercial:
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto or not prospecto.id:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if not self.authorization_service.usuario_puede_crear_proceso_comercial(usuario, prospecto):
            raise UsuarioNoAutorizadoException

        producto = self.repositorio_productos.obtener_por_codigo(tipo)

        if not producto:
            raise RecursoNoEncontradoException('No se encontró el producto seleccionado')

        estado = EstadoInformativoProcesoComercial(
            codigo='OPORTUNIDAD_CREADA',
            nombre=''
        )
        fecha_actual = datetime.now(tz=timezone.utc)

        proceso = ProcesoComercial(
            id=0, # arbitrario
            ejecutivo_comercial=prospecto.ejecutivo_comercial_asignado,
            ejecutivo_evaluacion=prospecto.ejecutivo_evaluacion_asignado,
            id_prospecto=prospecto.id,
            nombre_cliente=prospecto.nombre_riesgo,
            producto=producto,
            estado_actual=estado,
            fecha_apertura=fecha_actual,
            cerrado=False,
            renovacion=False
        )
        
        proceso = self.repositorio_procesos_comerciales.guardar(proceso, es_nuevo=True)

        self.repositorio_historial.registrar(
            HistorialEstadoProcesoComercial(
                id_proceso_comercial=proceso.id,
                codigo_estado=estado.codigo,
                rut_registrado_por=usuario.rut,
                fecha=fecha_actual
            )
        )
        
        return proceso