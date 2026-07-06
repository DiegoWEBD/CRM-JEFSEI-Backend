from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios

ID_CONDOMINIO = 10
ID_LINEAS_PERSONALES = 11


class RegistrarProspectoUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def _crear_linea_negocio(self, id_linea_negocio: int) -> LineaNegocio:
        return LineaNegocio(id=id_linea_negocio, nombre='')

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
        id_linea_negocio: int,  
        uf_por_metro_cuadrado: float | None = None,
        porcentaje_depreciacion: float | None = None,
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
        metros_cuadrados: float | None = None
    ) -> int:

        if id_linea_negocio == ID_LINEAS_PERSONALES:
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
                id_linea_negocio=id_linea_negocio
            )

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
            id_linea_negocio=id_linea_negocio,
            uf_por_metro_cuadrado=uf_por_metro_cuadrado,
            porcentaje_depreciacion=porcentaje_depreciacion,
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
            metros_cuadrados=metros_cuadrados
        )

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
        id_linea_negocio: int
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
            linea_negocio=self._crear_linea_negocio(id_linea_negocio),
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=registrado_por,
            informacion_completa=False
        )

        return self.repositorio_prospectos.registrar_prospecto(prospecto)

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
        id_linea_negocio: int,
        uf_por_metro_cuadrado: float | None,
        porcentaje_depreciacion: float | None,
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
        metros_cuadrados: float | None
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
            linea_negocio=self._crear_linea_negocio(id_linea_negocio),
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
            uf_por_metro_cuadrado=uf_por_metro_cuadrado,
            porcentaje_depreciacion=porcentaje_depreciacion,
            porcentaje_espacios_comunes=porcentaje_espacios_comunes,
            id_cliente=None,
            informacion_completa=False,
            planificacion_prospecto=None,
            materialidad=materialidad,
            clasificacion_preliminar_incendio=clasificacion_preliminar_incendio,
            procesos_productivos=procesos_productivos,
            ubicacion_piscina=ubicacion_piscina,
            tiene_alarma_incendio=tiene_alarma_incendio,
            tiene_sprinklers=tiene_sprinklers
        )
        
        return self.repositorio_prospectos.registrar_prospecto_condominio(prospecto)