from app.aplicacion.auth.use_cases.cerrar_todas_las_sesiones import CerrarTodasLasSesionesUseCase
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.presentacion.api.auditoria.dependencias.deps import get_servicio_auditoria


def get_cerrar_todas_las_sesiones_use_case():
    return CerrarTodasLasSesionesUseCase(
        get_servicio_auditoria(),
        JwtAuthenticationService(RepositorioSesionesPostgres()),
    )
