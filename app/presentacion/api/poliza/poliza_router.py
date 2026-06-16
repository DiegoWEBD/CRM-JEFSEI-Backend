from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.poliza.dependencias.deps import get_obtener_polizas_use_case


router = APIRouter(prefix='/polizas', tags=['Polizas'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_polizas(
    id_cliente: int = Query(),
    usuario: Usuario = Depends(permisos_requeridos('OBTENER_POLIZAS_TODAS', 'OBTENER_POLIZAS_PROPIAS')),
    use_case: ObtenerPolizasUseCase = Depends(get_obtener_polizas_use_case)
):
    try:
        rut_usuario = usuario.rut

        for rol in usuario.roles:
            for permiso in rol.permisos:
                if permiso.codigo == 'OBTENER_POLIZAS_TODAS':
                    rut_usuario = None

        polizas = use_case.ejecutar(id_cliente, rut_usuario)

        return {
            'polizas': polizas
        }

    except HTTPException:
        raise

    except UsuarioNoAutorizadoException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        )

    except RecursoNoEncontradoException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )