"""
Controller: Venta.
Responsabilidad: orquestar el registro de ventas (cabecera + detalles),
actualización de stock y consultas del historial.
Aplica SRP — sólo gestiona el flujo de venta.
"""

from datetime import datetime
from database import DatabaseConnection
from dao.venta_dao import VentaDAO
from dao.detalle_venta_dao import DetalleVentaDAO
from dao.producto_dao import ProductoDAO
from dao.cliente_dao import ClienteDAO
from models.venta import Venta
from models.detalle_venta import DetalleVenta
from exceptions import (
    VentaNoEncontradaError,
    StockInsuficienteError,
    ProductoNoEncontradoError,
    BaseDatosError,
    ValidacionError,
)
from UTIL.helpers import convertir_a_int


class VentaController:
    """Orquesta el ciclo completo de una venta."""

    def __init__(self):
        self._venta_dao   = VentaDAO()
        self._detalle_dao = DetalleVentaDAO()
        self._producto_dao = ProductoDAO()
        self._cliente_dao  = ClienteDAO()
        self._db = DatabaseConnection()

    # ── Consultas ─────────────────────────────────────────────────────────────

    def listar(self) -> list:
        """
        Retorna todas las ventas con datos de cliente y empleado.
        Cada fila: (id_venta, fecha, total, nombre_cliente, nombre_empleado)
        """
        return self._venta_dao.obtener_completo()

    def listar_clientes_combo(self) -> list[str]:
        """Lista 'ID — Nombre' para ComboBoxes de selección de cliente."""
        clientes = self._cliente_dao.obtener_todos()
        return [f"{c.id_usuario} — {c.nombre}" for c in clientes]

    def obtener_detalles(self, id_venta) -> list:
        """Retorna las filas de detalle_venta de una venta específica."""
        return self._detalle_dao.obtener_por_venta(id_venta)

    # ── Mutaciones ────────────────────────────────────────────────────────────

    def registrar(
        self,
        id_cliente: str,
        id_empleado: str,
        items: list[tuple],
    ) -> int:
        """
        Registra una venta completa de forma transaccional.

        Args:
            id_cliente  — ID del cliente.
            id_empleado — ID del empleado que realiza la venta.
            items       — lista de (id_producto, cantidad: int).

        Retorna:
            id_venta generado.

        Lanza:
            ValidacionError         — items vacío.
            ProductoNoEncontradoError — si algún producto no existe.
            StockInsuficienteError   — si no hay stock suficiente.
            BaseDatosError          — error de infraestructura.
        """
        if not items:
            raise ValidacionError("items", "la venta debe tener al menos un producto")

        # 1. Obtener productos y construir detalles (valida stock en memoria)
        detalles_obj: list[DetalleVenta] = []
        for id_prod, cantidad in items:
            cantidad = convertir_a_int(cantidad)
            if cantidad <= 0:
                raise ValidacionError("cantidad", "debe ser mayor que cero")
            producto = self._producto_dao.obtener_por_id(id_prod)
            if producto.stock < cantidad:
                raise StockInsuficienteError(producto.nombre, producto.stock, cantidad)
            detalle = DetalleVenta(producto, cantidad)
            detalles_obj.append(detalle)

        total = sum(d.subtotal for d in detalles_obj)

        # 2. Insertar cabecera de venta
        venta = Venta(None, id_cliente, id_empleado, datetime.now(), total)
        self._venta_dao.insertar(venta)   # asigna venta.id_venta

        # 3. Insertar detalles directamente (evita dependencia del id_venta
        #    en el modelo DetalleVenta, que no expone ese atributo públicamente)
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            for detalle in detalles_obj:
                cursor.execute(
                    """
                    INSERT INTO detalle_venta
                        (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        venta.id_venta,
                        detalle.id_producto,
                        detalle.cantidad,
                        detalle.precio_unitario,
                        detalle.subtotal,
                    ),
                )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise BaseDatosError(f"Error al insertar detalles: {e}") from e
        finally:
            cursor.close()

        # 4. Descontar stock por producto
        for id_prod, cantidad in items:
            self._producto_dao.actualizar_stock(id_prod, convertir_a_int(cantidad))

        return venta.id_venta

    def eliminar(self, id_venta) -> None:
        """
        Elimina una venta y sus detalles (sin revertir el stock).
        Lanza VentaNoEncontradaError si no existe.
        """
        self._detalle_dao.eliminar_por_venta(id_venta)
        self._venta_dao.eliminar(id_venta)