"""
Modelo Inventario — Singleton.
Principio: el inventario debe tener una única representación en memoria.
Aplica:
  - Patrón Singleton (__new__ + _instancia).
  - Encapsulamiento: __productos privado.
  - Método estático: verificar disponibilidad de stock.
  - Excepciones especializadas.
"""

import threading
from models.producto import Producto
from exceptions import ProductoNoEncontradoError


class Inventario:
    """
    Repositorio en memoria de productos. Singleton.

    Atributos de clase:
        _instancia  (privado)   — única instancia.
        _lock       (privado)   — mutex para thread-safety.

    Atributos de instancia:
        __productos (privado)   — lista de productos.
    """

    _instancia: "Inventario | None" = None
    _lock: threading.Lock = threading.Lock()

    # ── Singleton ─────────────────────────────────────────────────────────────

    def __new__(cls) -> "Inventario":
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    obj = super().__new__(cls)
                    obj.__dict__["_Inventario__productos"] = []
                    cls._instancia = obj
        return cls._instancia

    # ── Métodos de clase ──────────────────────────────────────────────────────

    @classmethod
    def instancia(cls) -> "Inventario":
        """Punto de acceso explícito al Singleton."""
        return cls()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def agregar_producto(self, producto: Producto) -> None:
        self.__productos.append(producto)

    def buscar_producto(self, id_producto) -> Producto:
        for producto in self.__productos:
            if producto.id_producto == id_producto:
                return producto
        raise ProductoNoEncontradoError(id_producto)

    def eliminar_producto(self, id_producto) -> None:
        producto = self.buscar_producto(id_producto)   # lanza si no existe
        self.__productos.remove(producto)

    def mostrar_catalogo(self) -> None:
        if not self.__productos:
            print("Inventario vacío.")
            return
        for producto in self.__productos:
            producto.mostrar_producto()

    def total_productos(self) -> int:
        return len(self.__productos)

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def hay_stock_suficiente(producto: Producto, cantidad: int) -> bool:
        """
        Método estático: consulta pura — no necesita la instancia del inventario.
        """
        return producto.stock >= cantidad

    def __repr__(self) -> str:
        return f"<Inventario productos={len(self.__productos)}>"