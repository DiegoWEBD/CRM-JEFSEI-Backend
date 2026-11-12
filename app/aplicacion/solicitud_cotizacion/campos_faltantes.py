"""Reglas de información faltante del prospecto base de una solicitud.

Se calculan sobre las columnas que la consulta del listado ya trae en la misma
fila, sin consultas adicionales. Son las mismas reglas que se validan para que
un prospecto pase a `informacion_completa`.
"""
from collections.abc import Mapping
from typing import Any

_CAMPOS_CONDOMINIO = (
    'porcentaje_espacios_comunes',
    'tiene_locales_comerciales',
    'uso_del_condominio',
    'materialidad',
    'clasificacion_preliminar_incendio',
    'procesos_productivos',
    'numero_pisos',
    'numero_torres',
    'cantidad_departamentos',
    'cantidad_subterraneos',
)


def calcular_campos_faltantes(fila: Mapping[str, Any]) -> list[str]:
    es_condominio = str(fila.get('linea_negocio') or '').lower() == 'condominio'

    campos_faltantes: list[str] = []

    if es_condominio:
        if fila.get('administrador') is None:
            campos_faltantes.append('administrador')

            if fila.get('telefono_contacto') is None:
                campos_faltantes.append('telefono_contacto')
            if fila.get('correo_contacto') is None:
                campos_faltantes.append('correo_contacto')

        for campo in _CAMPOS_CONDOMINIO:
            if fila.get(campo) is None:
                campos_faltantes.append(campo)

        if fila.get('tiene_piscina') is None:
            campos_faltantes.append('tiene_piscina')
        elif fila.get('tiene_piscina') is True and fila.get('ubicacion_piscina') is None:
            campos_faltantes.append('ubicacion_piscina')

        if fila.get('tiene_alarma_incendio') is None:
            campos_faltantes.append('tiene_alarma_incendio')
        if fila.get('tiene_sprinklers') is None:
            campos_faltantes.append('tiene_sprinklers')
        if fila.get('year_construccion') is None:
            campos_faltantes.append('year_construccion')
        if fila.get('metros_cuadrados') is None:
            campos_faltantes.append('metros_cuadrados')
        if fila.get('condominio_vertical') is None:
            campos_faltantes.append('condominio_vertical')

    # Campos base del prospecto (llenables por formulario)
    if fila.get('rut_riesgo') is None:
        campos_faltantes.append('rut_riesgo')
    if not es_condominio and fila.get('telefono_contacto') is None:
        campos_faltantes.append('telefono_contacto')
    if not es_condominio and fila.get('correo_contacto') is None:
        campos_faltantes.append('correo_contacto')
    if fila.get('direccion') is None:
        campos_faltantes.append('direccion')
    if fila.get('region') is None:
        campos_faltantes.append('region')
    if fila.get('comuna') is None:
        campos_faltantes.append('comuna')

    return campos_faltantes
