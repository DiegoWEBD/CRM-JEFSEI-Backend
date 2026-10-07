from datetime import datetime, timezone

from app.aplicacion.notificacion.use_cases.generar_alertas_cierre_estimado import (
    GenerarAlertasCierreEstimadoUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoComercialUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos, 
        repositorio_usuarios: RepositorioUsuarios,
        generar_alertas_cierre: GenerarAlertasCierreEstimadoUseCase,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.generar_alertas_cierre = generar_alertas_cierre

    def ejecutar(self, id_prospecto: int, rut_ej_comercial: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        rut_anterior = prospecto.ejecutivo_comercial_asignado.rut if prospecto.ejecutivo_comercial_asignado else None

        if rut_ej_comercial is not None:
            usuario = self.repositorio_usuarios.buscar(rut_ej_comercial)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.ejecutivo_comercial_asignado = usuario
        else:
            prospecto.ejecutivo_comercial_asignado = None

        self.repositorio_prospectos.asignar_ejecutivo_comercial(prospecto, asignado_por)

        # Con cambio de ejecutivo, re-evaluar las alertas de cierre del prospecto:
        # las del anterior quedaron leídas y se crea la del nuevo destinatario
        # (creada en este momento, no transferida). En desasignación no crea nada.
        # verificar_existencia=False: en esta ruta no debe bloquear la alerta
        # previa (leída) del mismo proceso/tipo/usuario — p. ej. al volver a
        # asignar al ejecutivo anterior. El scheduler sí mantiene la guarda.
        if rut_anterior != rut_ej_comercial:
            self.generar_alertas_cierre.ejecutar(
                id_prospecto=prospecto.id,
                ahora=datetime.now(tz=timezone.utc),
                verificar_existencia=False,
            )

        if rut_ej_comercial is not None:
            hub.publicar_desde_hilo(
                [rut_ej_comercial],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'asignacion_ejecutivo'},
            )

        if rut_anterior and rut_anterior != rut_ej_comercial:
            hub.publicar_desde_hilo(
                [rut_anterior],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'desasignacion_ejecutivo'},
            )
