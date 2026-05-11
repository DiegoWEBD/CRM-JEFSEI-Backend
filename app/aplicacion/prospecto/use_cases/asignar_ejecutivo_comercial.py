from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class AsignarEjecutivoComercialUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_prospecto: int, rut_ej_comercial: str):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if prospecto is None:
            raise ValueError("Prospecto no encontrado")
        
        if prospecto.evaluacion_riesgo is not None:
            raise Exception("El prospecto ya tiene un ejecutivo comercial asignado")
        
        ejecutivo_comercial = self.repositorio_usuarios.buscar(rut_ej_comercial)
        if ejecutivo_comercial is None:
            raise ValueError("Ejecutivo comercial no encontrado")

        evaluacion_riesgo = EvaluacionRiesgo(
            cotizaciones=[],
            ej_comercial=ejecutivo_comercial,
        )

        prospecto.evaluacion_riesgo = evaluacion_riesgo
        self.repositorio_prospectos.asignar_ejecutivo_comercial(prospecto)