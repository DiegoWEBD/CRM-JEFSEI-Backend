import asyncio

import pytest

from app.core.hub_notificaciones import HubNotificaciones

RUT = '11111111-1'


@pytest.mark.unit
class TestHubNotificaciones:

    def test_publicar_desde_hilo_entrega_a_los_suscriptores(self):
        async def escenario():
            hub_local = HubNotificaciones()
            hub_local.capturar_loop(asyncio.get_running_loop())

            cola = hub_local.suscribir(RUT)
            assert hub_local.conexiones_de(RUT) == 1

            hub_local.publicar_desde_hilo([RUT], {'evento': 'notificaciones_actualizadas'})
            await asyncio.sleep(0.01)

            assert cola.qsize() == 1
            assert cola.get_nowait() == {'evento': 'notificaciones_actualizadas'}

        asyncio.run(escenario())

    def test_publicar_a_rut_sin_conexion_no_falla(self):
        async def escenario():
            hub_local = HubNotificaciones()
            hub_local.capturar_loop(asyncio.get_running_loop())

            hub_local.publicar_desde_hilo(['99999999-9'], {'evento': 'ping'})
            await asyncio.sleep(0.01)

            assert hub_local.total_conexiones == 0

        asyncio.run(escenario())

    def test_publicar_sin_ruts_no_falla(self):
        hub_local = HubNotificaciones()
        hub_local.publicar_desde_hilo([], {'evento': 'ping'})
        hub_local.publicar_desde_hilo([''], {'evento': 'ping'})

        assert hub_local.total_conexiones == 0

    def test_publicar_sin_loop_capturado_no_falla(self):
        hub_local = HubNotificaciones()

        # Aún sin lifespan: simplemente no hay dónde entregar el evento.
        hub_local.publicar_desde_hilo([RUT], {'evento': 'ping'})

        assert hub_local.loop is None

    def test_desuscribir_libera_la_ultima_conexion(self):
        async def escenario():
            hub_local = HubNotificaciones()
            hub_local.capturar_loop(asyncio.get_running_loop())

            cola = hub_local.suscribir(RUT)
            hub_local.desuscribir(RUT, cola)

            assert hub_local.conexiones_de(RUT) == 0
            assert hub_local.total_conexiones == 0

        asyncio.run(escenario())
