from app.dominio.poliza.poliza import Poliza

class Cliente:
    def __init__(self, rut: str, nombre_cliente: str, nombre_contacto: str, telefono_contacto: str, correo_contacto: str, direccion: str, comuna: str, polizas: list[Poliza]):
        self.rut = rut
        self.nombre_cliente = nombre_cliente
        self.nombre_contacto = nombre_contacto
        self.telefono_contacto = telefono_contacto
        self.correo_contacto = correo_contacto
        self.direccion = direccion
        self.comuna = comuna
        self.polizas = polizas
