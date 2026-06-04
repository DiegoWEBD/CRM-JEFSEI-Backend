from pydantic import BaseModel


class ActualizarProspectoCondominioRequest(BaseModel):
    rut_riesgo: str | None
    nombre_riesgo: str
    nombre_contacto: str
    telefono_contacto: str 
    correo_contacto: str | None 
    direccion: str 
    region: str
    comuna: str 
    cargo_contacto: str | None
    observaciones: str | None 
    id_linea_negocio: int  
    uf_por_metro_cuadrado: float | None
    porcentaje_depreciacion: float | None
    porcentaje_espacios_comunes: float | None
    tiene_locales_comerciales: bool | None
    uso_del_condominio: str | None
    numero_pisos: int | None
    numero_torres: int | None
    cantidad_departamentos: int | None
    cantidad_subterraneos: int | None
    tiene_piscina: bool | None
    year_construccion: int | None
    metros_cuadrados: float | None
    desea_ser_contactado: bool | None