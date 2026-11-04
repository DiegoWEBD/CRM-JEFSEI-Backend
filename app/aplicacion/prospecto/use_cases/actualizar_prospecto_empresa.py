from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.prospecto_empresa.giro_comercial import GiroComercial
from app.dominio.prospecto.prospecto_empresa.servicio_giros_comerciales import ServicioGirosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.infraestructura.lib.normalizar_rut import normalizar_rut
from app.infraestructura.lib.normalizar_texto import normalizar_texto


class ActualizarProspectoEmpresaUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(
        self,
        id: int,
        rut_usuario: str,
        rut_riesgo: str | None,
        nombre_riesgo: str,
        telefono_contacto: str | None,
        correo_contacto: str | None,
        direccion: str | None,
        region: str | None,
        comuna: str | None,
        observaciones: str | None,
        nombre_fantasia: str | None,
        cantidad_trabajadores: int | None,
        giros_comerciales: list[str]
    ):
        
        prospecto = self.repositorio_prospectos.buscar_prospecto_empresa(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if not prospecto.ejecutivo_comercial_asignado or prospecto.ejecutivo_comercial_asignado.rut != rut_usuario:
            raise UsuarioNoAutorizadoException

        if normalizar_texto(prospecto.nombre_riesgo) != normalizar_texto(nombre_riesgo):
            nombre_existente = self.repositorio_prospectos.buscar_prospecto_por_nombre(nombre_riesgo)
            if nombre_existente:
                es_cliente = nombre_existente.id_cliente is not None
                raise RecursoYaExisteException(f'El {"cliente" if es_cliente else "prospecto"} {nombre_riesgo} ya está registrado')

        if rut_riesgo and normalizar_rut(prospecto.rut_riesgo) != normalizar_rut(rut_riesgo):
            rut_existente = self.repositorio_prospectos.buscar_prospecto_por_rut(rut_riesgo)
            if rut_existente:
                es_cliente = rut_existente.id_cliente is not None
                raise RecursoYaExisteException(f'El {"cliente" if es_cliente else "prospecto"} {rut_riesgo} ya está registrado')

        self._validar_giros_comerciales(id, prospecto.giros_comerciales, giros_comerciales)

        prospecto.rut_riesgo = rut_riesgo
        prospecto.nombre_riesgo = nombre_riesgo
        prospecto.telefono_contacto = telefono_contacto
        prospecto.correo_contacto = correo_contacto
        prospecto.direccion = direccion
        prospecto.region = region
        prospecto.comuna = comuna
        prospecto.observaciones = observaciones
        prospecto.nombre_fantasia = nombre_fantasia
        prospecto.cantidad_trabajadores = cantidad_trabajadores
        prospecto.giros_comerciales = [GiroComercial(nombre=nombre) for nombre in giros_comerciales]

        self.repositorio_prospectos.actualizar_prospecto_empresa(prospecto)

    def _validar_giros_comerciales(
        self,
        id_prospecto: int,
        giros_registrados: list[GiroComercial],
        giros_comerciales: list[str]
    ) -> None:
        """Valida los giros antes de reemplazar la lista registrada.

        No se permiten nombres vacíos ni repetidos en la solicitud, ni
        registrar un giro cuyo nombre ya esté registrado para la empresa
        (ignorando mayúsculas y tildes), salvo que sea exactamente el
        mismo giro que ya estaba registrado y se esté conservando.
        """
        ServicioGirosComerciales.validar_nombres(giros_comerciales)

        nombres_registrados = {giro.nombre for giro in giros_registrados}

        for nombre in giros_comerciales:
            if nombre in nombres_registrados:
                continue

            if self.repositorio_prospectos.existe_giro_comercial_por_nombre(id_prospecto, nombre):
                raise RecursoYaExisteException(f'El giro comercial {nombre} ya está registrado para la empresa')
