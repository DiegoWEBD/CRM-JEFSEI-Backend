from app.dominio.usuario.usuario import Usuario


def usuario_tiene_permiso(codigo: str, usuario: Usuario) -> bool:
    for rol in usuario.roles:
        for permiso in rol.permisos:
            if permiso.codigo == codigo:
                return True
    return False