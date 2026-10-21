from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.validador_alicuotas import validar_unidades
from app.dominio.usuario.usuario import Usuario


class ImportarAlicuotaOportunidadUseCase:
    """Asocia el archivo de alícuotas (unidades y prorrateos) a una oportunidad.

    Reemplaza por completo la alícuota previa de la oportunidad.
    """

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_unidades = repositorio_unidades
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id_proceso_comercial: int,
        nombre_excel: str,
        unidades: list[UnidadAlicuota],
        usuario: Usuario,
    ) -> None:
        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso or not proceso.id:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_solicitar_cotizacion(usuario, proceso.id):
            raise UsuarioNoAutorizadoException

        if proceso.cerrado:
            raise ConflictoEnAccionException('La oportunidad está cerrada')

        if proceso.producto.codigo != 'unidades':
            raise ConflictoEnAccionException('La alícuota solo aplica a oportunidades de unidades')

        if not nombre_excel or not nombre_excel.strip():
            raise ConflictoEnAccionException('Debe indicar el nombre del archivo de alícuotas')

        problemas = validar_unidades(unidades)

        if problemas:
            detalle = '; '.join(
                f'fila {problema.fila_origen}: {problema.mensaje}'
                if problema.fila_origen is not None
                else problema.mensaje
                for problema in problemas[:5]
            )
            raise ConflictoEnAccionException(f'Las unidades importadas no son válidas: {detalle}')

        self.repositorio_unidades.guardar_o_reemplazar(proceso.id, nombre_excel.strip(), unidades)
