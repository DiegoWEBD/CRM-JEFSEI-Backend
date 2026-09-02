from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class ObtenerUsuariosUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self) -> list[Usuario]:
        return self.repositorio_usuarios.obtener_todos()

    def ejecutar_paginado(
        self,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 15,
    ) -> tuple[list[Usuario], int]:
        return self.repositorio_usuarios.obtener_paginados(
            texto_busqueda=texto_busqueda,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
    