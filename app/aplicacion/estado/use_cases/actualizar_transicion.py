from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.rol.repositorio_roles import RepositorioRoles


class ActualizarTransicionUseCase:

    def __init__(
        self,
        repositorio_estados: RepositorioEstadosProcesoComercial,
        repositorio_notificaciones: RepositorioNotificaciones,
        generar_alertas_sla: GenerarAlertasSlaUseCase,
        repositorio_roles: RepositorioRoles,
    ):
        self.repositorio_estados = repositorio_estados
        self.repositorio_notificaciones = repositorio_notificaciones
        self.generar_alertas_sla = generar_alertas_sla
        self.repositorio_roles = repositorio_roles

    def ejecutar(
        self,
        codigo_estado_origen: str,
        codigo_estado_destino: str,
        es_manual: bool,
        accion_requerida: str | None,
        dias_limite: int | None = None,
        roles_responsables_nuevas: list[str] | None = None,
        roles_responsables_renovacion: list[str] | None = None,
    ) -> bool:
        transicion = self.repositorio_estados.obtener_transicion(
            codigo_estado_origen, codigo_estado_destino
        )
        if transicion is None:
            raise RecursoNoEncontradoException('La transición solicitada no existe')

        if transicion.es_principal:
            # La principal no es editable en su flujo (es_manual / acción
            # requerida): solo en su días límite, que es el que alimenta las
            # alertas SLA del estado de origen, y en sus responsables.
            if dias_limite is not None and dias_limite < 0:
                raise ConflictoEnAccionException(
                    'Los días límite no pueden ser negativos'
                )

            # Solo re-evaluar si el límite realmente cambió: un guardado
            # idéntico no debe borrar alertas ni re-notificar.
            sla_cambio = transicion.dias_limite != dias_limite
            transicion.dias_limite = dias_limite

            # Los responsables también alimentan las alertas SLA: un cambio
            # en ellos debe re-evaluar igual que el días límite.
            roles_cambiaron = self._actualizar_responsables(
                transicion,
                roles_responsables_nuevas,
                roles_responsables_renovacion,
            )
            sla_cambio = sla_cambio or roles_cambiaron
        else:
            # Solo las transiciones principales pueden tener responsables.
            if (
                roles_responsables_nuevas is not None
                or roles_responsables_renovacion is not None
            ):
                raise ConflictoEnAccionException(
                    'Solo las transiciones principales pueden tener responsables'
                )

            sla_cambio = False

            if es_manual is False and transicion.accion_requerida:
                accion_requerida = None

            transicion.es_manual = es_manual
            transicion.accion_requerida = (
                accion_requerida.strip() if accion_requerida else None
            )
            # El SLA es exclusivo de la transición principal.
            transicion.dias_limite = None

        actualizado = self.repositorio_estados.actualizar_transicion(transicion)

        if actualizado and sla_cambio:
            self._reevaluar_alertas_sla(codigo_estado_origen)

        return actualizado

    def _actualizar_responsables(
        self,
        transicion: TransicionEstadoProcesoComercial,
        roles_responsables_nuevas: list[str] | None,
        roles_responsables_renovacion: list[str] | None,
    ) -> bool:
        """Reemplaza los responsables dados (None = sin cambios).

        Devuelve True si algún responsable realmente cambió. Una lista
        vacía elimina los responsables de ese tipo de oportunidad; solo
        las transiciones principales pueden tener responsables.
        """
        cambios = (
            (
                roles_responsables_nuevas,
                False,
                transicion.roles_responsables_nuevas,
            ),
            (
                roles_responsables_renovacion,
                True,
                transicion.roles_responsables_renovacion,
            ),
        )
        cambiaron = False

        for roles, renovacion, actuales in cambios:
            if roles is None:
                continue

            roles = list(dict.fromkeys(rol.strip() for rol in roles if rol.strip()))
            self._validar_roles(roles)

            if sorted(roles) == sorted(actuales):
                continue

            self.repositorio_estados.reemplazar_roles_responsables(
                transicion.id, renovacion, roles
            )

            if renovacion:
                transicion.roles_responsables_renovacion = roles
            else:
                transicion.roles_responsables_nuevas = roles

            cambiaron = True

        return cambiaron

    def _validar_roles(self, roles: list[str]) -> None:
        codigos = {rol.codigo for rol in self.repositorio_roles.obtener_todos()}
        faltantes = [rol for rol in roles if rol not in codigos]

        if faltantes:
            raise ConflictoEnAccionException(
                'Los roles responsables indicados no existen'
            )

    def _reevaluar_alertas_sla(self, codigo_estado: str) -> None:
        """Elimina las alertas SLA no leídas del estado y las re-evalúa ya.

        El nuevo días límite puede hacer que una alerta deje de corresponder
        (se borra y no se recrea) o que pase de 'por vencer' a 'vencida' (se
        recrea con el tipo nuevo). La re-evaluación es idempotente: los demás
        estados no se tocan porque su dedupe_key siguen existiendo.
        """
        destinatarios: set[str] = set()

        notificaciones = self.repositorio_notificaciones.obtener_todas(
            codigo_estado=codigo_estado,
            leidas=False,
        )

        for notificacion in notificaciones:
            if notificacion.codigo_tipo not in TIPOS_ALERTA_SLA:
                continue

            self.repositorio_notificaciones.eliminar(notificacion)

            if notificacion.rut_usuario:
                destinatarios.add(notificacion.rut_usuario)

        self.generar_alertas_sla.ejecutar()

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'sla_reevaluado'},
            )
