"""
Reporte de Clientes.
Responsabilidad: consultar y estructurar información de clientes desde la BD.
Aplica:
  - SRP: única responsabilidad — generar datos del reporte de clientes.
  - Método de clase: punto de entrada al reporte.
  - Métodos estáticos: cálculos puros sin estado de instancia.
  - Excepciones especializadas del dominio.

CORRECCIÓN #12 — Problemas de zona horaria en reportes:
    obtener_clientes_nuevos_mes() usaba CURDATE() y DATE_FORMAT(CURDATE(), ...)
    que operan en UTC en servidores cloud (TiDB/AWS RDS).  En Colombia
    (UTC-5) esto provoca conteos incorrectos entre las 7:00 p.m. y medianoche.

    Solución:
    - CURDATE()  → DATE(CONVERT_TZ(NOW(), '+00:00', '-05:00'))
    - DATE_FORMAT(CURDATE(), '%Y-%m-01') → primera-del-mes calculada en UTC-5
    - La constante _TZ_OFFSET centraliza el offset para futuros cambios.

CORRECCIÓN NE-6 (Fase 10) — f-string residual eliminado:
    Las constantes _COL_NOW/_COL_DATE/_COL_MONTH/_COL_YEAR se definían con
    f-strings que interpolaban _TZ_OFFSET.  Además, obtener_clientes_nuevos_mes()
    usaba otro f-string directamente en cursor.execute().

    Esto contradecía la corrección #11 ya aplicada en ProductoDAO,
    ReporteInventario y ReporteVentas, estableciendo un precedente peligroso.

    Solución (idéntica a reporte_ventas.py):
    - Constantes redefinidas como literales sin f-string.
    - obtener_clientes_nuevos_mes() construye el SQL por concatenación
      explícita de constantes de módulo, sin f-string en cursor.execute().
"""

from database import DatabaseConnection
from exceptions import BaseDatosError, ClienteNoEncontradoError
from UTIL.helpers import formatear_moneda, obtener_fecha_actual


# ── Constantes de zona horaria Colombia (UTC-5) ───────────────────────────────
# _TZ_OFFSET es la única fuente del offset; los demás son fragmentos SQL
# construidos sin f-string (CORRECCIÓN NE-6 / alineado con corrección #11).
_TZ_OFFSET = "-05:00"

# CORRECCIÓN NE-6: cadenas literales — sin f-string.
# Antes:  _COL_NOW = f"CONVERT_TZ(NOW(), '+00:00', '{_TZ_OFFSET}')"
#         _COL_DATE = f"DATE({_COL_NOW})"   … etc.
# Ahora:  literales con el offset embebido explícitamente.
_COL_NOW   = "CONVERT_TZ(NOW(), '+00:00', '-05:00')"
_COL_DATE  = "DATE(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
_COL_MONTH = "MONTH(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
_COL_YEAR  = "YEAR(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"


