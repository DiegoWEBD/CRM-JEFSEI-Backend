from fastapi import APIRouter

from app.infraestructura.db.conexion import obtener_conexion

router = APIRouter(prefix="/etapas-proceso-comercial", tags=["EtapasProcesoComercial"])


@router.get("/", status_code=200)
def obtener_etapas():
    with obtener_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT codigo, nombre
                FROM EtapaProcesoComercial
                ORDER BY codigo
            """)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
