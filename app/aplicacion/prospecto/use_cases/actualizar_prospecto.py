from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ActualizarProspectoUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(
        self,
        id: int,
        rut_usuario: str,
        rut_riesgo: str | None,
        nombre_riesgo: str,
        telefono_contacto: str | None, 
        correo_contacto: str | None, 
        direccion: str | None, 
        region: str | None,
        comuna: str | None, 
        observaciones: str | None
    ) -> None:
        
        prospecto = self.repositorio_prospectos.buscar(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if not prospecto.ejecutivo_comercial_asignado or prospecto.ejecutivo_comercial_asignado.rut != rut_usuario:
            raise UsuarioNoAutorizadoException

        prospecto.rut_riesgo = rut_riesgo
        prospecto.nombre_riesgo = nombre_riesgo
        prospecto.telefono_contacto = telefono_contacto
        prospecto.correo_contacto = correo_contacto
        prospecto.direccion = direccion
        prospecto.region = region
        prospecto.comuna = comuna
        prospecto.observaciones = observaciones

        self.repositorio_prospectos.actualizar_prospecto(prospecto)
