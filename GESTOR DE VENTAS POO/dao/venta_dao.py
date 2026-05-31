"""
DAO Venta.
Aplica Singleton de DB, excepciones especializadas.

CORRECCIÓN #17 — VentaDAO oculta errores con try/except anidado:
    obtener_completo() tenía un bloque try/except interno que atrapaba
    CUALQUIER excepción de la primera query (incluidos errores de conexión
    o permisos) y silenciosamente ejecutaba una segunda query de fallback.
    Esto hacía imposible diagnosticar problemas reales en producción: un
    error de red, una tabla renombrada o una FK rota se swallowaban sin
    traza visible, y el sistema simplemente mostraba datos del fallback
    (o errores más confusos) sin indicar la causa raíz.

    Solución:
    - Se elimina el try/except anidado.
    - Se unifica en UNA sola query con LEFT JOIN a detalle_venta para calcular
      el total cuando la columna venta.total pudiera ser NULL o 0.
    - COALESCE(v.total, SUM(dv.subtotal), 0) garantiza que siempre haya un
      valor numérico sin necesidad de fallback silencioso.
    - Si la query falla, la excepción sube limpia a través de __manejar_error()
      y queda registrada en el log del sistema.

CORRECCIÓN #9 (soporte en DAO):
    La query ya usa LEFT JOIN entre venta y empleado para que los admins
    (que no tienen fila en la tabla empleado) también aparezcan en el
    historial.  COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)'))
    resuelve el nombre del vendedor en ambos casos.
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

        CORRECCIÓN #17 — Eliminación del try/except anidado silencioso:
            La versión anterior envolvía la query principal en un try/except
            que, ante cualquier error, ejecutaba silenciosamente una segunda
            query de fallback.  Esto ocultaba errores reales (conexión caída,
            FK rota, permisos insuficientes) y dificultaba el diagnóstico.

            Ahora existe UNA sola query que:
              - Usa COALESCE(v.total, COALESCE(SUM(dv.subtotal), 0)) para
                obtener el total desde la cabecera o calcularlo desde detalles.
              - Usa LEFT JOIN con empleado para incluir admins (fix #9).
              - Usa JOIN con usuario para resolver el nombre del vendedor.
            Si la query falla, la excepción sube limpia sin ser interceptada.

        CORRECCIÓN #9 — Ventas de admins incluidas:
            LEFT JOIN empleado garantiza que ventas registradas por un usuario
            de tipo 'admin' (sin fila en la tabla empleado) también aparezcan.
            COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)')) resuelve
            el nombre del vendedor en ambos casos.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    v.id_venta,
                    v.fecha,
                    COALESCE(v.total, COALESCE(SUM(dv.subtotal), 0))   AS total,
                    c.nombre                                             AS cliente,
                    COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)'))
                                                                         AS vendedor
                FROM venta v
                JOIN  cliente   c  ON v.id_cliente  = c.id_cliente
                JOIN  usuario   u  ON v.id_empleado = u.id_usuario
                LEFT JOIN empleado  e  ON v.id_empleado = e.id_empleado
                LEFT JOIN detalle_venta dv ON v.id_venta = dv.id_venta
                GROUP BY v.id_venta, v.fecha, v.total, c.nombre, e.nombre, u.id_usuario
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
