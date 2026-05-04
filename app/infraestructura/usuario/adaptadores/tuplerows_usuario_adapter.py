from app.dominio.permiso.permiso import Permiso
from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal
from app.dominio.usuario.usuario import Usuario
from psycopg.rows import TupleRow


class TupleRowsUsuarioAdapter(Usuario):
    
    def __init__(self, rows: list[TupleRow]):

        if not rows or len(rows) == 0:
            raise ValueError("Usuario inválido")
        
        rut=rows[0]['rut']
        nombre=rows[0]['nombre']
        correo=rows[0]['correo']
        telefono=rows[0]['telefono']
        id_sucursal=rows[0]['id_sucursal']
        nombre_sucursal=rows[0]['nombre_sucursal']
        password_hash=rows[0]['password_hash']
        meta_mensual_uf=rows[0]['meta_mensual_uf']

        sucursal = Sucursal(
            id=id_sucursal, 
            nombre=nombre_sucursal
        )

        roles: dict[str, Rol] = {}

        for row in rows:
            codigo_rol = row['codigo_rol']
            rol = roles.get(codigo_rol)

            if rol is None:
                nombre_rol = row['rol']
                rol = Rol(
                    codigo=codigo_rol,
                    nombre=nombre_rol,
                    permisos=[]
                )
                roles[codigo_rol] = rol
            
            codigo_permiso = row['codigo_permiso']

            if codigo_permiso is not None:
                descripcion_permiso = row['descripcion_permiso']

                permiso = Permiso(
                    codigo=codigo_permiso,
                    descripcion=descripcion_permiso
                )
                rol.permisos.append(permiso)

        super().__init__(
            rut=rut,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            sucursal=sucursal,
            password_hash=password_hash,
            roles=list(roles.values()),
            meta_mensual_uf=meta_mensual_uf
        )