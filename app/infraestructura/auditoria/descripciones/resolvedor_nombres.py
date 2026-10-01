import logging
from dataclasses import dataclass

from app.infraestructura.administrador_condominio.repositorio_administradores_postgres import RepositorioAdministradoresPostgres
from app.infraestructura.archivo.repositorio_archivos_postgres import RepositorioArchivosPostgres
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.contacto.repositorio_contactos_postgres import RepositorioContactosPostgres
from app.infraestructura.linea_negocio.repositorio_lineas_negocio_postgres import RepositorioLineasNegocioPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.producto.repositorio_producto_postgres import RepositorioProductoPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres

logger = logging.getLogger('auditoria')


@dataclass
class DatosOportunidad:
    producto: str | None = None
    cliente: str | None = None
    id_prospecto: int | None = None


class ResolvedorNombres:
    """Resuelve nombres legibles de entidades para las frases de auditoría.

    Toda consulta es best-effort: si falla o no existe, devuelve None y la
    frase cae al texto genérico. El nombre queda congelado al momento del
    hecho (fidelidad de auditoría), no el que tenga la entidad después.
    """

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectosPostgres | None = None,
        repositorio_usuarios: RepositorioUsuariosPostgres | None = None,
        repositorio_polizas: RepositorioPolizasPostgres | None = None,
        repositorio_companies: RepositorioCompanySegurosPostgres | None = None,
        repositorio_productos: RepositorioProductoPostgres | None = None,
        repositorio_lineas_negocio: RepositorioLineasNegocioPostgres | None = None,
        repositorio_contactos: RepositorioContactosPostgres | None = None,
        repositorio_procesos_comerciales: RepositorioProcesosComercialesPostgres | None = None,
        repositorio_archivos: RepositorioArchivosPostgres | None = None,
        repositorio_administradores: RepositorioAdministradoresPostgres | None = None,
    ) -> None:
        self.repositorio_prospectos = repositorio_prospectos or RepositorioProspectosPostgres()
        self.repositorio_usuarios = repositorio_usuarios or RepositorioUsuariosPostgres()
        self.repositorio_polizas = repositorio_polizas or RepositorioPolizasPostgres()
        self.repositorio_companies = repositorio_companies or RepositorioCompanySegurosPostgres()
        self.repositorio_productos = repositorio_productos or RepositorioProductoPostgres()
        self.repositorio_lineas_negocio = repositorio_lineas_negocio or RepositorioLineasNegocioPostgres()
        self.repositorio_contactos = repositorio_contactos or RepositorioContactosPostgres()
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales or RepositorioProcesosComercialesPostgres()
        self.repositorio_archivos = repositorio_archivos or RepositorioArchivosPostgres()
        self.repositorio_administradores = repositorio_administradores or RepositorioAdministradoresPostgres()

    def _resolver(self, consulta, etiqueta: str):
        try:
            return consulta()
        except Exception:
            logger.exception('No se pudo resolver %s para la descripción de auditoría', etiqueta)
            return None

    def nombre_prospecto(self, id_prospecto: int) -> str | None:
        prospecto = self._resolver(
            lambda: self.repositorio_prospectos.buscar(id_prospecto),
            f'prospecto {id_prospecto}',
        )
        return getattr(prospecto, 'nombre_riesgo', None)

    def nombre_cliente_por_id(self, id_cliente: int) -> str | None:
        prospecto = self._resolver(
            lambda: self.repositorio_prospectos.buscar_cliente(id_cliente),
            f'cliente {id_cliente}',
        )
        return getattr(prospecto, 'nombre_riesgo', None)

    def nombre_usuario(self, rut: str) -> str | None:
        usuario = self._resolver(
            lambda: self.repositorio_usuarios.buscar(rut),
            f'usuario {rut}',
        )
        return getattr(usuario, 'nombre', None)

    def nombre_cliente_poliza(self, numero_poliza: str) -> str | None:
        poliza = self._resolver(
            lambda: self.repositorio_polizas.buscar(numero_poliza),
            f'póliza {numero_poliza}',
        )
        return getattr(poliza, 'nombre_cliente', None)

    def nombre_company(self, id_company: int) -> str | None:
        company = self._resolver(
            lambda: self.repositorio_companies.buscar(id_company),
            f'company {id_company}',
        )
        return getattr(company, 'nombre', None)

    def nombre_producto(self, id_producto: int) -> str | None:
        producto = self._resolver(
            lambda: self.repositorio_productos.obtener_por_id(id_producto),
            f'producto {id_producto}',
        )
        return getattr(producto, 'nombre', None)

    def nombre_linea_negocio(self, id_linea_negocio: int) -> str | None:
        linea = self._resolver(
            lambda: self.repositorio_lineas_negocio.obtener_por_id(id_linea_negocio),
            f'linea de negocio {id_linea_negocio}',
        )
        return getattr(linea, 'nombre', None)

    def nombre_contacto(self, id_contacto: int) -> str | None:
        contacto = self._resolver(
            lambda: self.repositorio_contactos.buscar(id_contacto),
            f'contacto {id_contacto}',
        )
        return getattr(contacto, 'nombre', None)

    def datos_oportunidad(self, id_proceso: int) -> DatosOportunidad | None:
        proceso = self._resolver(
            lambda: self.repositorio_procesos_comerciales.buscar(id_proceso),
            f'proceso comercial {id_proceso}',
        )
        if proceso is None:
            return None
        producto = getattr(getattr(proceso, 'producto', None), 'nombre', None)
        return DatosOportunidad(
            producto=producto,
            cliente=getattr(proceso, 'nombre_cliente', None),
            id_prospecto=getattr(proceso, 'id_prospecto', None),
        )

    def nombre_archivo(self, id_archivo: int) -> str | None:
        archivo = self._resolver(
            lambda: self.repositorio_archivos.obtener_por_id(id_archivo),
            f'archivo {id_archivo}',
        )
        return getattr(archivo, 'nombre_original', None)

    def nombre_administrador(self, id_administrador: int) -> str | None:
        administrador = self._resolver(
            lambda: self.repositorio_administradores.buscar(id_administrador),
            f'administrador {id_administrador}',
        )
        return getattr(administrador, 'nombre_administrador', None)
