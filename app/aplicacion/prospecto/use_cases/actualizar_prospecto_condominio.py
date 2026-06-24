from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ActualizarProspectoCondominioUseCase:

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
    ):
        
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if not prospecto.ejecutivo_comercial_asignado or prospecto.ejecutivo_comercial_asignado.rut != rut_usuario:
            raise UsuarioNoAutorizadoException

        prospecto.rut_riesgo = rut_riesgo
        prospecto.nombre_riesgo = nombre_riesgo
        prospecto.telefono_contacto = telefono_contacto
        prospecto.correo_contacto = correo_contacto
        prospecto.direccion = direccion
        prospecto.region = region
        prospecto.comuna = comuna
        prospecto.observaciones = observaciones
        prospecto.tiene_locales_comerciales = tiene_locales_comerciales
        prospecto.uso_del_condominio = uso_del_condominio
        prospecto.numero_pisos = numero_pisos
        prospecto.numero_torres = numero_torres
        prospecto.cantidad_departamentos = cantidad_departamentos
        prospecto.cantidad_subterraneos = cantidad_subterraneos
        prospecto.tiene_piscina = tiene_piscina
        prospecto.year_construccion = year_construccion
        prospecto.metros_cuadrados = metros_cuadrados
        prospecto.materialidad = materialidad
        prospecto.clasificacion_preliminar_incendio = clasificacion_preliminar_incendio
        prospecto.procesos_productivos = procesos_productivos
        prospecto.ubicacion_piscina = ubicacion_piscina
        prospecto.tiene_alarma_incendio = tiene_alarma_incendio
        prospecto.tiene_sprinklers = tiene_sprinklers
        prospecto.uf_por_metro_cuadrado = uf_por_metro_cuadrado
        prospecto.porcentaje_depreciacion = porcentaje_depreciacion
        prospecto.porcentaje_espacios_comunes = porcentaje_espacios_comunes

        prospecto.linea_negocio = LineaNegocio(
            id=id_linea_negocio,
            nombre=''
        )

        self.repositorio_prospectos.actualizar_prospecto_condominio(prospecto)