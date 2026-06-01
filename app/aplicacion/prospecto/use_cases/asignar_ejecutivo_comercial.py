from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoComercialUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos, 
        repositorio_usuarios: RepositorioUsuarios
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_prospecto: int, rut_ej_comercial: str, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto:
            raise ValueError('Prospecto no encontrado')
        
        if prospecto.proceso_comercial.ejecutivo_comercial:
            raise Exception('El prospecto ya tiene un ejecutivo comercial asignado')
        
        usuario = self.repositorio_usuarios.buscar(rut_ej_comercial)

        if not usuario:
            raise ValueError('Ejecutivo comercial no encontrado')
        
        es_ejecutivo_comercial = False

        for rol in usuario.roles:
            if rol.codigo == 'EJECUTIVO_COMERCIAL':
                es_ejecutivo_comercial = True
                break

        if not es_ejecutivo_comercial:
            raise Exception(f'El usuario {rut_ej_comercial} no es ejecutivo comercial')

        prospecto.proceso_comercial.ejecutivo_comercial = usuario
        self.repositorio_prospectos.asignar_ejecutivo_comercial(prospecto, asignado_por)