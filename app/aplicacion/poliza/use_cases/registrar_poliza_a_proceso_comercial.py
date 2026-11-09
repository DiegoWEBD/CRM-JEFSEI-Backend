from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class RegistrarPolizaAProcesoComercialUseCase:

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_polizas: RepositorioPolizas,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_companies: RepositorioCompanySeguros,
        authorization_service: AuthorizationService,
        repositorio_historial_estados: RepositorioHistorialEstadoProcesosComerciales,
        servicio_alertas: ServicioAlertasProceso
    ) -> None:

        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_companies = repositorio_companies
        self.authorization_service = authorization_service
        self.repositorio_historial_estados = repositorio_historial_estados
        self.servicio_alertas = servicio_alertas

    def ejecutar(
        self,
        id_proceso_comercial: int,
        numero_poliza: str, 
        tipo: str,
        id_company: int,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime | None,
        inicio_vigencia: datetime | None,
        fin_vigencia: datetime | None,
        usuario: Usuario
    ):
        if self.repositorio_polizas.buscar(numero_poliza):
            raise RecursoYaExisteException(f'La póliza {numero_poliza} ya se encuentra registrada')

        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_subir_poliza(usuario.rut, id_proceso_comercial):
            raise UsuarioNoAutorizadoException

        if proceso.cerrado:
            raise ConflictoEnAccionException('No se puede registrar una póliza a una oportunidad cerrada')

        company = self.repositorio_companies.buscar(id_company)
        
        if not company:
            raise RecursoNoEncontradoException('Compañía no encontrada')

        prospecto = self.repositorio_prospectos.buscar_prospecto_por_proceso_comercial(id_proceso_comercial)

        if not prospecto:
            raise RecursoNoEncontradoException('Prospecto no encontrado para la oportunidad seleccionada')

        if not prospecto.id_cliente:
            id_cliente = self.repositorio_prospectos.crear_cliente(prospecto)

            if not id_cliente:
                raise ConflictoEnAccionException('Error al crear cliente')

            prospecto.id_cliente = id_cliente
        
        poliza = Poliza(
            numero_poliza=numero_poliza,
            id_prospecto=0,         # arbitrario
            nombre_cliente='',      # arbitrario
            id_proceso_comercial=id_proceso_comercial,
            tipo=tipo,
            nombre_producto='',
            company=company,
            prima_neta=prima_neta,
            comision_corredora_pct=comision_corredora_pct,
            fecha_emision=fecha_emision,
            inicio_vigencia=inicio_vigencia,
            fin_vigencia=fin_vigencia,
            estado=EstadoPoliza.REGISTRADA,
            renovacion_cotizada=False
        )

        self.repositorio_polizas.registrar_a_proceso_comercial(poliza, id_proceso_comercial)

        ESTADO_POLIZA_REGISTRADA = 'POLIZA_REGISTRADA'
        proceso.estado_actual.codigo = ESTADO_POLIZA_REGISTRADA
        self.repositorio_procesos_comerciales.guardar(proceso, es_nuevo=False)

        historial = HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso.id,
            codigo_estado=ESTADO_POLIZA_REGISTRADA,
            rut_registrado_por=usuario.rut,
            fecha=datetime.now(tz=timezone.utc)
        )

        self.repositorio_historial_estados.registrar(historial)

        # El registro de la póliza cambia el estado del proceso: la alerta de
        # permanencia en el estado anterior deja de ser relevante.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(
            id_proceso_comercial, TIPOS_ALERTA_SLA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )