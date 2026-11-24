from app.aplicacion.administrador_condominio.servicios.consulta_administradores_service import (
    ConsultaAdministradoresService,
)
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario


class ObtenerAdministradoresUseCase:
    """Listado paginado de administradores de condominio (datos básicos y PII de
    contacto). No incluye la relación de condominios bajo administración."""

    def __init__(
        self,
        consulta_service: ConsultaAdministradoresService,
        authorization_service: AuthorizationService,
    ):
        self.consulta_service = consulta_service
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        usuario: Usuario,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 25,
    ) -> dict:
        if not self.authorization_service.usuario_puede_ver_administradores(usuario):
            raise UsuarioNoAutorizadoException(
                "No tiene permiso para ver administradores de condominio"
            )

        return self.consulta_service.obtener_todos(
            texto_busqueda=texto_busqueda,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
