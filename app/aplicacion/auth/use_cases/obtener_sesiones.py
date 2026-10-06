from app.dominio.auth.repositorio_sesiones import RepositorioSesiones
from app.dominio.auth.sesion_con_usuario import SesionConUsuario


class ObtenerSesionesUseCase:

    def __init__(self, repositorio: RepositorioSesiones) -> None:
        self.repositorio = repositorio

    def ejecutar_paginado(
        self,
        texto_busqueda: str | None,
        rut_usuario: str | None,
        estado: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[SesionConUsuario], int]:
        return self.repositorio.obtener_sesiones_paginadas(
            texto_busqueda=texto_busqueda,
            rut_usuario=rut_usuario,
            estado=estado,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )