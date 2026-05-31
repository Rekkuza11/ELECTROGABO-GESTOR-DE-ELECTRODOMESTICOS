"""
Modelo Venta.
Aplica:
  - Encapsulamiento: atributos privados, acceso controlado.
  - Método estático: validación de descuento (lógica pura).
  - Excepciones especializadas: StockInsuficienteError, VentaVaciaError, DescuentoInvalidoError.
"""

from __future__ import annotations
from typing import List
from exceptions import VentaVaciaError, DescuentoInvalidoError


class Venta:
    """
    Representa una transacción de venta.

    Atributos (privados):
        __id_venta, __id_cliente, __id_empleado, __detalles, __fecha, __total
    """

    def __init__(self, id_venta, id_cliente, id_empleado, fecha=None, total: float = 0.0):
        self.__id_venta = id_venta
        self.__id_cliente = id_cliente
        self.__id_empleado = id_empleado
        self.__fecha = fecha
        self.__total = total
        self.__detalles: List = []

    # ── Propiedades públicas ──────────────────────────────────────────────────

    @property
    def id_venta(self):
        return self.__id_venta

    @id_venta.setter
    def id_venta(self, valor) -> None:
        if self.__id_venta is None:
            self.__id_venta = valor

    @property
    def id_cliente(self):
        return self.__id_cliente

    @property
    def id_empleado(self):
        return self.__id_empleado

    @property
    def fecha(self):
        return self.__fecha

    @fecha.setter
    def fecha(self, valor) -> None:
        self.__fecha = valor

    @property
    def total(self) -> float:
        return self.__total

    @total.setter
    def total(self, valor: float) -> None:
        self.__total = float(valor)

    @property
    def detalles(self) -> List:
        """Retorna copia de la lista para preservar encapsulamiento."""
        return list(self.__detalles)

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def agregar_detalle(self, detalle) -> None:
        """
        Agrega un DetalleVenta ya construido.
        La reducción de stock debe manejarse en la capa de servicio (SRP).
        """
        self.__detalles.append(detalle)

    def agregar_producto(self, producto, cantidad: int) -> None:
        """
        Crea y agrega un detalle a partir de un producto y cantidad.
        Delega al producto la validación de stock (lanza StockInsuficienteError).
        """
        from models.detalle_venta import DetalleVenta   # import local evita circular
        producto.reducir_stock(cantidad)
        detalle = DetalleVenta(producto, cantidad)
        self.__detalles.append(detalle)

    def calcular_total(self, descuento: float = 1.0) -> float:
        """
        Suma los subtotales y aplica un factor de descuento.
        Lanza VentaVaciaError si no hay detalles.
        Lanza DescuentoInvalidoError si el factor está fuera de [0, 1].
        """
        if not self.__detalles:
            raise VentaVaciaError()
        self._validar_descuento(descuento)
        subtotal = sum(d.subtotal for d in self.__detalles)
        self.__total = round(subtotal * descuento, 2)
        return self.__total

    def calcular_ganancia(self) -> float:
        """Ganancia bruta total de la venta."""
        return sum(d.calcular_ganancia() for d in self.__detalles)

    def mostrar_venta(self) -> None:
        print(f"\n{'─'*40}")
        print(f"Venta    : {self.__id_venta}")
        print(f"Cliente  : {self.__id_cliente}")
        print(f"Empleado : {self.__id_empleado}")
        print(f"Fecha    : {self.__fecha}")
        for detalle in self.__detalles:
            detalle.mostrar_detalle()
        print(f"Total    : ${self.__total:.2f}")

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def _validar_descuento(descuento: float) -> None:
        """
        Método estático: regla de negocio sobre el factor de descuento.
        No necesita estado de instancia.
        """
        try:
            v = float(descuento)
        except (ValueError, TypeError):
            raise DescuentoInvalidoError(descuento)
        if not (0.0 <= v <= 1.0):
            raise DescuentoInvalidoError(v)

    def __repr__(self) -> str:
        return (
            f"<Venta id={self.__id_venta} cliente={self.__id_cliente} "
            f"detalles={len(self.__detalles)} total={self.__total}>"
        )