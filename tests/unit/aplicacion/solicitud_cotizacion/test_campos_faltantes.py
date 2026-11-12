import pytest

from app.aplicacion.solicitud_cotizacion.campos_faltantes import (
    calcular_campos_faltantes,
)


def _fila_completa_no_condominio() -> dict:
    return {
        'linea_negocio': 'Incendio',
        'rut_riesgo': '76.123.456-7',
        'telefono_contacto': '+56912345678',
        'correo_contacto': 'contacto@correo.cl',
        'direccion': 'Av. Uno 123',
        'region': 'Metropolitana',
        'comuna': 'Santiago',
    }


def _fila_completa_condominio() -> dict:
    return {
        **_fila_completa_no_condominio(),
        'linea_negocio': 'Condominio',
        'administrador': 3,
        'porcentaje_espacios_comunes': 0.3,
        'tiene_locales_comerciales': False,
        'uso_del_condominio': 'residencial',
        'materialidad': 'hormigon',
        'clasificacion_preliminar_incendio': 'B',
        'procesos_productivos': False,
        'numero_pisos': 3,
        'numero_torres': 1,
        'cantidad_departamentos': 20,
        'cantidad_subterraneos': 1,
        'tiene_piscina': False,
        'ubicacion_piscina': None,
        'tiene_alarma_incendio': False,
        'tiene_sprinklers': False,
        'year_construccion': 2005,
        'metros_cuadrados': 1200,
        'condominio_vertical': True,
    }


@pytest.mark.unit
class TestCalcularCamposFaltantes:

    def test_no_condominio_completo_no_tiene_faltantes(self):
        assert calcular_campos_faltantes(_fila_completa_no_condominio()) == []

    def test_no_condominio_lista_solo_los_campos_nulos(self):
        fila = {
            **_fila_completa_no_condominio(),
            'telefono_contacto': None,
            'direccion': None,
        }

        assert calcular_campos_faltantes(fila) == ['telefono_contacto', 'direccion']

    def test_no_condominio_orden_de_los_campos_base(self):
        fila = {
            'linea_negocio': 'Incendio',
            'rut_riesgo': None,
            'telefono_contacto': None,
            'correo_contacto': None,
            'direccion': None,
            'region': None,
            'comuna': None,
        }

        assert calcular_campos_faltantes(fila) == [
            'rut_riesgo',
            'telefono_contacto',
            'correo_contacto',
            'direccion',
            'region',
            'comuna',
        ]

    def test_condominio_completo_no_tiene_faltantes(self):
        assert calcular_campos_faltantes(_fila_completa_condominio()) == []

    def test_condominio_sin_administrador_marca_telefono_y_correo(self):
        fila = {
            **_fila_completa_condominio(),
            'administrador': None,
            'telefono_contacto': None,
            'correo_contacto': None,
        }

        assert calcular_campos_faltantes(fila) == [
            'administrador',
            'telefono_contacto',
            'correo_contacto',
        ]

    def test_condominio_con_administrador_no_marca_telefono_ni_correo(self):
        fila = {
            **_fila_completa_condominio(),
            'telefono_contacto': None,
            'correo_contacto': None,
        }

        assert calcular_campos_faltantes(fila) == []

    def test_condominio_marca_rut_direccion_region_comuna_si_son_nulos(self):
        fila = {
            **_fila_completa_condominio(),
            'rut_riesgo': None,
            'direccion': None,
        }

        assert calcular_campos_faltantes(fila) == ['rut_riesgo', 'direccion']

    def test_piscina_nula_marca_tiene_piscina(self):
        fila = {
            **_fila_completa_condominio(),
            'tiene_piscina': None,
            'ubicacion_piscina': None,
        }

        assert calcular_campos_faltantes(fila) == ['tiene_piscina']

    def test_piscina_sin_ubicacion_marca_ubicacion_piscina(self):
        fila = {
            **_fila_completa_condominio(),
            'tiene_piscina': True,
            'ubicacion_piscina': None,
        }

        assert calcular_campos_faltantes(fila) == ['ubicacion_piscina']

    def test_sin_piscina_no_exige_ubicacion(self):
        fila = {
            **_fila_completa_condominio(),
            'tiene_piscina': False,
            'ubicacion_piscina': None,
        }

        assert calcular_campos_faltantes(fila) == []

    def test_condominio_bloque_completo_nulo_lista_todo_el_bloque(self):
        fila = {
            **_fila_completa_condominio(),
            'administrador': None,
            'porcentaje_espacios_comunes': None,
            'tiene_locales_comerciales': None,
            'uso_del_condominio': None,
            'materialidad': None,
            'clasificacion_preliminar_incendio': None,
            'procesos_productivos': None,
            'numero_pisos': None,
            'numero_torres': None,
            'cantidad_departamentos': None,
            'cantidad_subterraneos': None,
            'tiene_piscina': None,
            'ubicacion_piscina': None,
            'tiene_alarma_incendio': None,
            'tiene_sprinklers': None,
            'year_construccion': None,
            'metros_cuadrados': None,
            'condominio_vertical': None,
        }

        assert calcular_campos_faltantes(fila) == [
            'administrador',
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
            'tiene_piscina',
            'tiene_alarma_incendio',
            'tiene_sprinklers',
            'year_construccion',
            'metros_cuadrados',
            'condominio_vertical',
        ]

    def test_linea_condominio_distingue_mayusculas(self):
        fila = {
            **_fila_completa_condominio(),
            'linea_negocio': 'CONDOMINIO',
        }

        assert calcular_campos_faltantes(fila) == []
