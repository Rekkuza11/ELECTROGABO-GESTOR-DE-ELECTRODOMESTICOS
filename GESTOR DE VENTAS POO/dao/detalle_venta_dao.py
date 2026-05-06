"""
DAO DetalleVenta.
Aplica:
  - Singleton DatabaseConnection.
  - Encapsulamiento: método privado de extracción de valores.
  - Excepciones especializadas: IntegridadDatosError, BaseDatosError.
  - Cierre explícito del cursor en bloque finally (corrige omisión original).
"""

from database import DatabaseConnection
from exceptions import IntegridadDatosError, BaseDatosError


class DetalleVentaDAO:
    """Objeto de acceso a datos para la entidad DetalleVenta."""

    def __init__(self):
        self._db = DatabaseConnection()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def insertar(self, detalle) -> None:
        """
        Persiste un DetalleVenta en la base de datos.
        Lanza IntegridadDatosError si viola FK (id_venta o id_producto inexistente).
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                INSERT INTO detalle_venta
                    (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, self.__a_valores(detalle))
            conexion.commit()

            # Asigna el ID generado al objeto (sin romper encapsulamiento del modelo)
            detalle.id_detalle = cursor.lastrowid

        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, "insertar detalle_venta")
        finally:
            cursor.close()

    def obtener_por_venta(self, id_venta) -> list:
        """Retorna todas las filas de detalle asociadas a una venta."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT * FROM detalle_venta WHERE id_venta = %s",
                (id_venta,)
            )
            return cursor.fetchall()
        except Exception as e:
            self.__manejar_error(e, f"obtener detalles de venta {id_venta}")
        finally:
            cursor.close()

    def eliminar_por_venta(self, id_venta) -> None:
        """Elimina todos los detalles de una venta (usado antes de eliminar la venta)."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "DELETE FROM detalle_venta WHERE id_venta = %s",
                (id_venta,)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar detalles de venta {id_venta}")
        finally:
            cursor.close()

    # ── Privados de ayuda ─────────────────────────────────────────────────────

    @staticmethod
    def __a_valores(detalle) -> tuple:
        """Extrae los valores del DetalleVenta en el orden esperado por SQL."""
        return (
            detalle.id_venta,
            detalle.id_producto,
            detalle.cantidad,
            detalle.precio_unitario,
            detalle.subtotal,
        )

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "foreign key" in mensaje.lower() or "Cannot add or update" in mensaje:
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error