"""
Controller: Venta.
Responsabilidad: orquestar el registro de ventas (cabecera + detalles),
actualización de stock y consultas del historial.
Aplica SRP — sólo gestiona el flujo de venta.

CORRECCIONES — Fase 1:
  - #2:  registrar() — venta, detalles y descuento de stock se ejecutan en
         una ÚNICA transacción.
  - #18: eliminar() — antes de borrar la venta se consultan sus detalles y se
         repone el stock de cada producto en la misma transacción atómica.
  - #7  (refuerzo): el UPDATE de stock incluye AND stock >= %s.

CORRECCIÓN NE-TYPE — Mismatch de tipo en id_producto:
    Los UPDATE/SELECT de stock dentro de registrar() y eliminar() usaban
    id_prod tal como venía del carrito (puede ser int si el ID es numérico,
    p. ej. 44444).  MySQL/TiDB al comparar un INTEGER contra una columna
    varchar(20) intenta castear todas las filas y falla con 'PD8827'.
    Solución: str(id_prod) en todos los parámetros que tocan id_producto.
"""

from datetime import datetime
from database import DatabaseConnection
from dao.venta_dao import VentaDAO
from dao.detalle_venta_dao import DetalleVentaDAO
from dao.producto_dao import ProductoDAO
from dao.cliente_dao import ClienteDAO
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
        self._venta_dao    = VentaDAO()
        self._detalle_dao  = DetalleVentaDAO()
        self._producto_dao = ProductoDAO()
        self._cliente_dao  = ClienteDAO()
        self._db           = DatabaseConnection()

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
        Registra una venta completa de forma ATÓMICA.

        CORRECCIÓN #2: toda la escritura ocurre en una única transacción.
        CORRECCIÓN #7: UPDATE stock con AND stock >= %s previene negativos.
        CORRECCIÓN NE-TYPE: str(id_prod) en todos los parámetros de producto.

        Args:
            id_cliente  — ID del cliente.
            id_empleado — ID del empleado que realiza la venta.
            items       — lista de (id_producto, cantidad: int).

        Retorna:
            id_venta generado por AUTO_INCREMENT.
        """
        if not items:
            raise ValidacionError("items", "la venta debe tener al menos un producto")

        # ── 1. Normalizar IDs y cantidades ────────────────────────────────────
        items_normalizados: list[tuple] = []
        for id_prod_raw, cantidad_raw in items:
            cantidad = convertir_a_int(cantidad_raw)
            if cantidad <= 0:
                raise ValidacionError("cantidad", "debe ser mayor que cero")
            # CORRECCIÓN NE-TYPE: siempre guardar id como str para las queries
            id_prod = str(id_prod_raw).strip()
            items_normalizados.append((id_prod, cantidad))

        # ── 2. Pre-validación en memoria (sin escribir nada en BD) ────────────
        detalles_obj: list[DetalleVenta] = []
        for id_prod, cantidad in items_normalizados:
            producto = self._producto_dao.obtener_por_id(id_prod)
            if producto.stock < cantidad:
                raise StockInsuficienteError(producto.nombre, producto.stock, cantidad)
            detalles_obj.append(DetalleVenta(producto, cantidad))

        total = sum(d.subtotal for d in detalles_obj)

        # ── 3. Transacción única: venta + detalles + stock ────────────────────
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # 3a. Insertar cabecera de venta
            cursor.execute(
                """INSERT INTO venta (id_cliente, id_empleado, fecha, total)
                   VALUES (%s, %s, %s, %s)""",
                (id_cliente, id_empleado, datetime.now(), total),
            )
            id_venta = cursor.lastrowid

            # 3b. Insertar líneas de detalle
            for detalle in detalles_obj:
                cursor.execute(
                    """INSERT INTO detalle_venta
                           (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (
                        id_venta,
                        str(detalle.id_producto),   # CORRECCIÓN NE-TYPE
                        detalle.cantidad,
                        detalle.precio_unitario,
                        detalle.subtotal,
                    ),
                )

            # 3c. Descontar stock — AND stock >= %s protege contra negativos (#7)
            for id_prod, cantidad in items_normalizados:
                cursor.execute(
                    "UPDATE producto "
                    "SET stock = stock - %s "
                    "WHERE id_producto = %s AND stock >= %s",
                    (cantidad, str(id_prod), cantidad),   # CORRECCIÓN NE-TYPE
                )
                if cursor.rowcount == 0:
                    cursor.execute(
                        "SELECT nombre, stock FROM producto WHERE id_producto = %s",
                        (str(id_prod),),                  # CORRECCIÓN NE-TYPE
                    )
                    fila = cursor.fetchone()
                    if not fila:
                        raise ProductoNoEncontradoError(id_prod)
                    raise StockInsuficienteError(fila[0], int(fila[1]), cantidad)

            conexion.commit()
            return id_venta

        except (StockInsuficienteError, ProductoNoEncontradoError, ValidacionError):
            conexion.rollback()
            raise
        except Exception as e:
            conexion.rollback()
            raise BaseDatosError(f"Error al registrar venta: {e}") from e
        finally:
            cursor.close()

    def eliminar(self, id_venta) -> None:
        """
        Elimina una venta y sus detalles revirtiendo el stock descontado.

        CORRECCIÓN #18: se repone stock en la misma transacción atómica.
        CORRECCIÓN NE-TYPE: str(id_prod) en UPDATE de stock.
        """
        detalles = self._detalle_dao.obtener_por_venta(id_venta)

        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # Reponer el stock de cada producto involucrado en la venta
            for fila_detalle in detalles:
                # Formato de fila: (id_detalle, id_venta, id_producto,
                #                   cantidad, precio_unitario, subtotal)
                id_prod  = str(fila_detalle[2])   # CORRECCIÓN NE-TYPE
                cantidad = int(fila_detalle[3])
                cursor.execute(
                    "UPDATE producto SET stock = stock + %s WHERE id_producto = %s",
                    (cantidad, id_prod),
                )

            # Eliminar líneas de detalle
            cursor.execute(
                "DELETE FROM detalle_venta WHERE id_venta = %s",
                (id_venta,),
            )

            # Eliminar cabecera de venta
            cursor.execute(
                "DELETE FROM venta WHERE id_venta = %s",
                (id_venta,),
            )
            if cursor.rowcount == 0:
                raise VentaNoEncontradaError(id_venta)

            conexion.commit()

        except VentaNoEncontradaError:
            conexion.rollback()
            raise
        except Exception as e:
            conexion.rollback()
            raise BaseDatosError(f"Error al eliminar venta {id_venta}: {e}") from e
        finally:
            cursor.close()
