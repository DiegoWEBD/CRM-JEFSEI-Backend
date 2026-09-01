import math

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.producto.use_cases.actualizar_producto import ActualizarProductoUseCase
from app.aplicacion.producto.use_cases.crear_producto import CrearProductoUseCase
from app.aplicacion.producto.use_cases.eliminar_producto import EliminarProductoUseCase
from app.aplicacion.producto.use_cases.obtener_producto import ObtenerProductoUseCase
from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase
from app.infraestructura.producto.adaptadores.producto_json_adapter import ProductoJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.producto.deps import (
    get_actualizar_producto_use_case,
    get_crear_producto_use_case,
    get_eliminar_producto_use_case,
    get_obtener_producto_use_case,
    get_obtener_productos_use_case,
)
from app.presentacion.api.producto.dto.actualizar_producto_request import ActualizarProductoRequest
from app.presentacion.api.producto.dto.crear_producto_request import CrearProductoRequest

router = APIRouter(prefix='/productos', tags=['Productos'])


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_productos(
    id_linea_negocio: int | None = Query(default=None),
    texto_busqueda: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    tamano_pagina: int = Query(default=20, ge=1, le=100),
    use_case: ObtenerProductosUseCase = Depends(get_obtener_productos_use_case)
):
    productos, total = use_case.ejecutar(
        id_linea_negocio=id_linea_negocio,
        texto_busqueda=texto_busqueda,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
    )

    total_paginas = math.ceil(total / tamano_pagina) if total > 0 else 1

    return {
        'total': total,
        'pagina': pagina,
        'total_paginas': total_paginas,
        'data': [ProductoJsonAdapter.to_json(p) for p in productos],
    }


@router.get('/{id}', status_code=status.HTTP_200_OK)
def obtener_producto(
    id: int,
    use_case: ObtenerProductoUseCase = Depends(get_obtener_producto_use_case)
):
    producto = use_case.ejecutar(id)

    return {
        'data': ProductoJsonAdapter.to_json(producto)
    }


@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_producto(
    request: CrearProductoRequest,
    _ = Depends(permisos_requeridos('ADMINISTRAR_PRODUCTOS')),
    use_case: CrearProductoUseCase = Depends(get_crear_producto_use_case)
):
    registrado = use_case.ejecutar(
        nombre=request.nombre,
        id_linea_negocio=request.id_linea_negocio,
        codigo=request.codigo,
    )

    if not registrado:
        raise HTTPException(
            status_code=400,
            detail='Error al registrar el producto'
        )

    return {
        'message': 'Producto registrado correctamente'
    }


@router.put('/{id}', status_code=status.HTTP_200_OK)
def actualizar_producto(
    id: int,
    request: ActualizarProductoRequest,
    _ = Depends(permisos_requeridos('ADMINISTRAR_PRODUCTOS')),
    use_case: ActualizarProductoUseCase = Depends(get_actualizar_producto_use_case)
):
    actualizado = use_case.ejecutar(
        id=id,
        nombre=request.nombre,
        id_linea_negocio=request.id_linea_negocio,
        codigo=request.codigo,
    )

    if not actualizado:
        raise HTTPException(
            status_code=400,
            detail='Error al actualizar el producto'
        )

    return {
        'message': 'Producto actualizado correctamente'
    }


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def eliminar_producto(
    id: int,
    _ = Depends(permisos_requeridos('ADMINISTRAR_PRODUCTOS')),
    use_case: EliminarProductoUseCase = Depends(get_eliminar_producto_use_case)
):
    use_case.ejecutar(id)

    return {
        'message': 'Producto eliminado correctamente'
    }
