def convertir_numero_a_formato_chileno(numero: int | float, decimales: int = 2) -> str:
    numero_formateado = (
        f"{numero:,.{decimales}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    partes = numero_formateado.split(',')

    if len(partes) != 2:
        return numero_formateado
    
    decimales = int(partes[1])
    entero = partes[0]

    if decimales == 0:
        return entero.strip()
    
    return numero_formateado.strip()