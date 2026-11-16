from pydantic import BaseModel


class AsignarPermisosRolRequest(BaseModel):
    codigos_permiso: list[str]
