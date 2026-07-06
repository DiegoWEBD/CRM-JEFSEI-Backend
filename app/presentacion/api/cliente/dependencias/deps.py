from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_cobranza import AsignarEjecutivoCobranzaUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_renovacion import AsignarEjecutivoRenovacionUseCase
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_asignar_ejecutivo_cobranza_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoCobranzaUseCase(repositorio_prospectos, repositorio_usuarios)


def get_asignar_ejecutivo_renovacion_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoRenovacionUseCase(repositorio_prospectos, repositorio_usuarios)
