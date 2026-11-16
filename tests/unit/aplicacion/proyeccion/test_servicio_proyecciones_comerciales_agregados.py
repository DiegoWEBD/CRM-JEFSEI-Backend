from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import (
    ServicioProyeccionesComerciales,
)

FUTURO = datetime.now(tz=timezone.utc) + timedelta(days=30)
PASADO = datetime.now(tz=timezone.utc) - timedelta(days=30)


def crear_proceso(
    id_proceso: int,
    probabilidad_ejecutivo: float | None = None,
    probabilidad_estado: float | None = None,
    fecha_estimada_cierre: datetime | None = None,
):
    return SimpleNamespace(
        id=id_proceso,
        probabilidad_cierre_ejecutivo=probabilidad_ejecutivo,
        estado_actual=SimpleNamespace(probabilidad_cierre=probabilidad_estado),
        fecha_estimada_cierre=fecha_estimada_cierre,
    )


def crear_cotizacion(prima_neta: float, vencida: bool = False):
    return SimpleNamespace(
        prima_neta=prima_neta,
        fecha_vencimiento=PASADO if vencida else FUTURO,
    )


class FakeRepositorioSolicitudes:

    def __init__(self, solicitudes_por_proceso: dict[int, list]):
        self.solicitudes_por_proceso = solicitudes_por_proceso

    def obtener_solicitudes(self, id_proceso: int):
        return self.solicitudes_por_proceso.get(id_proceso, [])


class FakeRepositorioCotizaciones:

    def __init__(self, cotizaciones_por_solicitud: dict[int, list]):
        self.cotizaciones_por_solicitud = cotizaciones_por_solicitud

    def obtener_por_solicitud(self, id_solicitud: int):
        return self.cotizaciones_por_solicitud.get(id_solicitud, [])


def crear_servicio(
    solicitudes_por_proceso: dict[int, list],
    cotizaciones_por_solicitud: dict[int, list],
) -> ServicioProyeccionesComerciales:
    return ServicioProyeccionesComerciales(
        repositorio_solicitudes_cotizacion=FakeRepositorioSolicitudes(
            solicitudes_por_proceso
        ),
        repositorio_cotizaciones=FakeRepositorioCotizaciones(
            cotizaciones_por_solicitud
        ),
    )


class TestPrimaCotizadaTotal:

    def test_solo_suma_cotizaciones_vigentes(self):
        servicio = crear_servicio(
            solicitudes_por_proceso={1: [SimpleNamespace(id=11)], 2: [SimpleNamespace(id=21)]},
            cotizaciones_por_solicitud={
                11: [crear_cotizacion(100), crear_cotizacion(50, vencida=True)],
                21: [crear_cotizacion(30)],
            },
        )

        total = servicio.prima_cotizada_total(
            [crear_proceso(1), crear_proceso(2)]
        )

        assert total == 130

    def test_sin_procesos_devuelve_cero(self):
        servicio = crear_servicio({}, {})

        assert servicio.prima_cotizada_total([]) == 0


class TestPrimaPotencialEstimadaTotal:

    def test_suma_el_promedio_de_cotizaciones_vigentes_por_oportunidad(self):
        servicio = crear_servicio(
            solicitudes_por_proceso={
                1: [SimpleNamespace(id=11)],
                2: [SimpleNamespace(id=21)],
                3: [SimpleNamespace(id=31)],
            },
            cotizaciones_por_solicitud={
                11: [crear_cotizacion(100), crear_cotizacion(200)],
                21: [crear_cotizacion(30)],
                31: [crear_cotizacion(40, vencida=True)],
            },
        )

        total = servicio.prima_potencial_estimada_total(
            [crear_proceso(1), crear_proceso(2), crear_proceso(3)]
        )

        # 150 (promedio de 100 y 200) + 30 + 0 (sin cotizaciones vigentes)
        assert total == 180


class TestPrimaEsperadaTotal:

    def test_usa_probabilidad_del_ejecutivo_o_del_estado_y_omite_sin_probabilidad(self):
        servicio = crear_servicio(
            solicitudes_por_proceso={
                1: [SimpleNamespace(id=11)],
                2: [SimpleNamespace(id=21)],
                3: [SimpleNamespace(id=31)],
            },
            cotizaciones_por_solicitud={
                11: [crear_cotizacion(100)],
                21: [crear_cotizacion(200)],
                31: [crear_cotizacion(40)],
            },
        )

        total = servicio.prima_esperada_total(
            [
                crear_proceso(1, probabilidad_ejecutivo=0.5),
                crear_proceso(2, probabilidad_ejecutivo=None, probabilidad_estado=0.25),
                crear_proceso(3, probabilidad_ejecutivo=None, probabilidad_estado=None),
            ]
        )

        # 100 * 0.5 + 200 * 0.25 + (sin probabilidad no aporta)
        assert total == 100


class TestProyeccionPrimaEsperadaPorMes:

    def test_agrupa_por_mes_de_cierre_estimado_ordenado_y_omite_sin_fecha_o_sin_esperada(self):
        servicio = crear_servicio(
            solicitudes_por_proceso={
                1: [SimpleNamespace(id=11)],
                2: [SimpleNamespace(id=21)],
                3: [SimpleNamespace(id=31)],
                4: [SimpleNamespace(id=41)],
                5: [SimpleNamespace(id=51)],
            },
            cotizaciones_por_solicitud={
                11: [crear_cotizacion(100)],
                21: [crear_cotizacion(300)],
                31: [crear_cotizacion(200)],
                41: [crear_cotizacion(400)],
                51: [crear_cotizacion(100)],
            },
        )

        proyeccion = servicio.proyeccion_prima_esperada_por_mes(
            [
                crear_proceso(
                    1,
                    probabilidad_ejecutivo=0.5,
                    fecha_estimada_cierre=datetime(2026, 3, 15, tzinfo=timezone.utc),
                ),
                crear_proceso(
                    2,
                    probabilidad_estado=0.1,
                    fecha_estimada_cierre=datetime(2026, 1, 10, tzinfo=timezone.utc),
                ),
                crear_proceso(
                    3,
                    probabilidad_ejecutivo=0.1,
                    fecha_estimada_cierre=datetime(2026, 3, 2, tzinfo=timezone.utc),
                ),
                # sin fecha estimada: no entra al gráfico
                crear_proceso(4, probabilidad_ejecutivo=1.0),
                # sin probabilidad: no tiene prima esperada
                crear_proceso(
                    5,
                    fecha_estimada_cierre=datetime(2026, 2, 1, tzinfo=timezone.utc),
                ),
            ]
        )

        assert proyeccion == [
            {'mes': '2026-01', 'prima_esperada': 30},
            {'mes': '2026-03', 'prima_esperada': 70},
        ]
