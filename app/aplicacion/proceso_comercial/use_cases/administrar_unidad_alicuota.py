import math

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.usuario.usuario import Usuario

# Marca los campos del request que no vienen informados (sin cambio).
SIN_CAMBIO = object()


class AdministrarUnidadAlicuotaUseCase:
    """Administra la configuración de procesamiento de una unidad de la alícuota.

    Por cada unidad se puede:
    - descartarla del procesamiento (flag: no se elimina de la alícuota), y
    - fijar un monto asegurado personalizado (UF) que reemplaza al sugerido
      por el sistema en todos los cálculos (reparto de primas y cuotas).

    `None` en `monto_asegurado_personalizado` vuelve la unidad al monto
    sugerido; pasar `SIN_CAMBIO` deja el valor actual.
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
        id_unidad: int,
        usuario: Usuario,
        descartada=SIN_CAMBIO,
        monto_asegurado_personalizado=SIN_CAMBIO,
    ) -> UnidadAlicuota:
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

        unidad = self.repositorio_unidades.buscar_por_id(id_unidad, proceso.id)

        if unidad is None:
            raise RecursoNoEncontradoException('Unidad no encontrada en la alícuota de la oportunidad')

        if descartada is not SIN_CAMBIO:
            unidad.descartada = bool(descartada)

        if monto_asegurado_personalizado is not SIN_CAMBIO:
            if monto_asegurado_personalizado is not None:
                if (
                    not isinstance(monto_asegurado_personalizado, (int, float))
                    or not math.isfinite(monto_asegurado_personalizado)
                    or monto_asegurado_personalizado <= 0
                ):
                    raise ConflictoEnAccionException(
                        'El monto asegurado personalizado debe ser un monto mayor a cero'
                    )

            unidad.monto_asegurado_personalizado = (
                float(monto_asegurado_personalizado) if monto_asegurado_personalizado is not None else None
            )

        self.repositorio_unidades.actualizar_unidad(
            unidad.id,
            unidad.descartada,
            unidad.monto_asegurado_personalizado,
        )

        return unidad
