from datetime import datetime, timezone

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.reevaluar_alertas_renovacion_descarte import (
    ReevaluarAlertasRenovacionDescarteUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario

MOTIVO_DESCARTE_CAMBIO_LINEA = 'Descarte automático por cambio de línea de negocio del prospecto'


class CambiarLineaNegocioProspectoUseCase:

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_lineas_negocio: RepositorioLineasNegocio,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        servicio_alertas: ServicioAlertasProceso,
        reevaluar_alertas: ReevaluarAlertasRenovacionDescarteUseCase,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_lineas_negocio = repositorio_lineas_negocio
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_historial = repositorio_historial
        self.servicio_alertas = servicio_alertas
        self.reevaluar_alertas = reevaluar_alertas

    def ejecutar(
        self,
        id: int,
        id_linea_negocio: int,
        usuario: Usuario
    ) -> int:
        """Cambia la línea de negocio del prospecto y descarta todas sus
        oportunidades abiertas (acción irreversible).

        Devuelve la cantidad de oportunidades descartadas.
        """

        prospecto = self.repositorio_prospectos.buscar(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        if not prospecto.ejecutivo_comercial_asignado or prospecto.ejecutivo_comercial_asignado.rut != usuario.rut:
            raise UsuarioNoAutorizadoException(
                'Solo el ejecutivo comercial asignado puede cambiar la línea de negocio'
            )

        linea_negocio = self.repositorio_lineas_negocio.obtener_por_id(id_linea_negocio)

        if linea_negocio is None:
            raise DatoInvalidoException('La línea de negocio indicada no existe')

        if prospecto.linea_negocio.id == id_linea_negocio:
            raise ConflictoEnAccionException('El prospecto ya pertenece a la línea de negocio indicada')

        procesos_abiertos = self.repositorio_procesos_comerciales.obtener_procesos_comerciales(
            id_prospecto=id,
            abiertos=True
        )

        # Se descartan las oportunidades abiertas antes de cambiar la línea,
        # para no dejar el prospecto en la línea nueva con oportunidades
        # abiertas de la anterior si algo falla a mitad del proceso.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios: list[str] = []
        destinatarios_renovacion: list[str] = []

        for proceso in procesos_abiertos:
            self._descartar_proceso(proceso, ahora, usuario)
            destinatarios.extend(self.servicio_alertas.marcar_todas_leidas(proceso.id, ahora))

            # Si la oportunidad descartada era de renovación, la póliza base
            # vuelve a necesitar sus alertas: se re-evalúan de inmediato (los
            # hitos que sigan aplicando se recrean), sin esperar al scheduler.
            destinatarios_renovacion.extend(self.reevaluar_alertas.ejecutar(proceso.id, ahora))

        prospecto.linea_negocio = linea_negocio
        self.repositorio_prospectos.actualizar_prospecto(prospecto)

        destinatarios_unicos = list(dict.fromkeys(destinatarios))
        if destinatarios_unicos:
            hub.publicar_desde_hilo(
                destinatarios_unicos,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_descarte'},
            )

        destinatarios_renovacion_unicos = list(dict.fromkeys(destinatarios_renovacion))
        if destinatarios_renovacion_unicos:
            hub.publicar_desde_hilo(
                destinatarios_renovacion_unicos,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_actualizadas'},
            )

        return len(procesos_abiertos)

    def _descartar_proceso(
        self,
        proceso: ProcesoComercial,
        ahora: datetime,
        usuario: Usuario
    ) -> None:
        proceso.descartado = True
        proceso.cerrado = True
        proceso.fecha_cierre = ahora
        proceso.motivo_cierre = MOTIVO_DESCARTE_CAMBIO_LINEA
        self.repositorio_procesos_comerciales.actualizar(proceso)

        self.repositorio_historial.registrar(
            HistorialEstadoProcesoComercial(
                id_proceso_comercial=proceso.id,
                codigo_estado='OPORTUNIDAD_DESCARTADA',
                rut_registrado_por=usuario.rut,
                fecha=ahora,
                observacion=MOTIVO_DESCARTE_CAMBIO_LINEA,
            )
        )
