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
        falta_correo = False
    else:
        falta_telefono = prospecto.telefono_contacto is None
        falta_correo = prospecto.correo_contacto is None

    if prospecto.tiene_piscina is False:
        falta_ubicacion_piscina = False
    else:
        falta_ubicacion_piscina = prospecto.ubicacion_piscina is None

    validaciones = {
        "rut_riesgo": prospecto.rut_riesgo is not None,
        "nombre_riesgo": prospecto.nombre_riesgo is not None,
        "telefono_contacto": not falta_telefono,
        "correo_contacto": not falta_correo,
        "direccion": prospecto.direccion is not None,
        "region": prospecto.region is not None,
        "comuna": prospecto.comuna is not None,
        "linea_negocio": prospecto.linea_negocio is not None,
        "tiene_locales_comerciales": prospecto.tiene_locales_comerciales is not None,
        "uso_del_condominio": prospecto.uso_del_condominio is not None,
        "materialidad": prospecto.materialidad is not None,
        "clasificacion_preliminar_incendio": prospecto.clasificacion_preliminar_incendio is not None,
        "procesos_productivos": prospecto.procesos_productivos is not None,
        "numero_pisos": prospecto.numero_pisos is not None,
        "numero_torres": prospecto.numero_torres is not None,
        "cantidad_departamentos": prospecto.cantidad_departamentos is not None,
        "cantidad_subterraneos": prospecto.cantidad_subterraneos is not None,
        "tiene_piscina": prospecto.tiene_piscina is not None,
        "ubicacion_piscina": not falta_ubicacion_piscina,
        "tiene_alarma_incendio": prospecto.tiene_alarma_incendio is not None,
        "tiene_sprinklers": prospecto.tiene_sprinklers is not None,
        "year_construccion": prospecto.year_construccion is not None,
        "metros_cuadrados": prospecto.metros_cuadrados is not None,
        "uf_por_metro_cuadrado": prospecto.uf_por_metro_cuadrado is not None,
        "porcentaje_depreciacion": prospecto.porcentaje_depreciacion is not None,
        "porcentaje_espacios_comunes": prospecto.porcentaje_espacios_comunes is not None,
        "planificacion": datos_completos_planificacion,
    }

    print("=== Validaciones ===")
    for nombre, resultado in validaciones.items():
        print(f"{nombre:40}: {'✅' if resultado else '❌'}")

    return all(validaciones.values())