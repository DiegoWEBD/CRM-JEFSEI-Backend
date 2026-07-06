from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio


def informacion_completa_prospecto(prospecto: Prospecto) -> bool:
    return all([
        prospecto.rut_riesgo is not None,
        prospecto.nombre_riesgo is not None,
        prospecto.telefono_contacto is not None,
        prospecto.correo_contacto is not None,
        prospecto.direccion is not None,
        prospecto.region is not None,
        prospecto.comuna is not None
    ])


def informacion_completa_prospecto_condominio(prospecto: ProspectoCondominio) -> bool:
    datos_completos_planificacion = True

    if prospecto.planificacion_prospecto:
        datos_completos_planificacion = all([
            prospecto.planificacion_prospecto.prima_vigente is not None,
            prospecto.planificacion_prospecto.company_poliza is not None,
            prospecto.planificacion_prospecto.monto_asegurado_vigente is not None
        ])

    if prospecto.administrador:
        falta_telefono = False
    else:
        falta_telefono = prospecto.telefono_contacto is None
    
    if prospecto.tiene_piscina is False:
        falta_ubicacion_piscina = False
    else:
        falta_ubicacion_piscina = prospecto.ubicacion_piscina is None

    return all([
        prospecto.rut_riesgo is not None,
        prospecto.nombre_riesgo is not None,
        not falta_telefono,
        prospecto.correo_contacto is not None,
        prospecto.direccion is not None,
        prospecto.region is not None,
        prospecto.comuna is not None,
        prospecto.linea_negocio is not None,
        prospecto.tiene_locales_comerciales is not None,
        prospecto.uso_del_condominio is not None,
        prospecto.materialidad is not None,
        prospecto.clasificacion_preliminar_incendio is not None,
        prospecto.procesos_productivos is not None,
        prospecto.numero_pisos is not None,
        prospecto.numero_torres is not None,
        prospecto.cantidad_departamentos is not None,
        prospecto.cantidad_subterraneos is not None,
        prospecto.tiene_piscina is not None,
        not falta_ubicacion_piscina,
        prospecto.tiene_alarma_incendio is not None,
        prospecto.tiene_sprinklers is not None,
        prospecto.year_construccion is not None,
        prospecto.metros_cuadrados is not None,
        prospecto.uf_por_metro_cuadrado is not None,
        prospecto.porcentaje_depreciacion is not None,
        prospecto.porcentaje_espacios_comunes is not None,
        datos_completos_planificacion
    ])