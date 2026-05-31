"""
Modelo DetalleVenta.
Aplica:
  - Encapsulamiento: todos los atributos son privados, expuestos por propiedades.
  - El subtotal se calcula automáticamente y es de sólo lectura.
"""

from models.producto import Producto
from exceptions import ValidacionError


class DetalleVenta:
    """
    Representa una línea de detalle dentro de una venta.

    Atributos (todos privados):
        __id_detalle
        __producto
        __cantidad
        __precio_unitario   — captura el precio en el momento de la venta
        __subtotal          — calculado automáticamente
    """

    def __init__(self, producto: Producto, cantidad: int, id_detalle=None):
        self.__id_detalle = id_detalle
        self.__producto = self._validar_producto(producto)
        self.__cantidad = self._validar_cantidad(cantidad)
        self.__precio_unitario: float = producto.precio_venta
        self.__subtotal: float = self.__precio_unitario * self.__cantidad

    # ── Propiedades públicas ──────────────────────────────────────────────────

    @property
    def id_detalle(self):
        return self.__id_detalle

    @id_detalle.setter
    def id_detalle(self, valor) -> None:
        if self.__id_detalle is None:
            self.__id_detalle = valor

    @property
    def producto(self) -> Producto:
        return self.__producto

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @property
    def precio_unitario(self) -> float:
        return self.__precio_unitario

    @property
    def subtotal(self) -> float:
        return self.__subtotal

    # Necesario para que VentaDAO acceda al id del producto sin romper encapsulamiento
    @property
    def id_producto(self):
        return self.__producto.id_producto

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def calcular_ganancia(self) -> float:
        """Ganancia bruta = (precio_venta - precio_compra) × cantidad."""
        return self.__producto.calcular_ganancia_unitaria() * self.__cantidad

    def mostrar_detalle(self) -> None:
        print(
            f"  • {self.__producto.nombre} x{self.__cantidad} "
            f"@ ${self.__precio_unitario:.2f} = ${self.__subtotal:.2f}"
        )

    # ── Validaciones privadas ─────────────────────────────────────────────────

    @staticmethod
    def _validar_producto(producto) -> Producto:
        if not isinstance(producto, Producto):
            raise ValidacionError("producto", "debe ser una instancia de Producto")
        return producto

    @staticmethod
    def _validar_cantidad(cantidad) -> int:
        try:
            v = int(cantidad)
        except (ValueError, TypeError):
            raise ValidacionError("cantidad", "debe ser un entero")
        if v <= 0:
            raise ValidacionError("cantidad", "debe ser mayor que cero")
        return v

    def __repr__(self) -> str:
        return (
            f"<DetalleVenta producto={self.__producto.nombre} "
            f"cantidad={self.__cantidad} subtotal={self.__subtotal}>"
        )