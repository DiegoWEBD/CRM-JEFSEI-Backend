import requests

def obtener_valor_uf() -> float:
    try:
        response = requests.get(
            'https://mindicador.cl/api/uf',
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()

        serie = data.get('serie')
        if not serie:
            raise RuntimeError('La API de mindicador.cl retornó una serie vacía')

        return float(serie[0]['valor'])

    except requests.RequestException as exc:
        raise RuntimeError(
            'No se pudo obtener el valor de la UF desde mindicador.cl'
        ) from exc
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(
            f'Error al procesar la respuesta de mindicador.cl: {exc}'
        ) from exc