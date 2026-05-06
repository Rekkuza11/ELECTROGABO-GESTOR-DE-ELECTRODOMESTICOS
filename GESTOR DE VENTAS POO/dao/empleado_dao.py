"""
DAO Empleado.
Aplica Singleton de DB, excepciones especializadas.
"""

from database import DatabaseConnection
from models.empleado import Empleado
from exceptions import IntegridadDatosError, BaseDatosError, ValidacionError


class EmpleadoDAO:
    """Objeto de acceso a datos para la entidad Empleado."""

    def __init__(self):
        self._db = DatabaseConnection()

    def insertar(self, empleado: Empleado) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuario (id_usuario, password_hash, tipo) VALUES (%s, %s, %s)",
                (empleado.id_usuario, empleado.password, "empleado")
            )
            cursor.execute(
                "INSERT INTO empleado (id_empleado, nombre, rol) VALUES (%s, %s, %s)",
                (empleado.id_usuario, empleado.nombre, empleado.rol)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, "insertar empleado")
        finally:
            cursor.close()

    def obtener_todos(self) -> list:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT e.id_empleado, e.nombre, e.rol, u.password_hash
                FROM empleado e
                JOIN usuario u ON e.id_empleado = u.id_usuario
            """)
            return [Empleado.desde_fila_bd(fila) for fila in cursor.fetchall()]
        except Exception as e:
            self.__manejar_error(e, "obtener todos los empleados")
        finally:
            cursor.close()

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "Duplicate entry" in mensaje:
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error