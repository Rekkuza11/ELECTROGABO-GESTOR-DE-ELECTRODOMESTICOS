"""
LEGACY / DESCONECTADO — models/inventario.py
Fase 6 · Corrección #16.

Esta clase gestiona el inventario EN MEMORIA mediante un Singleton.
El flujo real del sistema usa ProductoDAO + DatabaseConnection para
persistir y consultar el inventario directamente en la base de datos.

Este módulo NO es invocado por ningún controller, DAO ni vista activa.
Se conserva como referencia de diseño OOP pero NO debe usarse en producción.

Gestión real de inventario:
    from dao.producto_dao import ProductoDAO
    ProductoDAO().obtener_todos()
    ProductoDAO().actualizar_stock(id_producto, cantidad)
"""

import warnings
warnings.warn(
    "models.inventario está desconectado del flujo real. "
    "Usa dao.producto_dao.ProductoDAO para gestión de inventario.",
    DeprecationWarning,
    stacklevel=2,
)

import threading
from models.producto import Producto
from exceptions import ProductoNoEncontradoError


class Inventario:
    """
    [LEGACY] Repositorio en memoria de productos. Singleton.
    Ver advertencia del módulo — no usar en código nuevo.
    """

    _instancia: "Inventario | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "Inventario":
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    obj = super().__new__(cls)
                    obj.__dict__["_Inventario__productos"] = []
                    cls._instancia = obj
        return cls._instancia

    @classmethod
    def instancia(cls) -> "Inventario":
        return cls()

    def agregar_producto(self, producto: Producto) -> None:
        self.__productos.append(producto)

    def buscar_producto(self, id_producto) -> Producto:
        for producto in self.__productos:
            if producto.id_producto == id_producto:
                return producto
        raise ProductoNoEncontradoError(id_producto)

    def eliminar_producto(self, id_producto) -> None:
        producto = self.buscar_producto(id_producto)
        self.__productos.remove(producto)

    def mostrar_catalogo(self) -> None:
        if not self.__productos:
            print("Inventario vacío.")
            return
        for producto in self.__productos:
            producto.mostrar_producto()

    def total_productos(self) -> int:
        return len(self.__productos)

    @staticmethod
    def hay_stock_suficiente(producto: Producto, cantidad: int) -> bool:
        return producto.stock >= cantidad

    def __repr__(self) -> str:
        return f"<Inventario [LEGACY] productos={len(self.__productos)}>"