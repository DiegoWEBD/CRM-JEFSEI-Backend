from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class ObtenerNotificacionesUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar_paginado(
        self,
        rut_usuario: str,
        pagina: int,
        tamano_pagina: int,
        no_leidas: bool | None = None,
        nivel: str | None = None,
        codigo_tipo: str | None = None,
    ) -> tuple[list[Notificacion], int]:
        return self.repositorio_notificaciones.obtener_paginado(
            rut_usuario=rut_usuario,
            no_leidas=no_leidas,
            nivel=nivel,
            codigo_tipo=codigo_tipo,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
