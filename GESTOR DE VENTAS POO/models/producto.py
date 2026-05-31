"""
Modelo Producto.
Aplica:
  - Encapsulamiento: todos los atributos privados, expuestos por propiedades.
  - Método estático: cálculo de margen (no depende del estado de instancia).
  - Método de clase: fábrica desde fila de BD.
  - Excepciones especializadas para stock y precio.

Fase 6:
  - #21: desde_fila_bd() ya no normaliza precios silenciosamente a 0.01.
         Si un precio en BD es inválido, PrecioInvalidoError emerge de forma
         visible en lugar de enmascarar el problema con un valor ficticio.
  - #24: id_producto.setter lanza ValidacionError si se intenta cambiar un ID
         ya asignado, en lugar de ignorar la operación en silencio.
"""

from exceptions import StockInsuficienteError, PrecioInvalidoError, ValidacionError


class Producto:
    """
    Representa un producto del inventario.

    Atributos de instancia (todos privados):
        __id_producto, __nombre, __marca,
        __precio_compra, __precio_venta, __stock
    """

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(
        self,
        nombre: str,
        marca: str,
        precio_compra: float,
        precio_venta: float,
        stock: int,
        id_producto=None,
    ):
        self.__id_producto  = id_producto
        self.__nombre       = self._validar_nombre(nombre)
        self.__marca        = self._validar_marca(marca)
        self.__precio_compra = self._validar_precio(precio_compra, "precio_compra")
        self.__precio_venta  = self._validar_precio(precio_venta, "precio_venta")
        self.__stock        = self._validar_stock(stock)

    # ── Propiedades públicas ──────────────────────────────────────────────────

    @property
    def id_producto(self):
        return self.__id_producto

    @id_producto.setter
    def id_producto(self, valor) -> None:
        """
        CORRECCIÓN #24: ya no silencia el intento de cambiar un ID ya asignado.
        El ID es inmutable una vez persistido; intentar cambiarlo es un error
        de programación que debe ser visible de inmediato.
        """
        if self.__id_producto is None:
            self.__id_producto = valor
        else:
            raise ValidacionError(
                "id_producto",
                "no se puede cambiar una vez asignado (inmutabilidad post-persistencia)"
            )

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = self._validar_nombre(valor)

    @property
    def marca(self) -> str:
        return self.__marca

    @marca.setter
    def marca(self, valor: str) -> None:
        self.__marca = self._validar_marca(valor)

    @property
    def precio_compra(self) -> float:
        return self.__precio_compra

    @precio_compra.setter
    def precio_compra(self, valor: float) -> None:
        self.__precio_compra = self._validar_precio(valor, "precio_compra")

    @property
    def precio_venta(self) -> float:
        return self.__precio_venta

    @precio_venta.setter
    def precio_venta(self, valor: float) -> None:
        self.__precio_venta = self._validar_precio(valor, "precio_venta")

    @property
    def stock(self) -> int:
        return self.__stock

    # ── Métodos de clase ──────────────────────────────────────────────────────

    @classmethod
    def desde_fila_bd(cls, fila: tuple) -> "Producto":
        """
        Fábrica: (id, nombre, marca, precio_compra, precio_venta, stock).

        CORRECCIÓN #21: se elimina la normalización silenciosa de precios a 0.01.
        Si la BD contiene un precio inválido (cero o negativo), el constructor
        lanzará PrecioInvalidoError de forma visible, en lugar de sustituir el
        valor por 0.01 sin ningún aviso.  Esto permite detectar y corregir datos
        incorrectos en lugar de ocultarlos.
        """
        id_p, nombre, marca, p_compra, p_venta, stock = fila
        return cls(nombre, marca, float(p_compra), float(p_venta), stock, id_p)

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def calcular_margen(precio_compra: float, precio_venta: float) -> float:
        """
        Método estático: calcula el margen de ganancia porcentual.
        No requiere instancia — es lógica pura de dominio.
        """
        if precio_compra <= 0:
            raise PrecioInvalidoError(precio_compra)
        return round(((precio_venta - precio_compra) / precio_compra) * 100, 2)

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def actualizar_precio_venta(self, nuevo_precio: float) -> None:
        self.precio_venta = nuevo_precio

    def aumentar_stock(self, cantidad: int) -> None:
        cantidad = self._validar_cantidad(cantidad)
        self.__stock += cantidad

    def reducir_stock(self, cantidad: int) -> None:
        cantidad = self._validar_cantidad(cantidad)
        if cantidad > self.__stock:
            raise StockInsuficienteError(self.__nombre, self.__stock, cantidad)
        self.__stock -= cantidad

    def calcular_ganancia_unitaria(self) -> float:
        return self.__precio_venta - self.__precio_compra

    def mostrar_producto(self) -> None:
        print(
            f"[{self.__id_producto}] {self.__nombre} ({self.__marca}) | "
            f"Venta: ${self.__precio_venta:.2f} | Stock: {self.__stock}"
        )

    # ── Métodos privados de validación ────────────────────────────────────────

    def _validar_nombre(self, nombre: str) -> str:
        if not nombre or not str(nombre).strip():
            raise ValidacionError("nombre", "no puede estar vacío")
        return str(nombre).strip()

    def _validar_marca(self, marca: str) -> str:
        if not marca or not str(marca).strip():
            raise ValidacionError("marca", "no puede estar vacía")
        return str(marca).strip()

    @staticmethod
    def _validar_precio(valor, campo: str = "precio") -> float:
        try:
            v = float(valor)
        except (ValueError, TypeError):
            raise PrecioInvalidoError(valor)
        if v <= 0:
            raise PrecioInvalidoError(v)
        return v

    @staticmethod
    def _validar_stock(valor) -> int:
        try:
            v = int(valor)
        except (ValueError, TypeError):
            raise ValidacionError("stock", "debe ser un número entero")
        if v < 0:
            raise ValidacionError("stock", "no puede ser negativo")
        return v

    @staticmethod
    def _validar_cantidad(cantidad) -> int:
        try:
            v = int(cantidad)
        except (ValueError, TypeError):
            raise ValidacionError("cantidad", "debe ser un número entero")
        if v <= 0:
            raise ValidacionError("cantidad", "debe ser mayor que cero")
        return v

    def __repr__(self) -> str:
        return (
            f"<Producto id={self.__id_producto} nombre='{self.__nombre}' "
            f"stock={self.__stock}>"
        )