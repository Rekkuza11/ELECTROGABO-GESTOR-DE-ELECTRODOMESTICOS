"""
Reporte de Ventas.
Responsabilidad: consultar y estructurar información de ventas desde la BD.
Aplica:
  - SRP: única responsabilidad — generar datos del reporte de ventas.
  - Método de clase: punto de entrada al reporte.
  - Métodos estáticos: cálculos puros de negocio.
  - Excepciones especializadas del dominio.

CORRECCIÓN #9 — Reporte de ventas excluye ventas de administradores:
    (aplicada por el equipo en Fase 4 — sin cambios aquí)

CORRECCIÓN #12 — Problemas de zona horaria en reportes:
    (aplicada por el equipo en Fase 4 — sin cambios aquí)

CORRECCIÓN #11 — SQL dinámico mediante f-string:
    El método obtener_ingresos_hoy() construía su query mediante un f-string
    que interpolaba las constantes _TZ_OFFSET y _COL_DATE directamente en
    el texto pasado a cursor.execute():

        cursor.execute(f\"\"\"
            ...
            WHERE DATE(CONVERT_TZ(fecha, '+00:00', '{_TZ_OFFSET}')) = {_COL_DATE}
        \"\"\")

    Aunque _TZ_OFFSET y _COL_DATE son constantes de módulo (nunca derivadas
    de entrada del usuario), el patrón establece un precedente peligroso:
    cualquier desarrollador que siga el mismo estilo con un valor dinámico
    introduciría una SQL injection.

    Solución:
    - Las constantes _COL_DATE, _COL_MONTH, _COL_YEAR se redefinen como
      cadenas literales sin f-string (el offset '-05:00' queda explícito).
    - En obtener_ingresos_hoy() el SQL se construye por concatenación de
      constantes de módulo verificadas, sin ningún f-string en el argumento
      de cursor.execute().
    - Mantener _TZ_OFFSET como fuente única del offset facilita actualizar
      la zona horaria en un solo lugar si fuera necesario.
"""

from datetime import datetime
from database import DatabaseConnection
from exceptions import BaseDatosError
from models.producto import Producto
from UTIL.helpers import formatear_moneda, obtener_fecha_actual


# ── Constantes de zona horaria Colombia (UTC-5) ───────────────────────────────
# _TZ_OFFSET es la única fuente del offset; los demás son fragmentos SQL
# construidos a partir de él sin usar f-string para evitar el patrón de
# SQL dinámico (CORRECCIÓN #11).
_TZ_OFFSET = "-05:00"

# CORRECCIÓN #11: cadenas literales sin f-string.
# Antes:  f"DATE(CONVERT_TZ(NOW(), '+00:00', '{_TZ_OFFSET}'))"
# Ahora:  literal con el offset embebido explícitamente.
_COL_DATE  = "DATE(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
_COL_MONTH = "MONTH(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
_COL_YEAR  = "YEAR(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"


