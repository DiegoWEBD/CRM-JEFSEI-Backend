from app.dominio.comunicado_gerencia.comunicado_gerencia import ComunicadoGerencia
from app.dominio.comunicado_gerencia.repositorio_comunicados_gerencia import RepositorioComunicadosGerencia


class ObtenerComunicadosGerenciaUseCase:
    def __init__(self, repositorio_comunicados_gerencia: RepositorioComunicadosGerencia):
        self.repositorio_comunicados_gerencia = repositorio_comunicados_gerencia

    def ejecutar(self) -> list[ComunicadoGerencia]:
        return self.repositorio_comunicados_gerencia.obtener_todos()