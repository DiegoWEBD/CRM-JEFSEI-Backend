from app.presentacion.api.prospecto.dto.prospecto_json import ProspectoJson


class ProspectoEmpresaJson(ProspectoJson):
    nombre_fantasia: str | None
    cantidad_trabajadores: int | None
    giros_comerciales: list[str]
