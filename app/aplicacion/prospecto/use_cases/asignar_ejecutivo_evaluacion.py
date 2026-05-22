from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class AsignarEjecutivoEvaluacionUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_prospecto: int, rut_ej_evaluacion: str):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto:
            raise ValueError('Prospecto no encontrado')
        
        if prospecto.ejecutivo_comercial_asignado:
            raise Exception('El prospecto ya tiene un ejecutivo de evaluación de proyectos asignado')
        
        usuario = self.repositorio_usuarios.buscar(rut_ej_evaluacion)

        if not usuario:
            raise ValueError('Ejecutivo no encontrado')
        
        es_ejecutivo_comercial = False

        for rol in usuario.roles:
            if rol.codigo == 'EJECUTIVO_EVALUACION_PROYECTO':
                es_ejecutivo_comercial = True
                break

        if not es_ejecutivo_comercial:
            raise Exception(f'El usuario {rut_ej_evaluacion} no es ejecutivo de evaluación de proyectos')

        prospecto.ejecutivo_comercial_asignado = usuario
        self.repositorio_prospectos.asignar_ejecutivo_evaluacion_proyectos(prospecto)