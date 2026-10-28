from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario


def _es_mismo_momento(a: datetime | None, b: datetime | None) -> bool:
    """Compara instantes tolerando mezcla de datetimes con/sin zona horaria.

    Los datetimes sin zona se interpretan como UTC (misma convención que la
    conexión a PostgreSQL)."""
    if a is None or b is None:
        return a is b

    if a.tzinfo is None:
        a = a.replace(tzinfo=timezone.utc)

    if b.tzinfo is None:
        b = b.replace(tzinfo=timezone.utc)

    return a == b


class ActualizarPolizaUseCase:

    def __init__(
        self,
        repositorio_polizas: RepositorioPolizas,
        authorization_service: AuthorizationService,
        servicio_alertas: ServicioAlertasProceso,
        generar_alerta_renovacion: GenerarAlertaRenovacionPolizaUseCase,
    ):
        self.repositorio_polizas = repositorio_polizas
        self.authorization_service = authorization_service
        self.servicio_alertas = servicio_alertas
        self.generar_alerta_renovacion = generar_alerta_renovacion

    def ejecutar(
        self,
        numero_poliza: str,
        usuario: Usuario,
        tipo: str,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime | None,
        inicio_vigencia: datetime | None,
        fin_vigencia: datetime | None,
        id_company: int | None,
    ) -> None:
        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if not poliza:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if not self.authorization_service.usuario_puede_actualizar_poliza(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException()

        self.repositorio_polizas.actualizar(
            numero_poliza=numero_poliza,
            tipo=tipo,
            prima_neta=prima_neta,
            comision_corredora_pct=comision_corredora_pct,
            fecha_emision=fecha_emision,
            inicio_vigencia=inicio_vigencia,
            fin_vigencia=fin_vigencia,
            id_company=id_company,
        )

        # El fin de vigencia determina los hitos de las alertas de renovación:
        # al cambiarlo, las de la vigencia anterior dejan de aplicar. Se
        # eliminan (no solo se marcan leídas: una fila leída con la misma
        # dedupe_key bloquearía la re-creación si la fecha vuelve a un valor
        # anterior) y se re-evalúa al tiro para crear las de la vigencia nueva,
        # sin esperar al scheduler.
        if _es_mismo_momento(poliza.fin_vigencia, fin_vigencia):
            return

        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.eliminar_renovacion(numero_poliza)

        for notificacion in self.generar_alerta_renovacion.ejecutar(numero_poliza, ahora):
            if notificacion.rut_usuario:
                destinatarios.append(notificacion.rut_usuario)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_actualizadas'},
            )
