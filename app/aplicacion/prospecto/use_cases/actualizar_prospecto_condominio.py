from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
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
        nombre_contacto: str,
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        region: str,
        comuna: str, 
        cargo_contacto: str | None,
        observaciones: str | None, 
        id_linea_negocio: int,  
        uf_por_metro_cuadrado: float | None,
        porcentaje_depreciacion: float | None,
        porcentaje_espacios_comunes: float | None,
        tiene_locales_comerciales: bool | None,
        uso_del_condominio: str | None,
        numero_pisos: int | None,
        numero_torres: int | None,
        cantidad_departamentos: int | None,
        cantidad_subterraneos: int | None,
        tiene_piscina: bool | None,
        year_construccion: int | None,
        metros_cuadrados: float | None,
        desea_ser_contactado: bool | None
    ):
        
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id)

        if prospecto is None:
            raise ValueError('Prospecto no encontrado')
        
        if prospecto.proceso_comercial.ejecutivo_comercial is None or prospecto.proceso_comercial.ejecutivo_comercial.rut != rut_usuario:
            raise UsuarioNoAutorizadoException('Usuario no autorizado')

        prospecto.rut_riesgo = rut_riesgo
        prospecto.nombre_riesgo = nombre_riesgo
        prospecto.nombre_contacto = nombre_contacto
        prospecto.telefono_contacto = telefono_contacto
        prospecto.correo_contacto = correo_contacto
        prospecto.direccion = direccion
        prospecto.region = region
        prospecto.comuna = comuna
        prospecto.observaciones = observaciones
        prospecto.cargo_contacto = cargo_contacto
        prospecto.tiene_locales_comerciales = tiene_locales_comerciales
        prospecto.uso_del_condominio = uso_del_condominio
        prospecto.numero_pisos = numero_pisos
        prospecto.numero_torres = numero_torres
        prospecto.cantidad_departamentos = cantidad_departamentos
        prospecto.cantidad_subterraneos = cantidad_subterraneos
        prospecto.tiene_piscina = tiene_piscina
        prospecto.year_construccion = year_construccion
        prospecto.metros_cuadrados = metros_cuadrados
        prospecto.desea_ser_contactado = desea_ser_contactado

        if prospecto.evaluacion_riesgo is None:
            prospecto.evaluacion_riesgo = EvaluacionRiesgo(
                uf_por_metro_cuadrado=uf_por_metro_cuadrado,
                porcentaje_depreciacion=porcentaje_depreciacion,
                porcentaje_espacios_comunes=porcentaje_espacios_comunes
            )
        else:
            prospecto.evaluacion_riesgo.uf_por_metro_cuadrado = uf_por_metro_cuadrado
            prospecto.evaluacion_riesgo.porcentaje_depreciacion = porcentaje_depreciacion
            prospecto.evaluacion_riesgo.porcentaje_espacios_comunes = porcentaje_espacios_comunes

        prospecto.linea_negocio = LineaNegocio(
            id=id_linea_negocio,
            nombre=''
        )

        self.repositorio_prospectos.actualizar_prospecto_condominio(prospecto)