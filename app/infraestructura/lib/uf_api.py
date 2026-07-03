import json
from urllib.request import urlopen, Request
from urllib.error import URLError


def obtener_valor_uf() -> float:
    url = 'https://mindicador.cl/api/uf'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        serie = data.get('serie', [])
        if not serie:
            raise RuntimeError('La API de mindicador.cl retornó una serie vacía')

        return float(serie[0]['valor'])

    except URLError:
        raise RuntimeError('No se pudo conectar a mindicador.cl para obtener el valor UF')
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f'Error al parsear la respuesta de mindicador.cl: {exc}')
