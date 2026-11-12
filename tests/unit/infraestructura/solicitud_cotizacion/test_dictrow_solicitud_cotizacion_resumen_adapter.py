import pytest

from app.infraestructura.solicitud_cotizacion.adaptadores.dictrow_solicitud_cotizacion_resumen_adapter import (
    DictRowSolicitudCotizacionResumenAdapter,
)


def _fila() -> dict:
    return {
        'id': 1,
        'id_prospecto': 10,
        'nombre_riesgo': 'Condominio Las Torres',
        'informacion_completa': False,
        'ejecutivo_comercial': 'Ana Pérez',
        'tipo': 'incendio',
        'recotizacion': False,
        'motivo_recotizacion': None,
        'producto': 'Incendio Condominio',
        'prioridad': 'alta',
        'fecha': '2026-11-10T10:00:00',
        'estudio_disponible': False,
        'tiene_cotizaciones': True,
        # Columnas del prospecto base para campos_faltantes
        'linea_negocio': 'Incendio',
        'rut_riesgo': '76.123.456-7',
        'telefono_contacto': '+56912345678',
        'correo_contacto': 'contacto@correo.cl',
        'direccion': 'Av. Uno 123',
        'region': 'Metropolitana',
        'comuna': 'Santiago',
    }


@pytest.mark.unit
class TestDictRowSolicitudCotizacionResumenAdapter:

    def test_mapea_los_campos_del_resumen(self):
        resumen = DictRowSolicitudCotizacionResumenAdapter(_fila()).to_solicitud_cotizacion_resumen()

        assert resumen.id == 1
        assert resumen.id_prospecto == 10
        assert resumen.nombre_riesgo == 'Condominio Las Torres'
        assert resumen.informacion_completa is False
        assert resumen.ejecutivo_comercial == 'Ana Pérez'
        assert resumen.tipo == 'incendio'
        assert resumen.producto == 'Incendio Condominio'
        assert resumen.prioridad == 'alta'
        assert resumen.fecha == '2026-11-10T10:00:00'

    def test_mapea_los_booleanos_de_exists(self):
        fila = {**_fila(), 'tiene_cotizaciones': False, 'estudio_disponible': True}

        resumen = DictRowSolicitudCotizacionResumenAdapter(fila).to_solicitud_cotizacion_resumen()

        assert resumen.tiene_cotizaciones is False
        assert resumen.estudio_disponible is True

    def test_calcula_campos_faltantes_desde_la_fila(self):
        fila = {**_fila(), 'telefono_contacto': None, 'direccion': None}

        resumen = DictRowSolicitudCotizacionResumenAdapter(fila).to_solicitud_cotizacion_resumen()

        assert resumen.campos_faltantes == ['telefono_contacto', 'direccion']

    def test_calcula_campos_faltantes_condominio(self):
        fila = {
            **_fila(),
            'linea_negocio': 'Condominio',
            'administrador': None,
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
            'tiene_piscina': True,
            'ubicacion_piscina': None,
            'tiene_alarma_incendio': False,
            'tiene_sprinklers': False,
            'year_construccion': 2005,
            'metros_cuadrados': 1200,
            'condominio_vertical': True,
            'telefono_contacto': None,
        }

        resumen = DictRowSolicitudCotizacionResumenAdapter(fila).to_solicitud_cotizacion_resumen()

        assert resumen.campos_faltantes == [
            'administrador',
            'telefono_contacto',
            'ubicacion_piscina',
        ]

    def test_sin_faltantes_devuelve_lista_vacia(self):
        resumen = DictRowSolicitudCotizacionResumenAdapter(_fila()).to_solicitud_cotizacion_resumen()

        assert resumen.campos_faltantes == []
