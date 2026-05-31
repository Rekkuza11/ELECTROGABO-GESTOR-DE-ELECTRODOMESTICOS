"""
Módulo de conexión a la base de datos.
Patrón Singleton: garantiza una única instancia de la clase de conexión
durante todo el ciclo de vida de la aplicación.
Principio SRP: única responsabilidad — gestionar la conexión.
"""

import threading
import mysql.connector
from mysql.connector import Error as MySQLError

from exceptions import ConexionBaseDatosError


class DatabaseConnection:
    """
    Singleton thread-safe para la conexión a MySQL.

    Atributos de clase (estáticos):
        _instancia  — referencia a la única instancia (privado)
        _lock       — mutex para acceso concurrente seguro (privado)
        _config     — parámetros de conexión compartidos (protegido)
    """

    # ── Miembros estáticos de clase ──────────────────────────────────────────
    _instancia: "DatabaseConnection | None" = None
    _lock: threading.Lock = threading.Lock()

    _config: dict = {
        "user":     "2XTfztzfJARuHio.root",
        "password": "X1cF7w1hZSFemDJW",
        "host":     "gateway01.us-east-1.prod.aws.tidbcloud.com",
        "database": "base_datos_electrogabo",
        "port":     4000,
        "ssl_ca": r"certs\isrgrootx1.pem",
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }

    # ── Singleton ────────────────────────────────────────────────────────────

    def __new__(cls) -> "DatabaseConnection":
        """Garantiza una sola instancia (double-checked locking)."""
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
                    cls._instancia.__inicializar()
        return cls._instancia

    def __inicializar(self) -> None:
        """Inicialización interna — sólo se ejecuta una vez."""
        self.__conexion = None  # privado: sólo accesible desde esta clase

    # ── Métodos de clase (alternativos de construcción) ──────────────────────

    @classmethod
    def configurar(
        cls,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 3306,
    ) -> None:
        """
        Método de clase: permite reconfigurar los parámetros ANTES de
        obtener la primera instancia (útil en tests o múltiples entornos).
        """
        with cls._lock:
            cls._config = {
                "user":     user,
                "password": password,
                "host":     host,
                "database": database,
                "port":     port,
            }
            cls._instancia = None   # fuerza reconexión con nueva config

    @classmethod
    def resetear(cls) -> None:
        """Método de clase: destruye la instancia actual (útil en tests)."""
        with cls._lock:
            if cls._instancia is not None:
                cls._instancia.__cerrar_seguro()
            cls._instancia = None

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def ping(conexion) -> bool:
        """
        Método estático: verifica si una conexión sigue activa.
        No necesita estado de instancia ni de clase.
        """
        try:
            conexion.ping(reconnect=False, attempts=1, delay=0)
            return True
        except Exception:
            return False

    # ── Interfaz pública ─────────────────────────────────────────────────────

    def obtener_conexion(self):
        """
        Retorna una conexión activa. Si la existente está caída,
        intenta reconectar antes de lanzar excepción.
        """
        try:
            if self.__conexion is None or not self.__conexion.is_connected():
                self.__conexion = mysql.connector.connect(**self._config)
            return self.__conexion
        except MySQLError as e:
            raise ConexionBaseDatosError(str(e)) from e

    # ── Privados de instancia ────────────────────────────────────────────────

    def __cerrar_seguro(self) -> None:
        """Cierra la conexión sin propagar errores."""
        try:
            if self.__conexion and self.__conexion.is_connected():
                self.__conexion.close()
        except Exception:
            pass

    def __repr__(self) -> str:
        conectado = (
            self.__conexion is not None and self.__conexion.is_connected()
        )
        return f"<DatabaseConnection host={self._config['host']} connected={conectado}>"


# ── Función de conveniencia (retrocompatibilidad con código existente) ────────

def obtener_conexion():
    """Obtiene una conexión a través del Singleton."""
    return DatabaseConnection().obtener_conexion()