import pytest

from app.infraestructura.auditoria.resolucion_ip import resolver_ip_origen


@pytest.mark.unit
class TestResolucionIpOrigen:

    def test_usa_x_forwarded_for_desde_proxy_confiable(self):
        headers = {"x-forwarded-for": "200.10.20.30, 10.0.0.1"}

        ip = resolver_ip_origen(headers, "127.0.0.1")

        assert ip == "200.10.20.30"

    def test_usa_x_real_ip_desde_proxy_confiable(self):
        headers = {"x-real-ip": "200.10.20.30"}

        ip = resolver_ip_origen(headers, "127.0.0.1")

        assert ip == "200.10.20.30"

    def test_ignora_headers_si_peer_no_es_proxy_confiable(self):
        headers = {
            "x-forwarded-for": "200.10.20.30",
            "x-real-ip": "200.10.20.30",
        }

        ip = resolver_ip_origen(headers, "203.0.113.9")

        assert ip == "203.0.113.9"

    def test_si_no_hay_headers_devuelve_peer_directo(self):
        ip = resolver_ip_origen({}, "203.0.113.9")

        assert ip == "203.0.113.9"

    def test_sin_peer_ni_headers_devuelve_desconocida(self):
        ip = resolver_ip_origen({}, None)

        assert ip == "desconocida"

    def test_x_forwarded_for_vacio_no_rompe(self):
        headers = {"x-forwarded-for": "  "}

        ip = resolver_ip_origen(headers, "127.0.0.1")

        assert ip == "127.0.0.1"
