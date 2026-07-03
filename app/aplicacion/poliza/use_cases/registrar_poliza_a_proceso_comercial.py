from datetime import datetime

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class RegistrarPolizaAProcesoComercialUseCase:

    def __init__(
        self,
        repositorio_polizas: RepositorioPolizas,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_companies: RepositorioCompanySeguros,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_companies = repositorio_companies
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id_proceso_comercial: int,
        numero_poliza: str, 
        tipo: str,
        id_company: int,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime,
        inicio_vigencia: datetime,
        fin_vigencia: datetime,
        usuario: Usuario
    ):
        if self.repositorio_polizas.buscar(numero_poliza):
            raise RecursoYaExisteException(f'La póliza {numero_poliza} ya se encuentra registrada')

        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')
        
        if not self.authorization_service.usuario_puede_subir_poliza(usuario.rut, id_proceso_comercial):
            raise UsuarioNoAutorizadoException

        company = self.repositorio_companies.buscar(id_company)

        if not company:
            raise RecursoNoEncontradoException('Compañía no encontrada')
        
        poliza = Poliza(
            numero_poliza=numero_poliza,
            id_proceso_comercial=id_proceso_comercial,
            tipo=tipo,
            nombre_producto='',
            company=company,
            prima_neta=prima_neta,
            comision_corredora_pct=comision_corredora_pct,
            fecha_emision=fecha_emision,
            inicio_vigencia=inicio_vigencia,
            fin_vigencia=fin_vigencia,
            estado=EstadoPoliza.REGISTRADA,
            renovacion_cotizada=False
        )

        self.repositorio_polizas.registrar_a_proceso_comercial(poliza, id_proceso_comercial, usuario.rut)