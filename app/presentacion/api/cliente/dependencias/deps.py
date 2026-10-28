from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.aplicacion.notificacion.use_cases.refrescar_alertas_renovacion import RefrescarAlertasRenovacionUseCase
from app.aplicacion.prospecto.use_cases.asignar_asistente_renovacion import AsignarAsistenteRenovacionUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_cobranza import AsignarEjecutivoCobranzaUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_renovacion import AsignarEjecutivoRenovacionUseCase
from app.infraestructura.notificacion.repositorio_notificaciones_postgres import RepositorioNotificacionesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def _crear_refrescar_alertas_renovacion() -> RefrescarAlertasRenovacionUseCase:
    repositorio_notificaciones = RepositorioNotificacionesPostgres()
    return RefrescarAlertasRenovacionUseCase(
        repositorio_notificaciones,
        GenerarAlertaRenovacionPolizaUseCase(repositorio_notificaciones),
    )


def get_asignar_ejecutivo_cobranza_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoCobranzaUseCase(
        repositorio_prospectos,
        repositorio_usuarios,
        RepositorioNotificacionesPostgres(),
    )


def get_asignar_ejecutivo_renovacion_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoRenovacionUseCase(
        repositorio_prospectos,
        repositorio_usuarios,
        RepositorioNotificacionesPostgres(),
        _crear_refrescar_alertas_renovacion(),
    )


def get_asignar_asistente_renovacion_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarAsistenteRenovacionUseCase(
        repositorio_prospectos,
        repositorio_usuarios,
        RepositorioNotificacionesPostgres(),
        _crear_refrescar_alertas_renovacion(),
    )
