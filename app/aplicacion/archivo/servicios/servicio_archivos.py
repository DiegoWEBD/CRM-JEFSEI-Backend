import os


class ServicioArchivos:
    """Servicio de aplicación para escribir, verificar y eliminar archivos en disco."""

    def guardar(self, directorio: str, nombre_archivo: str, contenido: bytes) -> str:
        """Escribe el archivo en disco y retorna la ruta completa."""
        ruta = os.path.join(directorio, nombre_archivo)
        os.makedirs(directorio, exist_ok=True)
        with open(ruta, 'wb') as f:
            f.write(contenido)
        return ruta

    def existe(self, directorio: str, nombre_archivo: str | None) -> bool:
        """Indica si el archivo existe en disco."""
        if not nombre_archivo:
            return False
        return os.path.exists(os.path.join(directorio, nombre_archivo))

    def eliminar(self, directorio: str, nombre_archivo: str | None) -> None:
        """Elimina el archivo si existe. Silencioso si no existe o es None."""
        if not nombre_archivo:
            return
        
        if self.existe(directorio, nombre_archivo):
            os.remove(os.path.join(directorio, nombre_archivo))