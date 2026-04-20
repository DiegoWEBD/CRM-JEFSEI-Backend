from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal

class Usuario:
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str, sucursal: Sucursal, roles: list[Rol], password_encriptada: str | None = None):
        self.rut = rut
        self.correo = correo
        self.nombre = nombre
        self.telefono = telefono
        self.sucursal = sucursal
        self.password_encriptada = password_encriptada
        self.roles = roles