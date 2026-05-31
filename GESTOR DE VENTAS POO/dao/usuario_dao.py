"""
DAO Usuario.
Aplica:
  - Singleton DatabaseConnection.
  - Encapsulamiento: método privado de manejo de errores.
  - Excepciones especializadas: IntegridadDatosError, BaseDatosError.
  - Principio SRP: sólo gestiona la tabla `usuario`, sin lógica de negocio.

CORRECCIÓN #6 — Contraseñas en texto plano:
    insertar() y actualizar_password() llaman a UTIL.security.hashear()
    antes de escribir la contraseña en la BD.  De esta manera el campo
    password_hash nunca almacena texto plano.
"""

from database import DatabaseConnection
from exceptions import (
    IntegridadDatosError,
    BaseDatosError,
    ValidacionError,
)
from UTIL.security import hashear


class UsuarioDAO:
    """Objeto de acceso a datos para la tabla `usuario`."""

    def __init__(self):
        self._db = DatabaseConnection()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def insertar(self, usuario) -> None:
        """
        Inserta un registro en la tabla usuario.
        CORRECCIÓN #6: almacena el hash de la contraseña, no el texto plano.
        Lanza IntegridadDatosError si el id ya existe (Duplicate entry).
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            pwd_hash = hashear(usuario.password)   # ← CORRECCIÓN #6
            cursor.execute(
                "INSERT INTO usuario (id_usuario, password_hash, tipo) VALUES (%s, %s, %s)",
                (usuario.id_usuario, pwd_hash, usuario.tipo)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"insertar usuario {usuario.id_usuario}")
        finally:
            cursor.close()

    def obtener_todos(self) -> list:
        """Retorna todas las filas de la tabla usuario."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT * FROM usuario")
            return cursor.fetchall()
        except Exception as e:
            self.__manejar_error(e, "obtener todos los usuarios")
        finally:
            cursor.close()

    def obtener_por_id(self, id_usuario) -> tuple | None:
        """
        Busca un usuario por su ID.
        Retorna la fila como tupla, o None si no existe.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT * FROM usuario WHERE id_usuario = %s",
                (id_usuario,)
            )
            return cursor.fetchone()
        except Exception as e:
            self.__manejar_error(e, f"obtener usuario {id_usuario}")
        finally:
            cursor.close()

    def actualizar_password(self, id_usuario, nueva_password: str) -> None:
        """
        Actualiza únicamente el hash de contraseña de un usuario.
        CORRECCIÓN #6: hashea la nueva contraseña antes de guardarla.
        """
        if not nueva_password or len(nueva_password.strip()) < 4:
            raise ValidacionError("password", "debe tener al menos 4 caracteres")
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            pwd_hash = hashear(nueva_password)     # ← CORRECCIÓN #6
            cursor.execute(
                "UPDATE usuario SET password_hash = %s WHERE id_usuario = %s",
                (pwd_hash, id_usuario)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"actualizar password de {id_usuario}")
        finally:
            cursor.close()

    def eliminar(self, id_usuario) -> None:
        """
        Elimina el usuario y, por CASCADE en BD, sus registros dependientes.
        Lanza IntegridadDatosError si hay restricciones que lo impiden.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario = %s",
                (id_usuario,)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar usuario {id_usuario}")
        finally:
            cursor.close()

    # ── Privados de ayuda ─────────────────────────────────────────────────────

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "Duplicate entry" in mensaje:
            raise IntegridadDatosError(
                f"Ya existe un usuario con ese ID: {mensaje}"
            ) from error
        if "foreign key" in mensaje.lower():
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error
