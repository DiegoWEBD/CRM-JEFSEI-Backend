from abc import ABC, abstractmethod

from app.dominio.comunicado_gerencia.comunicado_gerencia import ComunicadoGerencia


class RepositorioComunicadosGerencia(ABC):

    @abstractmethod
    def obtener_todos(self) -> list[ComunicadoGerencia]:
        pass