import re
import unicodedata

from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException


class ServicioGirosComerciales:
    """Reglas de negocio de los giros comerciales de un prospecto empresa.

    La unicidad de los nombres se valida en la capa de aplicación
    ignorando mayúsculas y tildes; el UNIQUE(id_prospecto_empresa, nombre)
    de la base de datos solo respalda la unicidad exacta.
    """

    @staticmethod
    def clave_normalizada(nombre: str) -> str:
        texto = unicodedata.normalize('NFD', nombre)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto.lower()

    @classmethod
    def es_el_mismo_giro(cls, nombre_a: str, nombre_b: str) -> bool:
        return cls.clave_normalizada(nombre_a) == cls.clave_normalizada(nombre_b)

    @classmethod
    def validar_nombres(cls, nombres: list[str]) -> None:
        """Rechaza nombres vacíos o repetidos dentro de una misma operación."""
        vistas: set[str] = set()

        for nombre in nombres:
            clave = cls.clave_normalizada(nombre)

            if not clave:
                raise ConflictoEnAccionException('El nombre del giro comercial es obligatorio')

            if clave in vistas:
                raise RecursoYaExisteException(f'El giro comercial {nombre} está repetido en la solicitud')

            vistas.add(clave)
