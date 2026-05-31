"""
Módulo de conexión a la base de datos.
Patrón Singleton: garantiza una única instancia de la clase de conexión
durante todo el ciclo de vida de la aplicación.
Principio SRP: única responsabilidad — gestionar la conexión.

CORRECCIÓN #5 — Credenciales hardcodeadas:
    Las credenciales de producción ya no viven en el código fuente.
    Se cargan desde un archivo .env ubicado en la raíz del proyecto
    usando python-dotenv.  El .env debe agregarse a .gitignore para
    que nunca se suba al repositorio.

    Jerarquía de búsqueda del .env:
        1. Ruta explícita pasada a configurar().
        2. Variable de entorno DATABASE_ENV_FILE.
        3. Archivo .env en el directorio del proyecto (raíz).

    Si falta alguna variable obligatoria se lanza ConexionBaseDatosError
    con un mensaje claro antes de intentar cualquier conexión.
"""

import os
import threading
import mysql.connector
from mysql.connector import Error as MySQLError
from pathlib import Path

from exceptions import ConexionBaseDatosError


def _cargar_config_desde_env(env_path: str | None = None) -> dict:
    """
    Lee las credenciales desde el archivo .env y devuelve el dict de config.

    Variables requeridas en .env:
        DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT, DB_SSL_CA
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        raise ConexionBaseDatosError(
            "python-dotenv no está instalado. Ejecuta: pip install python-dotenv"
        )

    # Determinar la ruta del .env
    if env_path:
        dotenv_file = Path(env_path)
    else:
        dotenv_file = Path(
            os.environ.get("DATABASE_ENV_FILE", "")
            or Path(__file__).parent / ".env"
        )

    if not dotenv_file.exists():
        raise ConexionBaseDatosError(
            f"Archivo de configuración no encontrado: {dotenv_file}. "
            "Crea un archivo .env con las variables DB_USER, DB_PASSWORD, "
            "DB_HOST, DB_NAME, DB_PORT y DB_SSL_CA."
        )

    load_dotenv(dotenv_file, override=False)  # no sobreescribe variables ya en el entorno

    variables_requeridas = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME", "DB_PORT"]
    faltantes = [v for v in variables_requeridas if not os.environ.get(v)]
    if faltantes:
        raise ConexionBaseDatosError(
            f"Faltan variables de entorno en {dotenv_file}: {faltantes}"
        )

    config: dict = {
        "user":     os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "host":     os.environ["DB_HOST"],
        "database": os.environ["DB_NAME"],
        "port":     int(os.environ["DB_PORT"]),
    }

    ssl_ca = os.environ.get("DB_SSL_CA", "")
    if ssl_ca:
        config["ssl_ca"]              = ssl_ca
        config["ssl_verify_cert"]     = True
        config["ssl_verify_identity"] = True

    return config


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
    _config: dict | None = None          # se inicializa al primer uso

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
        self.__conexion = None

    # ── Carga diferida de configuración ─────────────────────────────────────

    @classmethod
    def _obtener_config(cls) -> dict:
        """
        Carga la configuración desde .env la primera vez que se necesita.
        Esto permite que configurar() se llame antes de la primera conexión.
        """
        if cls._config is None:
            cls._config = _cargar_config_desde_env()
        return cls._config

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
        Método de clase: permite reconfigurar los parámetros en tiempo de
        ejecución (útil en tests o múltiples entornos).
        Cuando se llama, las credenciales se pasan directamente sin leer el .env.
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
    def configurar_desde_env(cls, env_path: str) -> None:
        """
        Método de clase: carga la configuración explícitamente desde la ruta
        de .env indicada.  Útil en entornos CI/CD o testing.
        """
        with cls._lock:
            cls._config = _cargar_config_desde_env(env_path)
            cls._instancia = None

    @classmethod
    def resetear(cls) -> None:
        """Método de clase: destruye la instancia actual (útil en tests)."""
        with cls._lock:
            if cls._instancia is not None:
                cls._instancia.__cerrar_seguro()
            cls._instancia = None
            cls._config    = None   # también limpia la config cacheada

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
            config = self._obtener_config()
            if self.__conexion is None or not self.__conexion.is_connected():
                self.__conexion = mysql.connector.connect(**config)
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
        try:
            host = self._obtener_config().get("host", "?")
        except Exception:
            host = "no configurado"
        conectado = (
            self.__conexion is not None and self.__conexion.is_connected()
        )
        return f"<DatabaseConnection host={host} connected={conectado}>"


# ── Función de conveniencia (retrocompatibilidad con código existente) ────────

def obtener_conexion():
    """Obtiene una conexión a través del Singleton."""
    return DatabaseConnection().obtener_conexion()
