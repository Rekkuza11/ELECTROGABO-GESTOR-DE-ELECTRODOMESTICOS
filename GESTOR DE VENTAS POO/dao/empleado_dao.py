"""
DAO Empleado.
Aplica Singleton de DB, excepciones especializadas.

CORRECCIÓN #6 — Contraseñas en texto plano:
    insertar() llama a UTIL.security.hashear() sobre el password antes de
    escribirlo en la tabla `usuario`.

FASE 8 — Eliminación segura:
  - tiene_ventas(id): consulta si el empleado es referenciado en alguna venta
    antes de intentar el DELETE.  La vista _eliminar() llama a este método
    primero y muestra un mensaje comprensible en lugar de dejar que el motor
    lance un FK constraint error genérico e ininteligible.
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

    # ── Validación de dependencias FK (Fase 8) ────────────────────────────────

    def tiene_ventas(self, id_empleado) -> bool:
        """
        FASE 8 — Pre-validación de FK antes de eliminar.

        Consulta si el empleado (o usuario admin) está referenciado en alguna
        venta de la tabla `venta`.  La vista _eliminar() debe llamar a este
        método ANTES de invocar eliminar(), de modo que el usuario reciba un
        mensaje claro ("No se puede eliminar: el empleado tiene ventas
        registradas") en lugar del FK constraint error crudo del motor.

        Nota: la columna venta.id_empleado referencia usuario.id_usuario
        (tras la migración de Fase 3, Fix #1), por lo que esta consulta
        funciona tanto para empleados como para administradores.

        Retorna:
            True  — el empleado tiene ventas y NO puede eliminarse.
            False — el empleado no tiene ventas y puede eliminarse con seguridad.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM venta WHERE id_empleado = %s LIMIT 1",
                (id_empleado,)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            raise BaseDatosError(
                f"Error al verificar ventas del empleado {id_empleado}: {e}"
            ) from e
        finally:
            cursor.close()

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "Duplicate entry" in mensaje:
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error
