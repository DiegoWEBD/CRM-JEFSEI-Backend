from datetime import datetime

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion


class RegistrarCotizacionASolicitudUseCase:

    def __init__(
        self, 
        repositorio_companies: RepositorioCompanySeguros,
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_cotizaciones: RepositorioCotizaciones,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.authorization_service = authorization_service
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_companies = repositorio_companies

    def ejecutar(
        self, 
        rut_usuario: str,
        id_solicitud: int, 
        monto_total_asegurado: float,
        tasa_afecta: float,
        tasa_excenta: float,
        tasa_politica: float,
        prima_adicional_asistencia: float,
        id_company: int,
        fecha_emision: datetime,
        fecha_vencimiento: datetime,
        
    ):

        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud):
            raise RecursoNoEncontradoException('Solicitud no encontrada')
        
        if not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(rut_usuario, id_solicitud):
            raise UsuarioNoAutorizadoException
        
        if self.repositorio_companies.buscar(id_company) is None:
            raise RecursoNoEncontradoException('Compañía no encontrada')
        
        company = CompanySeguros(
            id=id_company,
            nombre='' # Valor genérico, no es utilizado
        )

        cotizacion = Cotizacion(
            id=None,
            monto_total_asegurado=monto_total_asegurado,
            tasa_afecta=tasa_afecta,
            tasa_excenta=tasa_excenta,
            tasa_politica=tasa_politica,
            prima_adicional_asistencia=prima_adicional_asistencia,
            company=company,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento
        )

        self.repositorio_cotizaciones.registrar_cotizacion_a_solicitud(id_solicitud, cotizacion, rut_usuario)