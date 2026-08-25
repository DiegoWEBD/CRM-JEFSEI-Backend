from datetime import datetime

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario


class ActualizarPolizaUseCase:

    def __init__(
        self,
        repositorio_polizas: RepositorioPolizas,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_polizas = repositorio_polizas
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        numero_poliza: str,
        usuario: Usuario,
        tipo: str,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime | None,
        inicio_vigencia: datetime | None,
        fin_vigencia: datetime | None,
        id_company: int | None,
    ) -> None:
        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if not poliza:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if not self.authorization_service.usuario_puede_actualizar_poliza(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException()

        self.repositorio_polizas.actualizar(
            numero_poliza=numero_poliza,
            tipo=tipo,
            prima_neta=prima_neta,
            comision_corredora_pct=comision_corredora_pct,
            fecha_emision=fecha_emision,
            inicio_vigencia=inicio_vigencia,
            fin_vigencia=fin_vigencia,
            id_company=id_company,
        )
