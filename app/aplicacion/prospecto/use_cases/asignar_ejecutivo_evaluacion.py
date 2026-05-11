from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class AsignarEjecutivoEvaluacionUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_prospecto: int, rut_ej_evaluacion: str):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if prospecto is None:
            raise ValueError("Prospecto no encontrado")
        
        if prospecto.evaluacion_riesgo is None:
            raise Exception("Primero debe asignar un ejecutivo comercial al prospecto")
        
        if prospecto.evaluacion_riesgo.ej_evaluacion is not None:
            raise Exception("El prospecto ya tiene un ejecutivo de evaluación de proyectos asignado")
        
        ejecutivo_evaluacion = self.repositorio_usuarios.buscar(rut_ej_evaluacion)
        
        if ejecutivo_evaluacion is None:
            raise ValueError("Ejecutivo de evaluación no encontrado")

        prospecto.evaluacion_riesgo.ej_evaluacion = ejecutivo_evaluacion
        self.repositorio_prospectos.asignar_ejecutivo_evaluacion_proyectos(prospecto)