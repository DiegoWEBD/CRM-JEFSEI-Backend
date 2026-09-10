from fastapi import UploadFile
from datetime import datetime, timezone
import os

from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.dominio.usuario.usuario import Usuario


class SubirEstudioComercialUseCase:
    def __init__(self, repositorio_estudios: RepositorioEstudiosComerciales):
        self.repositorio_estudios = repositorio_estudios

    def ejecutar(self, archivo: UploadFile, id_solicitud: int,usuario: Usuario) -> tuple[int, str]:
        
        timestamp_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        nombre_unico = f'estudio_comercial_{id_solicitud}_{timestamp_ms}.pdf'
        ruta = f'documentos/estudios_finales/{nombre_unico}'
    
        os.makedirs('documentos/estudios_finales', exist_ok=True)
    
        with open(ruta, 'wb') as f:
            f.write(archivo.file.read())
    
        id_estudio = self.repositorio_estudios.insertar(id_solicitud=id_solicitud, nombre_archivo=nombre_unico, rut_usuario=usuario.rut)

        return id_estudio, nombre_unico