"""
Controller: Producto.
Responsabilidad: mediar entre la vista de gestión de productos y el ProductoDAO.
Aplica SRP — sólo orquesta operaciones CRUD sobre productos.

CORRECCIONES aplicadas:
  - #4  (Fase 3): _validar_id() devuelve str compatible con varchar(20).
  - NE-1 (Fase 7): _validar_precio() elimina caracteres de formato monetario
        ("$", ",", espacios) antes de intentar la conversión a float.
        Sin este paso, valores como "$1,200,000.00" que provienen del
        formulario de edición (_cargar_en_form ya hacía replace, pero
        rutas alternativas podían omitirlo) lanzaban ValueError dentro
        de convertir_a_float() y devolvían 0.0, pasando la guardia de
        es_numero_positivo() silenciosamente con precio cero.
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
        return self._dao.obtener_todos()

    def obtener(self, id_producto) -> Producto:
        return self._dao.obtener_por_id(id_producto)

    def listar_para_combo(self) -> list[str]:
        productos = self.listar()
        return [
            f"{p.id_producto} — {p.nombre}  (Stock: {p.stock})"
            for p in productos
        ]

    # ── Mutaciones ────────────────────────────────────────────────────────────

    def agregar(
        self,
        id_producto: str,
        nombre: str,
        marca: str,
        precio_compra: str,
        precio_venta: str,
        stock: str,
    ) -> None:
        """
        Valida y registra un nuevo producto con ID manual obligatorio.
        Lanza ValidacionError si algún campo es inválido.
        """
        id_p = self._validar_id(id_producto)
        self._validar_texto(nombre, "Nombre")
        self._validar_texto(marca, "Marca")
        pc = self._validar_precio(precio_compra, "Precio Compra")
        pv = self._validar_precio(precio_venta,  "Precio Venta")
        st = self._validar_stock(stock)

        producto = Producto(nombre.strip(), marca.strip(), pc, pv, st, id_p)
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
        self._validar_texto(nombre, "Nombre")
        self._validar_texto(marca, "Marca")
        pc = self._validar_precio(precio_compra, "Precio Compra")
        pv = self._validar_precio(precio_venta,  "Precio Venta")
        st = self._validar_stock(stock)

        producto = Producto(nombre.strip(), marca.strip(), pc, pv, st, id_producto)
        self._dao.actualizar(producto)

    def eliminar(self, id_producto) -> None:
        self._dao.eliminar(id_producto)

    # ── Validaciones privadas ─────────────────────────────────────────────────

    @staticmethod
    def _validar_id(valor: str) -> str:
        """
        CORRECCIÓN #4 — id_producto es varchar(20) en la BD, no int.
        Acepta cualquier cadena no vacía de hasta 20 caracteres.
        """
        val = str(valor).strip()
        if not val:
            raise ValidacionError("ID Producto", "no puede estar vacío")
        if len(val) > 20:
            raise ValidacionError("ID Producto", "máximo 20 caracteres (varchar en BD)")
        return val

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        if not validar_no_vacio(valor):
            raise ValidacionError(campo, "no puede estar vacío")
        return str(valor).strip()

    @staticmethod
    def _validar_precio(valor: str, campo: str) -> float:
        """
        CORRECCIÓN NE-1 (Fase 7) — Limpieza de formato monetario.

        El formulario de edición (_cargar_en_form) ya hacía .replace("$","")
        y .replace(",","") al cargar el valor desde la tabla, pero otras rutas
        de acceso (p. ej. copiar-pegar desde un campo externo, o formatear el
        valor antes de enviarlo) podían llegar con el formato completo
        "$1,200,000.00".  convertir_a_float() usa float() directamente y
        lanza ValueError ante cualquier caracter no numérico, devolviendo
        después 0.0 desde el helper — lo que silenciosamente pasaba la guardia
        de es_numero_positivo() con un precio incorrecto.

        Solución: limpiar el string ANTES de cualquier comprobación numérica.
        """
        # Eliminar símbolos de formato monetario y espacios
        limpio = (
            str(valor)
            .replace("$", "")
            .replace(",", "")
            .replace(" ", "")
            .strip()
        )
        if not es_numero_positivo(limpio):
            raise ValidacionError(campo, "debe ser un número mayor que cero")
        return convertir_a_float(limpio)

    @staticmethod
    def _validar_stock(valor: str) -> int:
        try:
            v = int(valor)
        except (ValueError, TypeError):
            raise ValidacionError("Stock", "debe ser un número entero")
        if v < 0:
            raise ValidacionError("Stock", "no puede ser negativo")
        return v