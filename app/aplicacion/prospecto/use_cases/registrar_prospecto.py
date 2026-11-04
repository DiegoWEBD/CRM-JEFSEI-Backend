from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.linea_negocio.linea_negocio import (
    CODIGO_LINEA_CONDOMINIOS,
    CODIGO_LINEAS_COMERCIALES,
    CODIGO_LINEAS_PERSONALES,
    LineaNegocio,
)
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.prospecto_empresa.giro_comercial import GiroComercial
from app.dominio.prospecto.prospecto_empresa.prospecto_empresa import ProspectoEmpresa
from app.dominio.prospecto.prospecto_empresa.servicio_giros_comerciales import ServicioGirosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class RegistrarProspectoUseCase:

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_lineas_negocio: RepositorioLineasNegocio
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_lineas_negocio = repositorio_lineas_negocio

    def _buscar_registrado_por(self, rut_usuario: str):
        registrado_por = self.repositorio_usuarios.buscar(rut_usuario)
        if not registrado_por:
            raise RecursoNoEncontradoException(f'Usuario {rut_usuario} no encontrado')
        return registrado_por

    def ejecutar(
        self,
        rut_usuario: str,
        rut_riesgo: str | None,
        id_administrador: int | None,
        nombre_riesgo: str,
        telefono_contacto: str | None, 
        correo_contacto: str | None, 
        direccion: str | None, 
        region: str | None,
        comuna: str | None, 
        observaciones: str | None, 
        codigo_linea_negocio: str,
        porcentaje_espacios_comunes: float | None = None,
        tiene_locales_comerciales: bool | None = None,
        uso_del_condominio: str | None = None,
        materialidad: str | None = None,
        clasificacion_preliminar_incendio: str | None = None,
        procesos_productivos: bool | None = None,
        numero_pisos: int | None = None,
        numero_torres: int | None = None,
        cantidad_departamentos: int | None = None,
        cantidad_subterraneos: int | None = None,
        tiene_piscina: bool | None = None,
        ubicacion_piscina: str | None = None,
        tiene_alarma_incendio: bool | None = None,
        tiene_sprinklers: bool | None = None,
        year_construccion: int | None = None,
        metros_cuadrados: float | None = None,
        condominio_vertical: bool | None = None,
        nombre_fantasia: str | None = None,
        cantidad_trabajadores: int | None = None,
        giros_comerciales: list[str] | None = None
    ) -> int:

        linea_negocio = self.repositorio_lineas_negocio.buscar_por_codigo(codigo_linea_negocio)

        if linea_negocio is None:
            raise DatoInvalidoException('La línea de negocio indicada no existe')

        nombre_existente = self.repositorio_prospectos.buscar_prospecto_por_nombre(nombre_riesgo)

        if nombre_existente:
            es_cliente = nombre_existente.id_cliente is not None
            raise RecursoYaExisteException(f'El {"cliente" if es_cliente else "prospecto"} {nombre_riesgo} ya está registrado')

        if rut_riesgo:
            rut_existente = self.repositorio_prospectos.buscar_prospecto_por_rut(rut_riesgo)

            if rut_existente:
                es_cliente = rut_existente.id_cliente is not None
                raise RecursoYaExisteException(f'El {"cliente" if es_cliente else "prospecto"} {rut_riesgo} ya está registrado')

        if codigo_linea_negocio == CODIGO_LINEAS_PERSONALES:
            return self._registrar_lineas_personales(
                rut_usuario=rut_usuario,
                rut_riesgo=rut_riesgo,
                nombre_riesgo=nombre_riesgo,
                telefono_contacto=telefono_contacto,
                correo_contacto=correo_contacto,
                direccion=direccion,
                region=region,
                comuna=comuna,
                observaciones=observaciones,
                linea_negocio=linea_negocio
            )

        if codigo_linea_negocio == CODIGO_LINEAS_COMERCIALES:
            return self._registrar_lineas_comerciales(
                rut_usuario=rut_usuario,
                rut_riesgo=rut_riesgo,
                nombre_riesgo=nombre_riesgo,
                telefono_contacto=telefono_contacto,
                correo_contacto=correo_contacto,
                direccion=direccion,
                region=region,
                comuna=comuna,
                observaciones=observaciones,
                linea_negocio=linea_negocio,
                nombre_fantasia=nombre_fantasia,
                cantidad_trabajadores=cantidad_trabajadores,
                giros_comerciales=giros_comerciales or []
            )

        if codigo_linea_negocio == CODIGO_LINEA_CONDOMINIOS:
            return self._registrar_condominio(
                rut_usuario=rut_usuario,
                rut_riesgo=rut_riesgo,
                id_administrador=id_administrador,
                nombre_riesgo=nombre_riesgo,
                telefono_contacto=telefono_contacto,
                correo_contacto=correo_contacto,
                direccion=direccion,
                region=region,
                comuna=comuna,
                observaciones=observaciones,
                linea_negocio=linea_negocio,
                porcentaje_espacios_comunes=porcentaje_espacios_comunes,
                tiene_locales_comerciales=tiene_locales_comerciales,
                uso_del_condominio=uso_del_condominio,
                materialidad=materialidad,
                clasificacion_preliminar_incendio=clasificacion_preliminar_incendio,
                procesos_productivos=procesos_productivos,
                numero_pisos=numero_pisos,
                numero_torres=numero_torres,
                cantidad_departamentos=cantidad_departamentos,
                cantidad_subterraneos=cantidad_subterraneos,
                tiene_piscina=tiene_piscina,
                ubicacion_piscina=ubicacion_piscina,
                tiene_alarma_incendio=tiene_alarma_incendio,
                tiene_sprinklers=tiene_sprinklers,
                year_construccion=year_construccion,
                metros_cuadrados=metros_cuadrados,
                condominio_vertical=condominio_vertical
            )

        raise DatoInvalidoException(f'La línea de negocio {codigo_linea_negocio} no está soportada')

    def _registrar_lineas_personales(
        self,
        rut_usuario: str,
        rut_riesgo: str | None,
        nombre_riesgo: str,
        telefono_contacto: str | None, 
        correo_contacto: str | None, 
        direccion: str | None, 
        region: str | None,
        comuna: str | None, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio
    ) -> int:
        registrado_por = self._buscar_registrado_por(rut_usuario)

        prospecto = Prospecto(
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            region=region,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=registrado_por,
            informacion_completa=False
        )

        return self.repositorio_prospectos.registrar_prospecto(prospecto)

    def _registrar_lineas_comerciales(
        self,
        rut_usuario: str,
        rut_riesgo: str | None,
        nombre_riesgo: str,
        telefono_contacto: str | None,
        correo_contacto: str | None,
        direccion: str | None,
        region: str | None,
        comuna: str | None,
        observaciones: str | None,
        linea_negocio: LineaNegocio,
        nombre_fantasia: str | None,
        cantidad_trabajadores: int | None,
        giros_comerciales: list[str]
    ) -> int:
        registrado_por = self._buscar_registrado_por(rut_usuario)

        ServicioGirosComerciales.validar_nombres(giros_comerciales)

        prospecto = ProspectoEmpresa(
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            region=region,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=registrado_por,
            informacion_completa=False,
            nombre_fantasia=nombre_fantasia,
            cantidad_trabajadores=cantidad_trabajadores,
            giros_comerciales=[GiroComercial(nombre=nombre) for nombre in giros_comerciales]
        )

        return self.repositorio_prospectos.registrar_prospecto_empresa(prospecto)

    def _registrar_condominio(
        self,
        rut_usuario: str,
        rut_riesgo: str | None,
        id_administrador: int | None,
        nombre_riesgo: str,
        telefono_contacto: str | None, 
        correo_contacto: str | None, 
        direccion: str | None, 
        region: str | None,
        comuna: str | None, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio,
        porcentaje_espacios_comunes: float | None,
        tiene_locales_comerciales: bool | None,
        uso_del_condominio: str | None,
        materialidad: str | None,
        clasificacion_preliminar_incendio: str | None,
        procesos_productivos: bool | None,
        numero_pisos: int | None,
        numero_torres: int | None,
        cantidad_departamentos: int | None,
        cantidad_subterraneos: int | None,
        tiene_piscina: bool | None,
        ubicacion_piscina: str | None,
        tiene_alarma_incendio: bool | None,
        tiene_sprinklers: bool | None,
        year_construccion: int | None,
        metros_cuadrados: float | None,
        condominio_vertical: bool | None
    ) -> int:
        registrado_por = self._buscar_registrado_por(rut_usuario)

        administrador = None
        if id_administrador is not None:
            administrador = AdministradorCondominio(
                id=id_administrador,
                nombre_administrador='',
                nombre_contacto='',
                telefono='',
                correo=''
            )

        prospecto = ProspectoCondominio(
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            administrador=administrador,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            region=region,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=registrado_por,
            ejecutivo_evaluacion_asignado=None,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            porcentaje_espacios_comunes=porcentaje_espacios_comunes,
            id_cliente=None,
            informacion_completa=False,
            planificacion_prospecto=None,
            materialidad=materialidad,
            clasificacion_preliminar_incendio=clasificacion_preliminar_incendio,
            procesos_productivos=procesos_productivos,
            ubicacion_piscina=ubicacion_piscina,
            tiene_alarma_incendio=tiene_alarma_incendio,
            tiene_sprinklers=tiene_sprinklers,
            condominio_vertical=condominio_vertical
        )
        
        return self.repositorio_prospectos.registrar_prospecto_condominio(prospecto)
