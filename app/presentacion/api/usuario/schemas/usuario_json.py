from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal

class UsuarioJson:
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str, sucursal: Sucursal, roles: list[Rol]):
        self.rut = rut
        self.correo = correo
        self.nombre = nombre
        self.telefono = telefono
        self.sucursal = sucursal
        self.roles = roles
        