"""
Controller: Venta.
Responsabilidad: orquestar el registro de ventas (cabecera + detalles),
actualización de stock y consultas del historial.
Aplica SRP — sólo gestiona el flujo de venta.

CORRECCIONES — Fase 1:
  - #2:  registrar() — venta, detalles y descuento de stock se ejecutan en
         una ÚNICA transacción.  Si cualquier paso falla se llama rollback()
         y la BD queda exactamente como estaba.  Ya no se delegan los INSERT
         a VentaDAO/DetalleVentaDAO (que hacían commit propios); se ejecutan
         directamente sobre el cursor compartido.
  - #18: eliminar() — antes de borrar la venta se consultan sus detalles y se
         repone el stock de cada producto en la misma transacción atómica.
         Stock y registros quedan siempre consistentes.
  - #7  (refuerzo): el UPDATE de stock incluye AND stock >= %s para que el
         motor rechace la operación si el stock bajó entre la pre-validación
         y el commit (protección ante concurrencia).
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

        CORRECCIÓN #2:
            Toda la escritura en BD (INSERT venta, INSERT detalles, UPDATE stock)
            ocurre dentro de una única transacción con un solo cursor.  Si
            cualquiera de los pasos falla se invoca rollback() y no queda
            ningún registro parcial en la base de datos.

        Flujo:
            1. Normalizar y validar items (en memoria, sin tocar BD).
            2. Pre-validar existencia y stock de cada producto (SELECTs).
            3. Abrir transacción única:
               a. INSERT INTO venta → obtener id_venta.
               b. INSERT INTO detalle_venta por cada línea.
               c. UPDATE stock con AND stock >= %s (previene negativos, fix #7).
                  Si rowcount == 0 → rollback y StockInsuficienteError.
            4. commit() — o rollback() ante cualquier excepción.

        Args:
            id_cliente  — ID del cliente.
            id_empleado — ID del empleado que realiza la venta.
            items       — lista de (id_producto, cantidad: int).

        Retorna:
            id_venta generado por AUTO_INCREMENT.

        Lanza:
            ValidacionError           — items vacío o cantidad inválida.
            ProductoNoEncontradoError — algún producto no existe.
            StockInsuficienteError    — stock insuficiente (en pre-validación
                                        o durante el UPDATE atómico).
            BaseDatosError            — error de infraestructura.
        """
        if not items:
            raise ValidacionError("items", "la venta debe tener al menos un producto")

        # ── 1. Normalizar IDs y cantidades ────────────────────────────────────
        items_normalizados: list[tuple] = []
        for id_prod_raw, cantidad_raw in items:
            cantidad = convertir_a_int(cantidad_raw)
            if cantidad <= 0:
                raise ValidacionError("cantidad", "debe ser mayor que cero")
            try:
                id_prod = int(id_prod_raw)
            except (ValueError, TypeError):
                id_prod = id_prod_raw  # ID alfanumérico: mantener como str
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
                        detalle.id_producto,
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
                    (cantidad, id_prod, cantidad),
                )
                if cursor.rowcount == 0:
                    # El stock cambió entre la pre-validación y este UPDATE
                    # (ej. otra transacción concurrente lo redujo).
                    cursor.execute(
                        "SELECT nombre, stock FROM producto WHERE id_producto = %s",
                        (id_prod,),
                    )
                    fila = cursor.fetchone()
                    if not fila:
                        raise ProductoNoEncontradoError(id_prod)
                    raise StockInsuficienteError(fila[0], int(fila[1]), cantidad)

            # Todo correcto: confirmar la transacción completa
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

        CORRECCIÓN #18:
            Antes de borrar cualquier registro, se recuperan los detalles
            de la venta y se reponen las unidades de cada producto en la
            misma transacción.  Si algo falla, rollback() deja la BD intacta:
            ni la venta se borra ni el stock se modifica.

        Flujo:
            1. SELECT detalle_venta (lectura previa, cursor independiente).
            2. Abrir transacción única:
               a. UPDATE stock = stock + cantidad  por cada detalle.
               b. DELETE FROM detalle_venta.
               c. DELETE FROM venta — si rowcount == 0 → VentaNoEncontradaError.
            3. commit() — o rollback() ante cualquier excepción.

        Lanza:
            VentaNoEncontradaError — la venta no existe.
            BaseDatosError         — error de infraestructura.
        """
        # Obtener detalles ANTES de iniciar la transacción de escritura.
        # DetalleVentaDAO usa su propio cursor y lo cierra en finally,
        # por lo que no interfiere con el cursor de la transacción siguiente.
        detalles = self._detalle_dao.obtener_por_venta(id_venta)

        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # Reponer el stock de cada producto involucrado en la venta
            for fila_detalle in detalles:
                # Formato de fila: (id_detalle, id_venta, id_producto,
                #                   cantidad, precio_unitario, subtotal)
                id_prod  = fila_detalle[2]
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