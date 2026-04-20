from app.dominio.rol.codigo_rol import CodigoRol

class Rol:
    def __init__(self, codigo: CodigoRol, nombre: str):
        self.codigo = codigo
        self.nombre = nombre