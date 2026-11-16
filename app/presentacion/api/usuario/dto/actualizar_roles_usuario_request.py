from pydantic import BaseModel


class ActualizarRolesUsuarioRequest(BaseModel):
    codigo_roles: list[str]
