from app.aplicacion.authorization.authorization_service_factory import AuthorizationServiceFactory
from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import ArmarEstudioComercialCondominioUseCase
from app.aplicacion.evaluacion_proyectos.use_cases.generar_desglose_unidades import GenerarDesgloseUnidadesUseCase
from app.aplicacion.proceso_comercial.use_cases.calcular_desglose_reconstruccion_unidades import CalcularDesgloseReconstruccionUnidadesUseCase
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.estudio_comercial_condominio.generador_excel_desglose_unidades import GeneradorExcelDesgloseUnidades
from app.infraestructura.estudio_comercial_condominio.repositorio_estudios_comerciales_postgres import RepositorioEstudiosComercialesPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import RepositorioSolicitudesCotizacionPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_unidades_alicuotas_postgres import RepositorioUnidadesAlicuotasPostgres


def get_armar_estudio_comercial_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_companies = RepositorioCompanySegurosPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()

    return ArmarEstudioComercialCondominioUseCase(
        repositorio_prospectos=repositorio_prospectos,
        repositorio_company_seguros=repositorio_companies,
        repositorio_cotizaciones=repositorio_cotizaciones,
        authorization_service=authorization_service
    )


def get_generar_desglose_unidades_use_case():
    return GenerarDesgloseUnidadesUseCase(
        authorization_service=AuthorizationServiceFactory.crear_authorization_service(),
        repositorio_solicitudes=RepositorioSolicitudesCotizacionPostgres(),
        repositorio_unidades=RepositorioUnidadesAlicuotasPostgres(),
        repositorio_cotizaciones=RepositorioCotizacionesPostgres(),
        repositorio_procesos_comerciales=RepositorioProcesosComercialesPostgres(),
        calcular_desglose_reconstruccion=CalcularDesgloseReconstruccionUnidadesUseCase(
            repositorio_prospectos=RepositorioProspectosPostgres(),
        ),
        generador_excel=GeneradorExcelDesgloseUnidades(),
    )


def get_repositorio_estudios():
    return RepositorioEstudiosComercialesPostgres()