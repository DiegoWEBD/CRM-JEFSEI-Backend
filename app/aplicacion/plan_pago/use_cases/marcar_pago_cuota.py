from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago


class MarcarPagoCuotaUseCase:

    def __init__(self, repositorio_planes_pago: RepositorioPlanesPago):
        self.repositorio_planes_pago = repositorio_planes_pago

    def ejecutar(self, id_cuota: int) -> None:
        cuota = self.repositorio_planes_pago.buscar_cuota_por_id(id_cuota)

        if cuota is None or cuota.id is None:
            raise RecursoNoEncontradoException(f'Cuota {id_cuota} no encontrada')

        if cuota.pagado:
            raise ConflictoEnAccionException(f'La cuota {id_cuota} ya se encuentra pagada')

        cuota.marcar_como_pagada()

        self.repositorio_planes_pago.actualizar_cuota(cuota.id, cuota.pagado, cuota.fecha_pago)
