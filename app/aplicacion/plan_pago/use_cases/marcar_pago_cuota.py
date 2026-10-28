from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.usuario.usuario import Usuario


class MarcarPagoCuotaUseCase:

    def __init__(
        self,
        repositorio_planes_pago: RepositorioPlanesPago,
        authorization_service: AuthorizationService
    ):
        self.repositorio_planes_pago = repositorio_planes_pago
        self.authorization_service = authorization_service

    def ejecutar(self, id_cuota: int, usuario: Usuario) -> None:
        cuota = self.repositorio_planes_pago.buscar_cuota_por_id(id_cuota)

        if cuota is None or cuota.id is None:
            raise RecursoNoEncontradoException(f'Cuota {id_cuota} no encontrada')

        if not self.authorization_service.usuario_puede_marcar_pago_cuota(usuario, cuota):
            raise UsuarioNoAutorizadoException('Esta acción sólo puede realizarla el ejecutivo de cobranza asignado')

        if cuota.pagado:
            raise ConflictoEnAccionException(f'La cuota {id_cuota} ya se encuentra pagada')

        cuota.marcar_como_pagada()

        self.repositorio_planes_pago.actualizar_cuota(cuota.id, cuota.pagado, cuota.fecha_pago)
