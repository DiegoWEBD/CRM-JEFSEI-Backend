from app.aplicacion.notificacion.notificacion_factory import NotificacionFactory
from app.aplicacion.notificacion.use_cases.refrescar_alertas_renovacion import (
    RefrescarAlertasRenovacionUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoRenovacionUseCase:
    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_notificaciones: RepositorioNotificaciones,
        refrescar_alertas_renovacion: RefrescarAlertasRenovacionUseCase,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_notificaciones = repositorio_notificaciones
        self.refrescar_alertas_renovacion = refrescar_alertas_renovacion

    def ejecutar(self, id_cliente: int, rut_ej_renovacion: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar_cliente(id_cliente)

        if not prospecto or not prospecto.id:
            raise RecursoNoEncontradoException('Cliente no encontrado')

        rut_anterior = prospecto.ejecutivo_renovacion_asignado.rut if prospecto.ejecutivo_renovacion_asignado else None

        if rut_ej_renovacion is not None:
            usuario = self.repositorio_usuarios.buscar(rut_ej_renovacion)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.ejecutivo_renovacion_asignado = usuario
        else:
            prospecto.ejecutivo_renovacion_asignado = None

        # Sin cliente asociado no hay asignación que guardar ni notificar.
        if not prospecto.id_cliente:
            return

        self.repositorio_prospectos.asignar_ejecutivo_renovacion(prospecto, asignado_por)

        if rut_anterior != rut_ej_renovacion:
            # Con cambio de ejecutivo, las alertas de renovación del anterior
            # dejan de ser suyas: se eliminan y se re-evalúan en este momento
            # para crear las del nuevo responsable (creadas ahora, no
            # transferidas). En desasignación se eliminan las previas y no se
            # crea nada (sin destinatario), igual que en cierre y SLA.
            self.refrescar_alertas_renovacion.ejecutar(prospecto.id_cliente)

        # Notificaciones de asignación/desasignación: en cada invocación con RUT
        # destino (asignación) y solo al cambiar de RUT (desasignación).
        if rut_ej_renovacion is not None:
            self.repositorio_notificaciones.registrar(
                NotificacionFactory.crear_notificacion_asignacion(
                    rut_asignado=rut_ej_renovacion,
                    detalle_asignacion='renovación',
                    entidad_tipo='CLIENTE',
                    entidad_id=prospecto.id_cliente,
                    nombre_entidad=prospecto.nombre_riesgo or f'#{prospecto.id_cliente}',
                    id_prospecto=prospecto.id,
                )
            )

        if rut_anterior and rut_anterior != rut_ej_renovacion:
            self.repositorio_notificaciones.registrar(
                NotificacionFactory.crear_notificacion_desasignacion(
                    rut_desasignado=rut_anterior,
                    detalle_asignacion='renovación',
                    entidad_tipo='CLIENTE',
                    entidad_id=prospecto.id_cliente,
                    nombre_entidad=prospecto.nombre_riesgo or f'#{prospecto.id_cliente}',
                    id_prospecto=prospecto.id,
                )
            )

        if rut_ej_renovacion is not None:
            hub.publicar_desde_hilo(
                [rut_ej_renovacion],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'asignacion_ejecutivo'},
            )

        if rut_anterior and rut_anterior != rut_ej_renovacion:
            hub.publicar_desde_hilo(
                [rut_anterior],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'desasignacion_ejecutivo'},
            )