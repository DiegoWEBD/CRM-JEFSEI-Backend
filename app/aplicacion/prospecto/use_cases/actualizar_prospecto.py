from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.infraestructura.lib.normalizar_rut import normalizar_rut
from app.infraestructura.lib.normalizar_texto import normalizar_texto


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

        if normalizar_texto(prospecto.nombre_riesgo) != normalizar_texto(nombre_riesgo):
            nombre_existente = self.repositorio_prospectos.buscar_prospecto_por_nombre(nombre_riesgo)
            if nombre_existente:
                es_cliente = nombre_existente.id_cliente is not None
                raise RecursoYaExisteException(f'El {"cliente" if es_cliente else "prospecto"} {nombre_riesgo} ya está registrado')

        if rut_riesgo and normalizar_rut(prospecto.rut_riesgo) != normalizar_rut(rut_riesgo):
            rut_existente = self.repositorio_prospectos.buscar_prospecto_por_rut(rut_riesgo)
            if rut_existente:
                es_cliente = rut_existente.id_cliente is not None
                raise RecursoYaExisteException(f'El {"cliente" if es_cliente else "prospecto"} {rut_riesgo} ya está registrado')
        
        prospecto_condominio = self.repositorio_prospectos.buscar_prospecto_condominio(id)
        
        if prospecto_condominio:
            prospecto_condominio.rut_riesgo = rut_riesgo
            prospecto_condominio.nombre_riesgo = nombre_riesgo
            prospecto_condominio.telefono_contacto = telefono_contacto
            prospecto_condominio.correo_contacto = correo_contacto
            prospecto_condominio.direccion = direccion
            prospecto_condominio.region = region
            prospecto_condominio.comuna = comuna
            prospecto_condominio.observaciones = observaciones

            self.repositorio_prospectos.actualizar_prospecto_condominio(prospecto_condominio)
        else:
            prospecto.rut_riesgo = rut_riesgo
            prospecto.nombre_riesgo = nombre_riesgo
            prospecto.telefono_contacto = telefono_contacto
            prospecto.correo_contacto = correo_contacto
            prospecto.direccion = direccion
            prospecto.region = region
            prospecto.comuna = comuna
            prospecto.observaciones = observaciones

            self.repositorio_prospectos.actualizar_prospecto(prospecto)
            
