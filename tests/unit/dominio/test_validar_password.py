import pytest

from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.usuario.validar_password import validar_fortaleza_password


@pytest.mark.unit
class TestValidarFortalezaPassword:

    def test_password_conforme_es_aceptada(self):
        validar_fortaleza_password('ClaveSegura123')

    def test_password_conforme_con_simbolos_es_aceptada(self):
        validar_fortaleza_password('Clave-Segura.2026')

    def test_rechaza_password_muy_corta(self):
        with pytest.raises(DatoInvalidoException, match='al menos 12 caracteres'):
            validar_fortaleza_password('Corta1a')

    def test_rechaza_password_de_exactamente_11_caracteres(self):
        with pytest.raises(DatoInvalidoException, match='al menos 12 caracteres'):
            validar_fortaleza_password('ClaveSegur1')

    def test_rechaza_password_que_excede_72_bytes(self):
        with pytest.raises(DatoInvalidoException, match='72 caracteres'):
            validar_fortaleza_password('Aa1' + 'x' * 70)

    def test_cuenta_bytes_y_no_caracteres(self):
        # 24 letras 'ñ' = 48 bytes... con relleno supera 72 bytes aunque sean ~30 caracteres
        with pytest.raises(DatoInvalidoException, match='72 caracteres'):
            validar_fortaleza_password('Ñ' * 30 + 'ñ' * 6 + 'aA1')

    def test_rechaza_sin_mayuscula(self):
        with pytest.raises(DatoInvalidoException, match='mayúscula'):
            validar_fortaleza_password('clavesegura123')

    def test_rechaza_sin_minuscula(self):
        with pytest.raises(DatoInvalidoException, match='minúscula'):
            validar_fortaleza_password('CLAVESEGURA123')

    def test_rechaza_sin_digito(self):
        with pytest.raises(DatoInvalidoException, match='dígito'):
            validar_fortaleza_password('ClaveSeguraLarga')

    def test_rechaza_password_comun_con_mayuscula_inicial(self):
        with pytest.raises(DatoInvalidoException, match='demasiado común'):
            validar_fortaleza_password('Password1234')

    def test_rechaza_password_comun_indistintamente_de_mayusculas(self):
        with pytest.raises(DatoInvalidoException, match='demasiado común'):
            validar_fortaleza_password('Welcome12345')

    def test_rechaza_password_vacia(self):
        with pytest.raises(DatoInvalidoException, match='al menos 12 caracteres'):
            validar_fortaleza_password('')
