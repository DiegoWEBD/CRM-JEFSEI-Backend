from app.dominio.comuna.comuna import Comuna
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class RegistrarProspectoUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(
        self,
        rut_usuario: str,
        rut_riesgo: str | None,
        nombre_riesgo: str, 
        nombre_contacto: str,
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        id_comuna: int, 
        observaciones: str | None, 
        id_linea_negocio: int,
        cargo_contacto: str | None, 
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
    ) -> int:

        linea_negocio = LineaNegocio(
            id=id_linea_negocio,
            nombre=''
        )

        registrado_por = self.repositorio_usuarios.buscar(rut_usuario)

        if not registrado_por:
            raise ValueError(f'Usuario {rut_usuario} no encontrado')

        comuna = Comuna(id=id_comuna, nombre='')

        prospecto = ProspectoCondominio(
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            nombre_contacto=nombre_contacto,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            companies_sugeridas=[],
            cargo_contacto=cargo_contacto,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            desea_ser_contactado=desea_ser_contactado,
            historial_estados=[],
            ejecutivo_comercial_asignado=None,
            ejecutivo_evaluacion_asignado=None
        )
        
        return self.repositorio_prospectos.registrar_prospecto_condominio(prospecto)