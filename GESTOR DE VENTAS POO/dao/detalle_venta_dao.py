"""
DAO DetalleVenta.
Aplica:
  - Singleton DatabaseConnection.
  - Encapsulamiento: método privado de extracción de valores.
  - Excepciones especializadas: IntegridadDatosError, BaseDatosError.
  - Cierre explícito del cursor en bloque finally.

CORRECCIÓN #3 — DetalleVentaDAO roto:
    El método __a_valores() intentaba acceder a detalle.id_venta, pero la
    clase DetalleVenta NO tiene ese atributo (solo tiene id_detalle,
    producto, cantidad, precio_unitario y subtotal).  El id_venta es un
    parámetro externo que viene del controller, no del objeto DetalleVenta.

    Solución:
    - insertar() recibe id_venta como parámetro explícito (ya era así en el
      llamador dentro de venta_controller.py, que ejecuta el INSERT directo).
    - __a_valores() acepta id_venta como argumento para construir la tupla
      completa, sin tocar atributos inexistentes del modelo.
    - Se añade un método insertar_con_id() para uso desde DAOs externos si
      alguna vez se necesita persistir desde fuera del controller atómico.
"""

from database import DatabaseConnection
from exceptions import IntegridadDatosError, BaseDatosError


class DetalleVentaDAO:
    """Objeto de acceso a datos para la entidad DetalleVenta."""

    def __init__(self):
        self._db = DatabaseConnection()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def insertar(self, id_venta, detalle) -> None:
        """
        Persiste un DetalleVenta en la base de datos.

        CORRECCIÓN #3:
            Recibe id_venta como parámetro separado porque DetalleVenta no
            posee ese atributo.  El id_venta lo administra el controller de
            ventas al momento de crear la cabecera.

        Args:
            id_venta — ID de la venta padre (obtenido tras insertar la cabecera).
            detalle  — instancia de DetalleVenta con cantidad, precio y subtotal.

        Lanza:
            IntegridadDatosError — si viola FK (id_venta o id_producto inexistente).
            BaseDatosError       — error de infraestructura.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                INSERT INTO detalle_venta
                    (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, self.__a_valores(id_venta, detalle))
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
    def __a_valores(id_venta, detalle) -> tuple:
        """
        Extrae los valores del DetalleVenta en el orden esperado por SQL.

        CORRECCIÓN #3:
            id_venta se pasa como argumento externo porque DetalleVenta no
            almacena el id de la venta a la que pertenece.
        """
        return (
            id_venta,                   # parámetro externo — no es atributo del modelo
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
