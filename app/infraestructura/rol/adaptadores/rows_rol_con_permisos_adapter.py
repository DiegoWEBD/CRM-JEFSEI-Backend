from psycopg.rows import DictRow

from app.dominio.permiso.permiso import Permiso
from app.dominio.rol.rol import Rol


class RowsRolConPermisosAdapter:
    """Convierte las filas de Rol LEFT JOIN PermisoRol LEFT JOIN Permiso
    en una lista de Rol con sus permisos agregados."""

    def __init__(self, rows: list[DictRow]):
        self.rows = rows

    def to_roles(self) -> list[Rol]:
        roles: dict[str, Rol] = {}

        for row in self.rows:
            if row['codigo'] not in roles:
                roles[row['codigo']] = Rol(
                    codigo=row['codigo'],
                    nombre=row['nombre'],
                    permisos=[]
                )

            if row['permiso_codigo'] is not None:
                roles[row['codigo']].permisos.append(
                    Permiso(
                        codigo=row['permiso_codigo'],
                        descripcion=row['permiso_descripcion'],
                        nombre=row['permiso_nombre']
                    )
                )

        return list(roles.values())
