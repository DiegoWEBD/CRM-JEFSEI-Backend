from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal

class Usuario:
    def __init__(
        self, 
        rut: str, 
        nombre: str, 
        correo: str, 
        telefono: str, 
        sucursal: Sucursal,
        meta_mensual_uf: int | None = None,
        roles: list[Rol] = [], 
        password_hash: str | None = None
    ):
        self.rut = rut
        self.correo = correo
        self.nombre = nombre
        self.telefono = telefono
        self.sucursal = sucursal
        self.password_hash = password_hash
        self.roles = roles
        self.meta_mensual_uf = meta_mensual_uf
        