import math

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.usuario.usuario import Usuario

# Marca los campos del cambio que no vienen informados (sin cambio).
SIN_CAMBIO = object()


class CambioUnidadAlicuota:
    """Configuración nueva de una unidad de la alícuota.

    `None` en `monto_asegurado_personalizado` vuelve la unidad al monto
    sugerido; pasar `SIN_CAMBIO` deja el valor actual.
    """

    def __init__(
        self,
        id_unidad: int,
        descartada=SIN_CAMBIO,
        monto_asegurado_personalizado=SIN_CAMBIO,
    ) -> None:
        self.id_unidad = id_unidad
        self.descartada = descartada
        self.monto_asegurado_personalizado = monto_asegurado_personalizado


class AdministrarUnidadesAlicuotaUseCase:
    """Administra la configuración de procesamiento de las unidades de la alícuota.

    Recibe el lote de unidades a modificar y lo aplica de una sola vez (una
    única transacción): o se aplican todos los cambios o ninguno. Por cada
    unidad se puede:

    - descartarla del procesamiento (flag: no se elimina de la alícuota), y
    - fijar un monto asegurado personalizado (UF) que reemplaza al sugerido
      por el sistema en todos los cálculos (reparto de primas y cuotas).

    `None` en `monto_asegurado_personalizado` vuelve la unidad al monto
    sugerido; `SIN_CAMBIO` deja el valor actual.
    """

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_unidades = repositorio_unidades
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id_proceso_comercial: int,
        cambios: list[CambioUnidadAlicuota],
        usuario: Usuario,
    ) -> list[UnidadAlicuota]:
        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso or not proceso.id:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_administrar_alicuotas(usuario, proceso.id):
            raise UsuarioNoAutorizadoException(
                'Solo el ejecutivo de evaluación asignado al prospecto puede administrar la alícuota'
            )

        if proceso.cerrado:
            raise ConflictoEnAccionException('La oportunidad está cerrada')

        if proceso.producto.codigo != 'unidades':
            raise ConflictoEnAccionException('La alícuota solo aplica a oportunidades de unidades')

        if not cambios:
            raise ConflictoEnAccionException('No hay cambios que aplicar en las unidades de la alícuota')

        self._validar_lote(cambios)

        # Todo se valida antes de tocar nada: si un cambio es inválido no se
        # persiste ninguno (todo-o-nada).
        unidades = self.repositorio_unidades.listar_por_oportunidad(proceso.id)
        unidades_por_id = {unidad.id: unidad for unidad in unidades}

        faltantes = [cambio.id_unidad for cambio in cambios if cambio.id_unidad not in unidades_por_id]

        if faltantes:
            raise RecursoNoEncontradoException(
                'Unidades no encontradas en la alícuota de la oportunidad: '
                + ', '.join(str(id_unidad) for id_unidad in faltantes)
            )

        actualizadas = []

        for cambio in cambios:
            unidad = unidades_por_id[cambio.id_unidad]

            if cambio.descartada is not SIN_CAMBIO:
                unidad.descartada = bool(cambio.descartada)

            if cambio.monto_asegurado_personalizado is not SIN_CAMBIO:
                unidad.monto_asegurado_personalizado = (
                    float(cambio.monto_asegurado_personalizado)
                    if cambio.monto_asegurado_personalizado is not None
                    else None
                )

            actualizadas.append(unidad)

        self.repositorio_unidades.actualizar_unidades(actualizadas)

        return actualizadas

    def _validar_lote(self, cambios: list[CambioUnidadAlicuota]) -> None:
        vistos = set()

        for cambio in cambios:
            if cambio.id_unidad in vistos:
                raise ConflictoEnAccionException(
                    f'La unidad {cambio.id_unidad} está repetida en los cambios'
                )

            vistos.add(cambio.id_unidad)

            monto = cambio.monto_asegurado_personalizado

            if monto is not SIN_CAMBIO and monto is not None:
                if not isinstance(monto, (int, float)) or not math.isfinite(monto) or monto <= 0:
                    raise ConflictoEnAccionException(
                        'El monto asegurado personalizado debe ser un monto mayor a cero '
                        f'(unidad {cambio.id_unidad})'
                    )
