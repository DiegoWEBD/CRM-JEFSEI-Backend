from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException


class CrearTransicionUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
    ):
        self.repositorio_estados = repositorio_estados

    def ejecutar(
        self,
        codigo_estado_origen: str,
        codigo_estado_destino: str,
        es_manual: bool = True,
        es_principal: bool = False,
        accion_requerida: str | None = None,
    ) -> bool:
        # La transición principal define el flujo feliz, el destinatario de las
        # alertas SLA y su días límite: es una restricción del negocio y solo
        # se siembra por migración de base de datos.
        if es_principal:
            raise ConflictoEnAccionException(
                'Las transiciones principales no se pueden crear desde la aplicación; '
                'definen el flujo feliz y el SLA del estado y se siembran por migración'
            )

        origen = self.repositorio_estados.obtener_por_codigo(codigo_estado_origen)
        if origen is None:
            raise RecursoNoEncontradoException('El estado de origen no existe')

        destino = self.repositorio_estados.obtener_por_codigo(codigo_estado_destino)
        if destino is None:
            raise RecursoNoEncontradoException('El estado de destino no existe')

        if codigo_estado_origen == codigo_estado_destino:
            raise ConflictoEnAccionException('La transición no puede ir del estado hacia sí mismo')

        if self.repositorio_estados.existe_transicion(codigo_estado_origen, codigo_estado_destino):
            raise RecursoYaExisteException(
                'Ya existe una transición entre los estados indicados'
            )

        transicion = TransicionEstadoProcesoComercial(
            codigo_estado_origen=codigo_estado_origen,
            codigo_estado_destino=codigo_estado_destino,
            nombre_estado_destino=destino.nombre,
            nombre_estado_origen=origen.nombre,
            es_manual=es_manual,
            es_principal=es_principal,
            accion_requerida=accion_requerida.strip() if accion_requerida else None,
        )

        return self.repositorio_estados.crear_transicion(transicion)
