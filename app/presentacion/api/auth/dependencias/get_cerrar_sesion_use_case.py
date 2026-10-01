from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.presentacion.api.auditoria.dependencias.deps import get_servicio_auditoria


def get_cerrar_sesion_use_case():
    return CerrarSesionUseCase(get_servicio_auditoria())
