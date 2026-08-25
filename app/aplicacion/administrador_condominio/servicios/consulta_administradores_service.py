from abc import ABC, abstractmethod


class ConsultaAdministradoresService(ABC):

    @abstractmethod
    def obtener_todos(
        self,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 25,
    ) -> dict:
        pass
