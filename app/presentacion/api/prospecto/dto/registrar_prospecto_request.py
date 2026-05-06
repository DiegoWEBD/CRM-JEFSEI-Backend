from pydantic import BaseModel


class RegistrarProspectoRequest(BaseModel):
    rut_riesgo: str | None
    nombre_riesgo: str 
    nombre_contacto: str
    telefono_contacto: str 
    correo_contacto: str | None 
    direccion: str 
    id_comuna: int 
    observaciones: str | None 
    id_linea_negocio: int
    cargo_contacto: str | None 
    tiene_locales_comerciales: bool | None
    uso_del_condominio: str | None
    numero_pisos: int | None
    numero_torres: int | None
    cantidad_departamentos: int | None
    cantidad_subterraneos: int | None
    tiene_piscina: bool | None
    year_construccion: int | None
    metros_cuadrados: int | None
    desea_ser_contactado: bool | None