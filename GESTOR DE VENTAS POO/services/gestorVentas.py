"""
Servicio GestorVentas — Singleton.
Aplica:
  - Patrón Singleton: única instancia del gestor de ventas activo.
  - Encapsulamiento: __ventas privado.
  - Método de clase: punto de acceso al Singleton.
  - Métodos estáticos: lógica de negocio sin estado.
  - Excepciones especializadas: VentaNoEncontradaError.
"""

import threading
from models.venta import Venta
from exceptions import VentaNoEncontradaError, VentaVaciaError


class GestorVentas:
    """
    Gestor central de ventas. Patrón Singleton.

    Atributos de clase:
        _instancia  (privado)
        _lock       (privado)

    Atributos de instancia:
        __ventas    (privado) — lista de ventas en memoria.
    """

    _instancia: "GestorVentas | None" = None
    _lock: threading.Lock = threading.Lock()

    # ── Singleton ─────────────────────────────────────────────────────────────

    def __new__(cls) -> "GestorVentas":
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    obj = super().__new__(cls)
                    obj.__dict__["_GestorVentas__ventas"] = []
                    cls._instancia = obj
        return cls._instancia

    # ── Métodos de clase ──────────────────────────────────────────────────────

    @classmethod
    def instancia(cls) -> "GestorVentas":
        """Punto de acceso explícito al Singleton."""
        return cls()

    @classmethod
    def resetear(cls) -> None:
        """Destruye la instancia (útil en tests)."""
        with cls._lock:
            cls._instancia = None

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def crear_venta(self, id_venta, id_cliente, id_empleado) -> Venta:
        venta = Venta(id_venta, id_cliente, id_empleado)
        self.__ventas.append(venta)
        return venta

    def agregar_producto_a_venta(self, id_venta, producto, cantidad: int) -> None:
        """
        Agrega un producto a la venta indicada.
        Propaga StockInsuficienteError si el stock es insuficiente.
        """
        venta = self.buscar_venta(id_venta)
        venta.agregar_producto(producto, cantidad)

    def buscar_venta(self, id_venta) -> Venta:
        for venta in self.__ventas:
            if venta.id_venta == id_venta:
                return venta
        raise VentaNoEncontradaError(id_venta)

    def eliminar_venta(self, id_venta) -> None:
        venta = self.buscar_venta(id_venta)   # lanza si no existe
        self.__ventas.remove(venta)

    def mostrar_ventas(self) -> None:
        if not self.__ventas:
            print("No hay ventas registradas.")
            return
        for venta in self.__ventas:
            venta.mostrar_venta()

    def total_ventas(self) -> int:
        return len(self.__ventas)

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def calcular_total_con_descuento(subtotal: float, porcentaje_descuento: float) -> float:
        """
        Método estático: matemática pura de negocio.
        porcentaje_descuento: valor entre 0 y 100.
        """
        if not (0 <= porcentaje_descuento <= 100):
            from exceptions import DescuentoInvalidoError
            raise DescuentoInvalidoError(porcentaje_descuento)
        factor = 1 - (porcentaje_descuento / 100)
        return round(subtotal * factor, 2)

    def __repr__(self) -> str:
        return f"<GestorVentas ventas_en_memoria={len(self.__ventas)}>"