"""
DAO Empleado.
Aplica Singleton de DB, excepciones especializadas.

CORRECCIÓN #6 — Contraseñas en texto plano:
    insertar() llama a UTIL.security.hashear() sobre el password antes de
    escribirlo en la tabla `usuario`.
"""

from database import DatabaseConnection
from models.empleado import Empleado
from exceptions import IntegridadDatosError, BaseDatosError, ValidacionError
from UTIL.security import hashear


class EmpleadoDAO:
    """Objeto de acceso a datos para la entidad Empleado."""

    def __init__(self):
        self._db = DatabaseConnection()

    def insertar(self, empleado: Empleado) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            pwd_hash = hashear(empleado.password)   # ← CORRECCIÓN #6
            cursor.execute(
                "INSERT INTO usuario (id_usuario, password_hash, tipo) VALUES (%s, %s, %s)",
                (empleado.id_usuario, pwd_hash, "empleado")
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

    def eliminar(self, id_empleado) -> None:
        """
        Elimina empleado correctamente:
        1. Primero borra la fila en 'empleado' (tabla hija)
        2. Luego borra la fila en 'usuario' (tabla padre)
        Esto evita errores de FK constraint.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_empleado FROM empleado WHERE id_empleado = %s",
                (id_empleado,)
            )
            if not cursor.fetchone():
                raise BaseDatosError(f"Error en 'eliminar empleado': No existe el empleado {id_empleado}")

            cursor.execute(
                "DELETE FROM empleado WHERE id_empleado = %s",
                (id_empleado,)
            )
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario = %s",
                (id_empleado,)
            )
            conexion.commit()
        except BaseDatosError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar empleado {id_empleado}")
        finally:
            cursor.close()

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "Duplicate entry" in mensaje:
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error
