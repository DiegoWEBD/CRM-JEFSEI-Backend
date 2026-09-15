import re

def normalizar_rut(v: str | None) -> str | None:
    if v is None:
        return None
    
    clean = re.sub(r'[^0-9kK]', '', v).upper()
    if len(clean) <= 1:
        return clean
    return f"{clean[:-1]}-{clean[-1]}"