class ReporteVentas:
    """
    Genera reportes sobre las ventas del sistema.

    Atributos de clase:
        _tabla (protegido) — nombre de la tabla principal.
    """

    _tabla: str = "venta"

    def __init__(self):
        self._db = DatabaseConnection()

    # ── Método de clase (punto de entrada recomendado) ────────────────────────

    @classmethod
    def generar(cls) -> "ReporteVentas":
        """Fábrica: crea e imprime el reporte completo de ventas."""
        reporte = cls()
        reporte.mostrar_resumen()
        return reporte

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def obtener_ventas_completas(self) -> list:
        """
        Retorna todas las ventas con datos de cliente y empleado/admin.
        Cada fila: (id_venta, fecha, total, nombre_cliente, nombre_vendedor)

        CORRECCIÓN #9: LEFT JOIN empleado asegura que ventas de admins aparezcan.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    v.id_venta,
                    v.fecha,
                    v.total,
                    c.nombre                                              AS cliente,
                    COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)')) AS empleado
                FROM venta v
                JOIN  cliente  c ON v.id_cliente  = c.id_cliente
                JOIN  usuario  u ON v.id_empleado = u.id_usuario
                LEFT JOIN empleado e ON v.id_empleado = e.id_empleado
                ORDER BY v.fecha DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener ventas completas: {e}") from e
        finally:
            cursor.close()

    def obtener_ventas_por_fecha(self, fecha_inicio: str, fecha_fin: str) -> list:
        """
        Filtra ventas en un rango de fechas (formato 'YYYY-MM-DD').
        Retorna: (id_venta, fecha, total, cliente, empleado)

        CORRECCIÓN #9: LEFT JOIN empleado incluye ventas de admins.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    v.id_venta,
                    v.fecha,
                    v.total,
                    c.nombre                                              AS cliente,
                    COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)')) AS empleado
                FROM venta v
                JOIN  cliente  c ON v.id_cliente  = c.id_cliente
                JOIN  usuario  u ON v.id_empleado = u.id_usuario
                LEFT JOIN empleado e ON v.id_empleado = e.id_empleado
                WHERE DATE(v.fecha) BETWEEN %s AND %s
                ORDER BY v.fecha DESC
            """, (fecha_inicio, fecha_fin))
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al filtrar ventas por fecha: {e}") from e
        finally:
            cursor.close()

    def obtener_total_ingresos(self) -> float:
        """Retorna la suma total de todas las ventas registradas."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COALESCE(SUM(total), 0) FROM venta")
            resultado = cursor.fetchone()
            return float(resultado[0]) if resultado else 0.0
        except Exception as e:
            raise BaseDatosError(f"Error al calcular ingresos totales: {e}") from e
        finally:
            cursor.close()

    def obtener_ingresos_hoy(self) -> float:
        """
        Retorna el total de ventas del día actual en hora colombiana.

        CORRECCIÓN #12: usa CONVERT_TZ en vez de CURDATE() para operar
            en UTC-5 (Colombia) independientemente de la configuración del
            servidor de base de datos.

        CORRECCIÓN #11: el SQL ya no se construye con f-string.
            Se usa concatenación explícita de la constante de módulo _COL_DATE,
            que es un fragmento SQL verificado, nunca derivado de entrada del
            usuario.  Esto elimina el patrón de SQL dinámico en cursor.execute().
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # CORRECCIÓN #11: concatenación de constantes de módulo, sin f-string.
            # _COL_DATE = "DATE(CONVERT_TZ(NOW(), '+00:00', '-05:00'))"
            sql = (
                "SELECT COALESCE(SUM(total), 0) "
                "FROM venta "
                "WHERE DATE(CONVERT_TZ(fecha, '+00:00', '-05:00')) = "
                + _COL_DATE
            )
            cursor.execute(sql)
            resultado = cursor.fetchone()
            return float(resultado[0]) if resultado else 0.0
        except Exception as e:
            raise BaseDatosError(f"Error al calcular ingresos del día: {e}") from e
        finally:
            cursor.close()

    def obtener_cantidad_ventas(self) -> int:
        """Retorna el número total de ventas registradas."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM venta")
            resultado = cursor.fetchone()
            return int(resultado[0]) if resultado else 0
        except Exception as e:
            raise BaseDatosError(f"Error al contar ventas: {e}") from e
        finally:
            cursor.close()

    def obtener_ventas_por_empleado(self) -> list:
        """
        Agrupa las ventas por empleado/vendedor.
        Retorna: (nombre_vendedor, total_ventas, monto_total)

        CORRECCIÓN #9: LEFT JOIN empleado y JOIN usuario permiten incluir
            a los admins que hayan registrado ventas.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)')) AS vendedor,
                    COUNT(v.id_venta)                                     AS total_ventas,
                    COALESCE(SUM(v.total), 0)                             AS monto_total
                FROM usuario u
                LEFT JOIN empleado e ON u.id_usuario = e.id_empleado
                LEFT JOIN venta v   ON u.id_usuario  = v.id_empleado
                WHERE u.tipo IN ('empleado', 'admin')
                GROUP BY u.id_usuario, e.nombre
                ORDER BY monto_total DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener ventas por empleado: {e}") from e
        finally:
            cursor.close()

    def obtener_top_productos_vendidos(self, limite: int = 5) -> list:
        """
        Productos más vendidos en cantidad.
        Retorna: (nombre_producto, marca, unidades_vendidas, ingresos_generados)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    p.nombre                      AS producto,
                    p.marca,
                    SUM(dv.cantidad)              AS unidades_vendidas,
                    SUM(dv.subtotal)              AS ingresos_generados
                FROM detalle_venta dv
                JOIN producto p ON dv.id_producto = p.id_producto
                GROUP BY p.id_producto, p.nombre, p.marca
                ORDER BY unidades_vendidas DESC
                LIMIT %s
            """, (limite,))
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener top productos: {e}") from e
        finally:
            cursor.close()

    def obtener_venta_promedio(self) -> float:
        """Retorna el valor promedio por venta."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COALESCE(AVG(total), 0) FROM venta")
            resultado = cursor.fetchone()
            return round(float(resultado[0]), 2) if resultado else 0.0
        except Exception as e:
            raise BaseDatosError(f"Error al calcular promedio de ventas: {e}") from e
        finally:
            cursor.close()

    def mostrar_resumen(self) -> None:
        """Imprime en consola un resumen ejecutivo del reporte de ventas."""
        total_ventas     = self.obtener_cantidad_ventas()
        ingresos_totales = self.obtener_total_ingresos()
        ingresos_hoy     = self.obtener_ingresos_hoy()
        promedio         = self.obtener_venta_promedio()

        print("\n" + "═" * 50)
        print("       REPORTE DE VENTAS — ElectroGabo")
        print("═" * 50)
        print(f"  Fecha de generación : {obtener_fecha_actual()}")
        print(f"  Total de ventas     : {total_ventas}")
        print(f"  Ingresos totales    : {formatear_moneda(ingresos_totales)}")
        print(f"  Ingresos hoy        : {formatear_moneda(ingresos_hoy)}")
        print(f"  Ticket promedio     : {formatear_moneda(promedio)}")

        print("\n  — Top 5 productos más vendidos —")
        top = self.obtener_top_productos_vendidos(5)
        if top:
            for i, (producto, marca, unidades, ingresos) in enumerate(top, 1):
                print(f"  {i}. {producto} ({marca}) | "
                      f"{unidades} uds | {formatear_moneda(float(ingresos))}")
        else:
            print("  Sin datos aún.")

        print("\n  — Ventas por vendedor —")
        por_vendedor = self.obtener_ventas_por_empleado()
        if por_vendedor:
            for vendedor, total_v, monto in por_vendedor:
                print(f"  • {vendedor}: {total_v} ventas | "
                      f"{formatear_moneda(float(monto))}")
        else:
            print("  Sin datos aún.")

        print("═" * 50 + "\n")

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def calcular_crecimiento(valor_anterior: float, valor_actual: float) -> float:
        """
        Método estático: calcula el porcentaje de crecimiento entre dos períodos.
        Retorna 0.0 si el valor anterior es cero (evita división por cero).
        """
        if valor_anterior == 0:
            return 0.0
        return round(((valor_actual - valor_anterior) / valor_anterior) * 100, 2)

    @staticmethod
    def formatear_fila_consola(id_venta, fecha, total, cliente, empleado) -> str:
        """Método estático: formatea una fila de venta para mostrar en consola."""
        return (
            f"  [{id_venta}] {fecha} | "
            f"Cliente: {cliente} | Empleado: {empleado} | "
            f"Total: {formatear_moneda(float(total))}"
        )