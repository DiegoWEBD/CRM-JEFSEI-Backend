from datetime import datetime

from app.dominio.comunicado_gerencia.comunicado_gerencia import ComunicadoGerencia
from app.dominio.comunicado_gerencia.repositorio_comunicados_gerencia import RepositorioComunicadosGerencia
from app.dominio.usuario.usuario import Usuario


class RegistrarComunicadoGerenciaUseCase:
    def __init__(self, repositorio: RepositorioComunicadosGerencia):
        self.repositorio = repositorio

    def ejecutar(
        self,
        usuario: Usuario,
        titulo: str,
        descripcion: str,
        prioridad: str,
        caducidad: datetime
    ) -> bool:
        comunicado = ComunicadoGerencia(
            id=None,
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            fecha=datetime.now(),
            caducidad=caducidad,
            nombre_gerente=usuario.nombre
        )

        return self.repositorio.registrar(comunicado, usuario.rut)
