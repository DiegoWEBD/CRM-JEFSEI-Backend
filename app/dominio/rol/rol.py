from app.dominio.permiso.permiso import Permiso

class Rol:
    def __init__(self, codigo: str, nombre: str, permisos: list[Permiso] = []):
        self.codigo = codigo
        self.nombre = nombre
        self.permisos = permisos