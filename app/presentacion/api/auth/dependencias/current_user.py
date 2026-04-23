from typing import Annotated
from fastapi import Depends

from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user

CurrentUser = Annotated[Usuario, Depends(get_current_user)]