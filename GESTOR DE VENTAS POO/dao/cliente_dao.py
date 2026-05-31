"""
DAO Cliente.
Aplica Singleton de DB, excepciones especializadas y método de clase fábrica.

CORRECCIÓN #6 — Contraseñas en texto plano:
    insertar() llama a UTIL.security.hashear() sobre el password antes de
    escribirlo en la tabla `usuario`.  Así nunca se almacena texto plano.
"""

from database import DatabaseConnection
from models.cliente import Cliente
from exceptions import (
    ClienteNoEncontradoError,
    ClienteDuplicadoError,
    IntegridadDatosError,
    BaseDatosError,
)
from UTIL.security import hashear


class ClienteDAO:
    """Objeto de acceso a datos para la entidad Cliente."""

    def __init__(self):
        self._db = DatabaseConnection()

    def insertar(self, cliente: Cliente) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            pwd_hash = hashear(cliente.password)   # ← CORRECCIÓN #6
            cursor.execute(
                "INSERT INTO usuario (id_usuario, password_hash, tipo) VALUES (%s, %s, %s)",
                (cliente.id_usuario, pwd_hash, "cliente")
            )
            cursor.execute(
                "INSERT INTO cliente (id_cliente, nombre, telefono, direccion) VALUES (%s, %s, %s, %s)",
                (cliente.id_usuario, cliente.nombre, cliente.telefono, cliente.direccion)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, "insertar cliente")
        finally:
            cursor.close()

    def obtener_todos(self) -> list:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id_cliente, c.nombre, c.telefono, c.direccion, u.password_hash
                FROM cliente c
                JOIN usuario u ON c.id_cliente = u.id_usuario
            """)
            return [Cliente.desde_fila_bd(fila) for fila in cursor.fetchall()]
        except Exception as e:
            self.__manejar_error(e, "obtener todos los clientes")
        finally:
            cursor.close()

    def obtener_por_id(self, id_cliente) -> Cliente:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id_cliente, c.nombre, c.telefono, c.direccion, u.password_hash
                FROM cliente c
                JOIN usuario u ON c.id_cliente = u.id_usuario
                WHERE c.id_cliente = %s
            """, (id_cliente,))
            fila = cursor.fetchone()
            if not fila:
                raise ClienteNoEncontradoError(id_cliente)
            return Cliente.desde_fila_bd(fila)
        except ClienteNoEncontradoError:
            raise
        except Exception as e:
            self.__manejar_error(e, f"obtener cliente {id_cliente}")
        finally:
            cursor.close()

    def eliminar(self, id_cliente) -> None:
        """
        Elimina cliente correctamente:
        1. Primero borra la fila en 'cliente' (tabla hija)
        2. Luego borra la fila en 'usuario' (tabla padre)
        Esto evita errores de FK constraint.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_cliente FROM cliente WHERE id_cliente = %s",
                (id_cliente,)
            )
            if not cursor.fetchone():
                raise ClienteNoEncontradoError(id_cliente)

            cursor.execute(
                "DELETE FROM cliente WHERE id_cliente = %s",
                (id_cliente,)
            )
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario = %s",
                (id_cliente,)
            )
            conexion.commit()
        except ClienteNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar cliente {id_cliente}")
        finally:
            cursor.close()

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "Duplicate entry" in mensaje:
            raise ClienteDuplicadoError(mensaje) from error
        if "foreign key" in mensaje.lower():
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error
