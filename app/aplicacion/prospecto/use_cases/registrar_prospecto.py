from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class RegistrarProspectoUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

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

        linea_negocio = LineaNegocio(
            id=id_linea_negocio,
            nombre=''
        )

        registrado_por = self.repositorio_usuarios.buscar(rut_usuario)

        if not registrado_por:
            raise RecursoNoEncontradoException(f'Usuario {rut_usuario} no encontrado')

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