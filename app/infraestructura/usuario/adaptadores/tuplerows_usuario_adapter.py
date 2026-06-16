from app.dominio.permiso.permiso import Permiso
from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal
from app.dominio.usuario.usuario import Usuario
from psycopg.rows import DictRow


class TupleRowsUsuarioAdapter:
    
    def __init__(self, rows: list[DictRow]):

        if not rows or len(rows) == 0:
            raise ValueError("Usuario inválido")
        
        self.rows = rows

    def to_usuario(self) -> Usuario:
        
        rut=self.rows[0]['rut']
        nombre=self.rows[0]['nombre']
        correo=self.rows[0]['correo']
        telefono=self.rows[0]['telefono']
        id_sucursal=self.rows[0]['id_sucursal']
        nombre_sucursal=self.rows[0]['nombre_sucursal']
        password_hash=self.rows[0]['password_hash']
        meta_mensual_uf=self.rows[0]['meta_mensual_uf']
        fecha_registro=self.rows[0]['fecha_registro']
        habilitado=self.rows[0]['habilitado']
        eliminado=self.rows[0]['eliminado']
        porcentaje_comision=self.rows[0]['porcentaje_comision']
        junior=self.rows[0]['junior']

        sucursal = Sucursal(
            id=id_sucursal, 
            nombre=nombre_sucursal
        )

        roles: dict[str, Rol] = {}

        for row in self.rows:
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

        return Usuario(
            rut=rut,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            sucursal=sucursal,
            password_hash=password_hash,
            roles=list(roles.values()),
            meta_mensual_uf=meta_mensual_uf,
            fecha_registro=fecha_registro,
            habilitado=habilitado,
            eliminado=eliminado,
            porcentaje_comision=porcentaje_comision,
            junior=junior
        )