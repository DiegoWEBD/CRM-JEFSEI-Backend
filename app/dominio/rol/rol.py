from app.dominio.permiso.permiso import Permiso
from app.dominio.rol.codigo_rol import CodigoRol

class Rol:
    def __init__(self, codigo: CodigoRol, nombre: str, permisos: list[Permiso]):
        self.codigo = codigo
        self.nombre = nombre
        self.permisos = permisos