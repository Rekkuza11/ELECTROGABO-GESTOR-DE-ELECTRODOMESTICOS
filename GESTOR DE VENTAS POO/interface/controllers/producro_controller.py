"""
Controller: Producto.
Responsabilidad: mediar entre la vista de gestión de productos y el ProductoDAO.
Aplica SRP — sólo orquesta operaciones CRUD sobre productos.
"""

from dao.producto_dao import ProductoDAO
from models.producto import Producto
from exceptions import (
    ProductoNoEncontradoError,
    BaseDatosError,
    ValidacionError,
    PrecioInvalidoError,
)
from UTIL.helpers import validar_no_vacio, convertir_a_float, convertir_a_int, es_numero_positivo


class ProductoController:
    """Coordina la lógica de negocio entre la vista y el DAO de Producto."""

    def __init__(self):
        self._dao = ProductoDAO()

    # ── Consultas ─────────────────────────────────────────────────────────────

    def listar(self) -> list[Producto]:
        """Retorna todos los productos del inventario."""
        return self._dao.obtener_todos()

    def obtener(self, id_producto) -> Producto:
        """
        Retorna un producto por ID.
        Lanza ProductoNoEncontradoError si no existe.
        """
        return self._dao.obtener_por_id(id_producto)

    def listar_para_combo(self) -> list[str]:
        """
        Retorna lista de strings 'ID — Nombre (Stock: N)' para ComboBoxes.
        """
        productos = self.listar()
        return [
            f"{p.id_producto} — {p.nombre}  (Stock: {p.stock})"
            for p in productos
        ]

    # ── Mutaciones ────────────────────────────────────────────────────────────

    def agregar(
        self,
        nombre: str,
        marca: str,
        precio_compra: str,
        precio_venta: str,
        stock: str,
    ) -> None:
        """
        Valida y registra un nuevo producto.
        Lanza ValidacionError o PrecioInvalidoError si los datos son inválidos.
        """
        self._validar_texto(nombre, "Nombre")
        self._validar_texto(marca, "Marca")
        pc = self._validar_precio(precio_compra, "Precio Compra")
        pv = self._validar_precio(precio_venta, "Precio Venta")
        st = self._validar_stock(stock)

        producto = Producto(nombre.strip(), marca.strip(), pc, pv, st)
        self._dao.insertar(producto)

    def actualizar(
        self,
        id_producto,
        nombre: str,
        marca: str,
        precio_compra: str,
        precio_venta: str,
        stock: str,
    ) -> None:
        """
        Valida y actualiza un producto existente.
        Lanza ProductoNoEncontradoError si el ID no existe.
        """
        self._validar_texto(nombre, "Nombre")
        self._validar_texto(marca, "Marca")
        pc = self._validar_precio(precio_compra, "Precio Compra")
        pv = self._validar_precio(precio_venta, "Precio Venta")
        st = self._validar_stock(stock)

        producto = Producto(nombre.strip(), marca.strip(), pc, pv, st, id_producto)
        self._dao.actualizar(producto)

    def eliminar(self, id_producto) -> None:
        """
        Elimina un producto por ID.
        Lanza ProductoNoEncontradoError si no existe.
        """
        self._dao.eliminar(id_producto)

    # ── Validaciones privadas ─────────────────────────────────────────────────

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        if not validar_no_vacio(valor):
            raise ValidacionError(campo, "no puede estar vacío")
        return str(valor).strip()

    @staticmethod
    def _validar_precio(valor: str, campo: str) -> float:
        if not es_numero_positivo(valor):
            raise ValidacionError(campo, "debe ser un número mayor que cero")
        return convertir_a_float(valor)

    @staticmethod
    def _validar_stock(valor: str) -> int:
        try:
            v = int(valor)
        except (ValueError, TypeError):
            raise ValidacionError("Stock", "debe ser un número entero")
        if v < 0:
            raise ValidacionError("Stock", "no puede ser negativo")
        return v