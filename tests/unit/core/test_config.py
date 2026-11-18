import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_sin_secreto_jwt_la_aplicacion_no_arranca(monkeypatch):
    """Fail-fast: sin ACCESS_TOKEN_SECRET_KEY no debe construirse Settings."""
    monkeypatch.delenv('ACCESS_TOKEN_SECRET_KEY', raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_secreto_jwt_vacio_es_invalido(monkeypatch):
    monkeypatch.setenv('ACCESS_TOKEN_SECRET_KEY', '   ')

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_rechaza_el_valor_de_prueba_conocido(monkeypatch):
    """El antiguo default 'test-secret-key-for-ci' es público y no debe aceptarse."""
    monkeypatch.setenv('ACCESS_TOKEN_SECRET_KEY', 'test-secret-key-for-ci')

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_secreto_jwt_explicito_es_aceptado(monkeypatch):
    monkeypatch.setenv('ACCESS_TOKEN_SECRET_KEY', 'un-secreto-fuerte-y-explícito-123')

    settings = Settings(_env_file=None)

    assert settings.ACCESS_TOKEN_SECRET_KEY == 'un-secreto-fuerte-y-explícito-123'


def test_entorno_invalido_es_rechazado(monkeypatch):
    monkeypatch.setenv('CRM_ENTORNO', 'staging')

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_documentacion_habilitada_segun_entorno(monkeypatch):
    monkeypatch.setenv('CRM_ENTORNO', 'produccion')
    assert Settings(_env_file=None).documentacion_habilitada is False

    monkeypatch.setenv('CRM_ENTORNO', 'desarrollo')
    assert Settings(_env_file=None).documentacion_habilitada is True
