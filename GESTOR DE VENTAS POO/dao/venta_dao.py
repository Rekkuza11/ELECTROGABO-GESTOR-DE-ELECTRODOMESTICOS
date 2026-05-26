"""
DAO Venta.
Aplica Singleton de DB, excepciones especializadas.

CORRECCIÓN:
- obtener_completo usa LEFT JOIN con empleado y LEFT JOIN con usuario
  para que las ventas registradas por un administrador (que no tiene fila
  en la tabla `empleado`) también aparezcan en el historial.
  El nombre del vendedor se resuelve con COALESCE: primero intenta el
  nombre del empleado, luego el id_usuario del admin.
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
        """
        Retorna ventas con datos de cliente y vendedor.

        Usa LEFT JOIN con empleado y LEFT JOIN con usuario para cubrir
        dos casos:
          - Vendedor es un empleado  → muestra e.nombre
          - Vendedor es un admin     → no tiene fila en `empleado`, muestra
                                       u.id_usuario como identificador

        COALESCE elige el primer valor no nulo: nombre del empleado o, si
        no existe, el id del usuario (admin).
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            try:
                cursor.execute("""
                    SELECT
                        v.id_venta,
                        v.fecha,
                        COALESCE(v.total, 0)                        AS total,
                        c.nombre                                     AS cliente,
                        COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)'))
                                                                     AS vendedor
                    FROM venta v
                    JOIN  cliente  c ON v.id_cliente  = c.id_cliente
                    JOIN  usuario  u ON v.id_empleado = u.id_usuario
                    LEFT  JOIN empleado e ON v.id_empleado = e.id_empleado
                    ORDER BY v.id_venta DESC
                """)
                return cursor.fetchall()
            except Exception:
                # Fallback: calcular total desde detalle_venta
                cursor.execute("""
                    SELECT
                        v.id_venta,
                        v.fecha,
                        COALESCE(SUM(dv.subtotal), 0)               AS total,
                        c.nombre                                     AS cliente,
                        COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)'))
                                                                     AS vendedor
                    FROM venta v
                    JOIN  cliente  c  ON v.id_cliente  = c.id_cliente
                    JOIN  usuario  u  ON v.id_empleado = u.id_usuario
                    LEFT  JOIN empleado    e  ON v.id_empleado  = e.id_empleado
                    LEFT  JOIN detalle_venta dv ON v.id_venta   = dv.id_venta
                    GROUP BY v.id_venta, v.fecha, c.nombre, e.nombre, u.id_usuario
                    ORDER BY v.id_venta DESC
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
