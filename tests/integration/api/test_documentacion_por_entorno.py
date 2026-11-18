from starlette.testclient import TestClient

from app.core.config import Settings
from app.main import _crear_app


def _config_de_pruebas(entorno: str) -> Settings:
    return Settings(
        _env_file=None,
        ACCESS_TOKEN_SECRET_KEY='clave-de-pruebas-solo-local-nunca-produccion',
        CRM_ENTORNO=entorno,
    )


class TestDocumentacionPorEntorno:

    def test_produccion_oculta_la_documentacion_interactiva(self):
        app = _crear_app(_config_de_pruebas('produccion'))

        with TestClient(app) as c:
            assert c.get('/openapi.json').status_code == 404
            assert c.get('/docs').status_code == 404
            assert c.get('/redoc').status_code == 404

    def test_desarrollo_expone_la_documentacion_interactiva(self):
        app = _crear_app(_config_de_pruebas('desarrollo'))

        with TestClient(app) as c:
            assert c.get('/openapi.json').status_code == 200
            assert c.get('/docs').status_code == 200
