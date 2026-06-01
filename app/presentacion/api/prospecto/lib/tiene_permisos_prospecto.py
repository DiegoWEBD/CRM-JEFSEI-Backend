from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import usuario_tiene_permiso


def tiene_permisos_prospecto(
    usuario: Usuario,
    prospecto: Prospecto
) -> bool:

    if usuario_tiene_permiso("OBTENER_PROSPECTOS_TODOS", usuario):
        return True

    if not usuario_tiene_permiso("OBTENER_PROSPECTOS_PROPIOS", usuario):
        return False

    ruts_autorizados = {
        prospecto.registrado_por.rut
    }

    if prospecto.proceso_comercial.ejecutivo_comercial:
        ruts_autorizados.update([prospecto.proceso_comercial.ejecutivo_comercial.rut])

    if prospecto.proceso_comercial.ejecutivo_evaluacion:
        ruts_autorizados.update([prospecto.proceso_comercial.ejecutivo_evaluacion.rut])

    return usuario.rut in ruts_autorizados