"""
Controller: Autenticación.
Responsabilidad: verificar credenciales contra la BD y determinar el tipo
de usuario que intenta iniciar sesión.
Aplica SRP — sólo gestiona el proceso de login/logout.

CORRECCIÓN #6 — Contraseñas en texto plano:
    El método login() ya no compara password_hash == password en texto plano.
    Ahora usa UTIL.security.verificar() que hace la comparación contra el
    hash HMAC-SHA256 almacenado.  Esto garantiza que aunque la BD sea
    comprometida, las contraseñas originales no queden expuestas.
"""

from database import DatabaseConnection
from exceptions import CredencialesInvalidasError, BaseDatosError
from UTIL.security import verificar


class AuthController:
    """
    Controla el acceso al sistema.

    Tipos de usuario soportados: 'admin', 'empleado', 'cliente'.
    """

    def __init__(self):
        self._db = DatabaseConnection()
        self._sesion_activa: dict | None = None

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self, id_usuario: str, password: str) -> dict:
        """
        Verifica las credenciales del usuario en la tabla `usuario`.

        CORRECCIÓN #6:
            La contraseña ingresada se hashea antes de comparar, usando
            UTIL.security.verificar() con hmac.compare_digest para evitar
            ataques de timing.

        Retorna:
            dict con claves 'id', 'tipo' si las credenciales son válidas.

        Lanza:
            CredencialesInvalidasError — usuario no existe o contraseña incorrecta.
            BaseDatosError             — error de infraestructura.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT id_usuario, password_hash, tipo "
                "FROM usuario WHERE id_usuario = %s",
                (id_usuario,),
            )
            fila = cursor.fetchone()
            if not fila:
                raise CredencialesInvalidasError(id_usuario)

            id_u, pwd_hash, tipo = fila

            # CORRECCIÓN #6: verificar usando hash, no comparación directa
            if not verificar(password, pwd_hash):
                raise CredencialesInvalidasError(id_usuario)

            self._sesion_activa = {"id": id_u, "tipo": tipo}
            return self._sesion_activa

        except CredencialesInvalidasError:
            raise
        except Exception as e:
            raise BaseDatosError(f"Error al autenticar: {e}") from e
        finally:
            cursor.close()

    # ── Logout ────────────────────────────────────────────────────────────────

    def logout(self) -> None:
        """Cierra la sesión actual."""
        self._sesion_activa = None

    # ── Consultas de sesión ───────────────────────────────────────────────────

    @property
    def sesion(self) -> dict | None:
        """Retorna el dict de sesión activa, o None si no hay sesión."""
        return self._sesion_activa

    def hay_sesion(self) -> bool:
        return self._sesion_activa is not None

    def es_admin(self) -> bool:
        return (
            self._sesion_activa is not None
            and self._sesion_activa.get("tipo") == "admin"
        )

    def es_empleado(self) -> bool:
        return (
            self._sesion_activa is not None
            and self._sesion_activa.get("tipo") == "empleado"
        )
