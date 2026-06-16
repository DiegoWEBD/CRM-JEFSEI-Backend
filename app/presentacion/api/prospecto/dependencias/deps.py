from app.aplicacion.linea_negocio.use_cases.obtener_linea_negocio_prospecto import ObtenerLineaNegocioProspectoUseCase
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.aplicacion.prospecto.use_cases.actualizar_prospecto_condominio import ActualizarProspectoCondominioUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial import AsignarEjecutivoComercialUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_evaluacion import AsignarEjecutivoEvaluacionUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto import ObtenerProspectoUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto_condominio import ObtenerProspectoCondominioUseCase
from app.aplicacion.prospecto.use_cases.registrar_prospecto import RegistrarProspectoUseCase
from app.infraestructura.historial_estado.repositorio_historial_estado_postgres import RepositorioHistorialEstadoPostgres
from app.infraestructura.linea_negocio.repositorio_lineas_negocio_postgres import RepositorioLineasNegocioPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service import ConsultaProspectosPostgresService
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres
from app.presentacion.api.prospecto.dependencias.obtener_prospecto_factory import ObtenerProspectoFactory


def get_consulta_prospectos_service() -> ConsultaProspectosService:
    return ConsultaProspectosPostgresService()

def get_obtener_prospecto_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    return ObtenerProspectoUseCase(repositorio_prospectos)

def get_obtener_prospecto_condominio_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_historial_estado = RepositorioHistorialEstadoPostgres()

    return ObtenerProspectoCondominioUseCase(repositorio_prospectos, repositorio_historial_estado)

def get_registrar_prospecto_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return RegistrarProspectoUseCase(repositorio_prospectos=repositorio_prospectos, repositorio_usuarios=repositorio_usuarios)

def get_asignar_ejecutivo_comercial_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoComercialUseCase(repositorio_prospectos, repositorio_usuarios)

def get_asignar_ejecutivo_evaluacion_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoEvaluacionUseCase(repositorio_prospectos, repositorio_usuarios)

def get_obtener_linea_negocio_prospecto_use_case():
    repositorio = RepositorioLineasNegocioPostgres()
    return ObtenerLineaNegocioProspectoUseCase(repositorio)


def get_obtener_prospecto_factory():
    prospecto_condominio_use_case = get_obtener_prospecto_condominio_use_case()
    
    return ObtenerProspectoFactory(
        obtener_prospecto_condominio=prospecto_condominio_use_case
    )

def get_actualizar_prospecto_condominio_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    return ActualizarProspectoCondominioUseCase(repositorio_prospectos)