import csv
import io

from app.dominio.auditoria.registro_auditoria import RegistroAuditoria

COLUMNAS = [
    'id', 'fecha_registro', 'categoria', 'evento', 'resultado', 'estado_http',
    'rut_usuario', 'nombre_usuario', 'ip_origen', 'user_agent', 'id_peticion',
    'metodo', 'ruta', 'entidad_tipo', 'entidad_id', 'detalle', 'duracion_ms',
]


def generar_csv_registros_auditoria(registros: list[RegistroAuditoria]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNAS)

    for registro in registros:
        writer.writerow([
            registro.id,
            registro.fecha_registro.isoformat() if registro.fecha_registro else None,
            registro.categoria,
            registro.evento,
            registro.resultado,
            registro.estado_http,
            registro.rut_usuario,
            registro.nombre_usuario,
            registro.ip_origen,
            registro.user_agent,
            registro.id_peticion,
            registro.metodo,
            registro.ruta,
            registro.entidad_tipo,
            registro.entidad_id,
            registro.detalle,
            registro.duracion_ms,
        ])

    return buffer.getvalue()
