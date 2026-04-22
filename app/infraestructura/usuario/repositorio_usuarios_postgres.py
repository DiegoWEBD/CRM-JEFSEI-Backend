from app.dominio.usuario.usuario import Usuario
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.usuario.adaptadores.tuplerows_usuario_adapter import TupleRowsUsuarioAdapter

class RepositorioUsuariosPostgres(RepositorioUsuarios):

    def buscar(self, rut: str) -> Usuario | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select U.rut, U.nombre, 
                    U.correo, U.telefono,
                    S.id as id_sucursal,
                    S.nombre as nombre_sucursal, 
                    RU.codigo_rol,
                    R.nombre as rol,
                    PR.codigo_permiso, 
                    P.descripcion as descripcion_permiso
                    from Usuario U
                    inner join Sucursal S
                    on U.id_sucursal = S.id
                    left join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    left join Rol R
                    on RU.codigo_rol = R.codigo
                    left join PermisoRol PR
                    on R.codigo = PR.codigo_rol
                    left join Permiso P
                    on PR.codigo_permiso = P.codigo
                    where U.rut = %(rut)s
                '''
                params = {
                    'rut': rut
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None

                return TupleRowsUsuarioAdapter(rows)

    def registrar(self, usuario: Usuario) -> bool:
        return False