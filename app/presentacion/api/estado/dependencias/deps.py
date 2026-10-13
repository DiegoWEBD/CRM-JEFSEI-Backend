from app.aplicacion.estado.use_cases.actualizar_estado_configuracion import ActualizarEstadoConfiguracionUseCase
from app.aplicacion.estado.use_cases.actualizar_transicion import ActualizarTransicionUseCase
from app.aplicacion.estado.use_cases.crear_transicion import CrearTransicionUseCase
from app.aplicacion.estado.use_cases.eliminar_transicion import EliminarTransicionUseCase
from app.aplicacion.estado.use_cases.obtener_estados_configuracion import ObtenerEstadosConfiguracionUseCase
from app.aplicacion.estado.use_cases.obtener_transiciones_admin import ObtenerTransicionesAdminUseCase
from app.aplicacion.estado.use_cases.obtener_transiciones_manuales import ObtenerTransicionesManualesUseCase
from app.infraestructura.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial_postgres import RepositorioEstadosProcesoComercialPostgres


def get_obtener_transiciones_manuales_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return ObtenerTransicionesManualesUseCase(
        repositorio_estados=repositorio_estados,
    )


def get_obtener_estados_configuracion_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return ObtenerEstadosConfiguracionUseCase(
        repositorio_estados=repositorio_estados,
    )


def get_actualizar_estado_configuracion_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return ActualizarEstadoConfiguracionUseCase(
        repositorio_estados=repositorio_estados,
    )


def get_obtener_transiciones_admin_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return ObtenerTransicionesAdminUseCase(
        repositorio_estados=repositorio_estados,
    )


def get_crear_transicion_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return CrearTransicionUseCase(
        repositorio_estados=repositorio_estados,
    )


def get_actualizar_transicion_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return ActualizarTransicionUseCase(
        repositorio_estados=repositorio_estados,
    )


def get_eliminar_transicion_use_case():
    repositorio_estados = RepositorioEstadosProcesoComercialPostgres()

    return EliminarTransicionUseCase(
        repositorio_estados=repositorio_estados,
    )
