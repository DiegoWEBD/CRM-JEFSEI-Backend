from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class CambiarLineaNegocioProspectoUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(
        self,
        id: int,
        id_linea_negocio: int,
        usuario: Usuario
    ) -> None:
        
        prospecto = self.repositorio_prospectos.buscar(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if not prospecto.ejecutivo_comercial_asignado or prospecto.ejecutivo_comercial_asignado.rut != usuario.rut:
            raise UsuarioNoAutorizadoException
        
        prospecto.linea_negocio.id = id_linea_negocio

        self.repositorio_prospectos.actualizar_prospecto(prospecto)
            
