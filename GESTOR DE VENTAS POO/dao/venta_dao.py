"""
DAO Venta.
Aplica Singleton de DB, excepciones especializadas.
"""

from database import DatabaseConnection
from models.venta import Venta
from exceptions import VentaNoEncontradaError, IntegridadDatosError, BaseDatosError


class VentaDAO:
    """Objeto de acceso a datos para la entidad Venta."""

    def __init__(self):
        self._db = DatabaseConnection()

    def insertar(self, venta: Venta) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                INSERT INTO venta (id_cliente, id_empleado, fecha, total)
                VALUES (%s, %s, %s, %s)
            """, (venta.id_cliente, venta.id_empleado, venta.fecha, venta.total))
            conexion.commit()
            venta.id_venta = cursor.lastrowid
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, "insertar venta")
        finally:
            cursor.close()

    def obtener_todos(self) -> list:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT * FROM venta")
            return cursor.fetchall()
        except Exception as e:
            self.__manejar_error(e, "obtener todas las ventas")
        finally:
            cursor.close()

    def obtener_completo(self) -> list:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT v.id_venta, v.fecha, v.total,
                       c.nombre AS cliente,
                       e.nombre AS empleado
                FROM venta v
                JOIN cliente c ON v.id_cliente = c.id_cliente
                JOIN empleado e ON v.id_empleado = e.id_empleado
            """)
            return cursor.fetchall()
        except Exception as e:
            self.__manejar_error(e, "obtener ventas completas")
        finally:
            cursor.close()

    def eliminar(self, id_venta) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("DELETE FROM venta WHERE id_venta=%s", (id_venta,))
            if cursor.rowcount == 0:
                raise VentaNoEncontradaError(id_venta)
            conexion.commit()
        except VentaNoEncontradaError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar venta {id_venta}")
        finally:
            cursor.close()

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "foreign key" in mensaje.lower():
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error