class ReporteClientes:
    """
    Genera reportes sobre los clientes y su comportamiento de compra.

    Atributos de clase:
        _tabla (protegido) — tabla principal.
    """

    _tabla: str = "cliente"

    def __init__(self):
        self._db = DatabaseConnection()

    # ── Método de clase (punto de entrada recomendado) ────────────────────────

    @classmethod
    def generar(cls) -> "ReporteClientes":
        """Fábrica: crea e imprime el reporte completo de clientes."""
        reporte = cls()
        reporte.mostrar_resumen()
        return reporte

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def obtener_todos_los_clientes(self) -> list:
        """
        Retorna todos los clientes registrados con su información básica.
        Cada fila: (id_cliente, nombre, telefono, direccion)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT id_cliente, nombre, telefono, direccion
                FROM cliente
                ORDER BY nombre ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener clientes: {e}") from e
        finally:
            cursor.close()

    def obtener_total_clientes(self) -> int:
        """Retorna el número total de clientes registrados."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM cliente")
            resultado = cursor.fetchone()
            return int(resultado[0]) if resultado else 0
        except Exception as e:
            raise BaseDatosError(f"Error al contar clientes: {e}") from e
        finally:
            cursor.close()

    def obtener_clientes_con_compras(self) -> list:
        """
        Retorna clientes que han realizado al menos una compra,
        junto con su historial resumido.
        Cada fila: (id_cliente, nombre, total_compras, monto_total_gastado)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    c.id_cliente,
                    c.nombre,
                    COUNT(v.id_venta)         AS total_compras,
                    COALESCE(SUM(v.total), 0) AS monto_total_gastado
                FROM cliente c
                JOIN venta v ON c.id_cliente = v.id_cliente
                GROUP BY c.id_cliente, c.nombre
                ORDER BY monto_total_gastado DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener clientes con compras: {e}") from e
        finally:
            cursor.close()

    def obtener_clientes_sin_compras(self) -> list:
        """
        Retorna clientes registrados que nunca han realizado una compra.
        Útil para campañas de reactivación.
        Cada fila: (id_cliente, nombre, telefono)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id_cliente, c.nombre, c.telefono
                FROM cliente c
                LEFT JOIN venta v ON c.id_cliente = v.id_cliente
                WHERE v.id_venta IS NULL
                ORDER BY c.nombre ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener clientes sin compras: {e}") from e
        finally:
            cursor.close()

    def obtener_top_clientes(self, limite: int = 5) -> list:
        """
        Clientes que más han gastado en el sistema.
        Retorna: (id_cliente, nombre, telefono, total_compras, monto_total)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    c.id_cliente,
                    c.nombre,
                    c.telefono,
                    COUNT(v.id_venta)          AS total_compras,
                    COALESCE(SUM(v.total), 0)  AS monto_total
                FROM cliente c
                JOIN venta v ON c.id_cliente = v.id_cliente
                GROUP BY c.id_cliente, c.nombre, c.telefono
                ORDER BY monto_total DESC
                LIMIT %s
            """, (limite,))
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener top clientes: {e}") from e
        finally:
            cursor.close()

    def obtener_historial_cliente(self, id_cliente) -> list:
        """
        Retorna el historial completo de compras de un cliente específico.
        Lanza ClienteNoEncontradoError si el cliente no existe.
        Cada fila: (id_venta, fecha, total, nombre_empleado)
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

            cursor.execute("""
                SELECT
                    v.id_venta,
                    v.fecha,
                    v.total,
                    COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)')) AS empleado
                FROM venta v
                JOIN  usuario  u ON v.id_empleado = u.id_usuario
                LEFT JOIN empleado e ON v.id_empleado = e.id_empleado
                WHERE v.id_cliente = %s
                ORDER BY v.fecha DESC
            """, (id_cliente,))
            return cursor.fetchall()
        except ClienteNoEncontradoError:
            raise
        except Exception as e:
            raise BaseDatosError(
                f"Error al obtener historial del cliente {id_cliente}: {e}"
            ) from e
        finally:
            cursor.close()

    def obtener_gasto_promedio_por_cliente(self) -> float:
        """
        Calcula el gasto promedio por cliente (entre los que han comprado).
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(AVG(monto_cliente), 0)
                FROM (
                    SELECT SUM(total) AS monto_cliente
                    FROM venta
                    GROUP BY id_cliente
                ) AS sub
            """)
            resultado = cursor.fetchone()
            return round(float(resultado[0]), 2) if resultado else 0.0
        except Exception as e:
            raise BaseDatosError(f"Error al calcular gasto promedio: {e}") from e
        finally:
            cursor.close()

    def obtener_clientes_nuevos_mes(self) -> int:
        """
        Cuenta cuántos clientes hicieron su primera compra en el mes actual.

        CORRECCIÓN #12 — Zona horaria Colombia:
            Usa CONVERT_TZ() para trabajar en UTC-5 (Colombia) en lugar de
            CURDATE() que opera en UTC en servidores cloud.

        CORRECCIÓN NE-6 (Fase 10) — Sin f-string en cursor.execute():
            La versión anterior construía el SQL con un f-string que
            interpolaba _COL_YEAR, _COL_MONTH y _TZ_OFFSET.  Ahora el SQL
            se construye por concatenación explícita de constantes de módulo,
            sin ningún f-string en el argumento de cursor.execute().
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # CORRECCIÓN NE-6: concatenación de constantes — sin f-string.
            # _COL_YEAR  = "YEAR(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
            # _COL_MONTH = "MONTH(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
            sql = (
                "SELECT COUNT(DISTINCT id_cliente) "
                "FROM venta "
                "WHERE " + _COL_YEAR  + " = YEAR(CONVERT_TZ(fecha, '+00:00', '-05:00'))"
                "  AND " + _COL_MONTH + " = MONTH(CONVERT_TZ(fecha, '+00:00', '-05:00'))"
                "  AND id_cliente NOT IN ("
                "        SELECT id_cliente"
                "        FROM venta"
                "        WHERE CONVERT_TZ(fecha, '+00:00', '-05:00')"
                "              < DATE_FORMAT("
                "                    CONVERT_TZ(NOW(), '+00:00', '-05:00'),"
                "                    '%Y-%m-01'"
                "                )"
                "  )"
            )
            cursor.execute(sql)
            resultado = cursor.fetchone()
            return int(resultado[0]) if resultado else 0
        except Exception as e:
            raise BaseDatosError(f"Error al obtener clientes nuevos del mes: {e}") from e
        finally:
            cursor.close()

    def mostrar_resumen(self) -> None:
        """Imprime en consola un resumen ejecutivo del reporte de clientes."""
        total_clientes = self.obtener_total_clientes()
        sin_compras    = self.obtener_clientes_sin_compras()
        gasto_promedio = self.obtener_gasto_promedio_por_cliente()
        nuevos_mes     = self.obtener_clientes_nuevos_mes()
        top_clientes   = self.obtener_top_clientes(5)

        clientes_activos = total_clientes - len(sin_compras)
        tasa_actividad   = self.calcular_tasa_actividad(total_clientes, clientes_activos)

        print("\n" + "═" * 50)
        print("      REPORTE DE CLIENTES — ElectroGabo")
        print("═" * 50)
        print(f"  Fecha de generación   : {obtener_fecha_actual()}")
        print(f"  Total clientes        : {total_clientes}")
        print(f"  Clientes activos      : {clientes_activos}  ({tasa_actividad}%)")
        print(f"  Clientes sin compras  : {len(sin_compras)}")
        print(f"  Nuevos este mes       : {nuevos_mes}")
        print(f"  Gasto promedio        : {formatear_moneda(gasto_promedio)}")

        print("\n  — Top 5 mejores clientes —")
        if top_clientes:
            for i, (id_c, nombre, telefono, compras, monto) in enumerate(top_clientes, 1):
                print(f"  {i}. {nombre} | Tel: {telefono} | "
                      f"{compras} compras | {formatear_moneda(float(monto))}")
        else:
            print("  Sin datos aún.")

        if sin_compras:
            print(f"\n  — Clientes sin actividad ({len(sin_compras)}) —")
            for id_c, nombre, telefono in sin_compras:
                print(f"  • [{id_c}] {nombre} | Tel: {telefono}")

        print("═" * 50 + "\n")

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def calcular_tasa_actividad(total: int, activos: int) -> float:
        """
        Método estático: porcentaje de clientes que han realizado al menos
        una compra respecto al total registrado.
        """
        if total == 0:
            return 0.0
        return round((activos / total) * 100, 2)

    @staticmethod
    def clasificar_cliente(monto_total: float) -> str:
        """
        Método estático: segmenta al cliente según su gasto histórico.
        Retorna: 'VIP', 'FRECUENTE', 'OCASIONAL' o 'NUEVO'.
        """
        if monto_total >= 1_000_000:
            return "VIP"
        if monto_total >= 300_000:
            return "FRECUENTE"
        if monto_total > 0:
            return "OCASIONAL"
        return "NUEVO"

    @staticmethod
    def formatear_fila_consola(id_c, nombre, telefono, compras, monto) -> str:
        """Método estático: formatea una fila de cliente para consola."""
        return (
            f"  [{id_c}] {nombre} | Tel: {telefono} | "
            f"Compras: {compras} | Total: {formatear_moneda(float(monto))}"
        )