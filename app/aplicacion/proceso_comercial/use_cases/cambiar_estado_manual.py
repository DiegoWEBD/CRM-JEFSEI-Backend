from datetime import datetime, timezone

from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class CambiarEstadoManualUseCase:

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        repositorio_estados: RepositorioEstadosProcesoComercial,
        servicio_alertas: ServicioAlertasProceso,
    ):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas
        self.repositorio_historial = repositorio_historial
        self.repositorio_estados = repositorio_estados

    def ejecutar(
        self,
        id: int,
        codigo_estado_destino: str,
        observacion: str | None,
        usuario: Usuario,
    ):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')

        if proceso.ejecutivo_comercial is None or usuario.rut != proceso.ejecutivo_comercial.rut:
            raise UsuarioNoAutorizadoException('Solo el ejecutivo comercial asignado puede cambiar el estado manualmente')

        if proceso.cerrado:
            raise ConflictoEnAccionException('La oportunidad está cerrada')

        estado_destino = self.repositorio_estados.obtener_por_codigo(codigo_estado_destino)

        if not estado_destino:
            raise RecursoNoEncontradoException('Estado inválido')

        # transiciones posibles desde el estado actual del proceso
        transiciones = self.repositorio_estados.obtener_transiciones_manuales(proceso.estado_actual.codigo)
        transicion_valida = False

        for transicion in transiciones:
            if transicion.codigo_estado_destino == estado_destino.codigo:
                transicion_valida = True
                break

        if not transicion_valida:
            raise ConflictoEnAccionException(f'La transición hacia {estado_destino.codigo} no es válida desde el estado actual')

        proceso.estado_actual = estado_destino
        self.repositorio_procesos_comerciales.guardar(proceso)

        self.repositorio_historial.registrar(
            HistorialEstadoProcesoComercial(
                id_proceso_comercial=proceso.id,
                codigo_estado=estado_destino.codigo,
                rut_registrado_por=usuario.rut,
                observacion=observacion,
                fecha=datetime.now(tz=timezone.utc)
            )
        )


        # La alerta de permanencia en el estado anterior deja de ser relevante.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(id, TIPOS_ALERTA_SLA, ahora)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )
