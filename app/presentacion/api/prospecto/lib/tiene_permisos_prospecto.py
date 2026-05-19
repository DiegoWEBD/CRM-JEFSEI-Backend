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

    if prospecto.evaluacion_riesgo:
        ruts_autorizados.update([prospecto.ejecutivo_comercial_asignado.rut])

        if prospecto.evaluacion_riesgo.ej_evaluacion:
            ruts_autorizados.update([prospecto.ejecutivo_evaluacion_asignado.rut])

    return usuario.rut in ruts_autorizados