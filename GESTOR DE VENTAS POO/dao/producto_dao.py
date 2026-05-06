"""
DAO Producto.
Aplica:
  - Usa el Singleton DatabaseConnection.
  - Encapsulamiento: métodos de ayuda privados.
  - Método de clase: fábrica de Producto desde fila de BD.
  - Excepciones especializadas: ProductoNoEncontradoError, IntegridadDatosError.
  - Principio DIP: depende de la abstracción (DatabaseConnection), no de mysql directo.
"""

from database import DatabaseConnection
from models.producto import Producto
from exceptions import (
    ProductoNoEncontradoError,
    IntegridadDatosError,
    BaseDatosError,
)


class ProductoDAO:
    """Objeto de acceso a datos para la entidad Producto."""

    # ── Miembro protegido de clase ────────────────────────────────────────────
    _tabla: str = "producto"

    def __init__(self):
        self._db = DatabaseConnection()   # protegido: accesible en subclases

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def insertar(self, producto: Producto) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                INSERT INTO producto (nombre, marca, precio_compra, precio_venta, stock)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, self.__a_valores(producto))
            conexion.commit()
            producto.id_producto = cursor.lastrowid
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, "insertar producto")
        finally:
            cursor.close()

    def obtener_todos(self) -> list:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(f"SELECT * FROM {self._tabla}")
            return [Producto.desde_fila_bd(fila) for fila in cursor.fetchall()]
        except Exception as e:
            self.__manejar_error(e, "obtener todos los productos")
        finally:
            cursor.close()

    def obtener_por_id(self, id_producto) -> Producto:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                f"SELECT * FROM {self._tabla} WHERE id_producto = %s",
                (id_producto,)
            )
            fila = cursor.fetchone()
            if not fila:
                raise ProductoNoEncontradoError(id_producto)
            return Producto.desde_fila_bd(fila)
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            self.__manejar_error(e, f"obtener producto {id_producto}")
        finally:
            cursor.close()

    def actualizar(self, producto: Producto) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                UPDATE producto
                SET nombre=%s, marca=%s, precio_compra=%s, precio_venta=%s, stock=%s
                WHERE id_producto=%s
            """
            valores = self.__a_valores(producto) + (producto.id_producto,)
            cursor.execute(sql, valores)
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(producto.id_producto)
            conexion.commit()
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"actualizar producto {producto.id_producto}")
        finally:
            cursor.close()

    def eliminar(self, id_producto) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                f"DELETE FROM {self._tabla} WHERE id_producto=%s",
                (id_producto,)
            )
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(id_producto)
            conexion.commit()
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar producto {id_producto}")
        finally:
            cursor.close()

    def actualizar_stock(self, id_producto, cantidad: int) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "UPDATE producto SET stock = stock - %s WHERE id_producto = %s",
                (cantidad, id_producto)
            )
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(id_producto)
            conexion.commit()
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"actualizar stock {id_producto}")
        finally:
            cursor.close()

    # ── Métodos privados de ayuda ─────────────────────────────────────────────

    @staticmethod
    def __a_valores(producto: Producto) -> tuple:
        """Extrae los valores del objeto en orden para los parámetros SQL."""
        return (
            producto.nombre,
            producto.marca,
            producto.precio_compra,
            producto.precio_venta,
            producto.stock,
        )

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        """
        Traduce errores de infraestructura a excepciones de dominio.
        Lanza BaseDatosError o IntegridadDatosError según el tipo de error.
        """
        mensaje = str(error)
        if "Duplicate entry" in mensaje or "foreign key" in mensaje.lower():
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error