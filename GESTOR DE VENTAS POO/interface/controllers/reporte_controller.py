"""
Controller: Reportes.
Responsabilidad: agregar datos de los tres módulos de reporte
(ventas, clientes, inventario) para alimentar el dashboard y las vistas.
Aplica SRP — sólo consolida información para presentación.

CORRECCIÓN #13 — Dashboard no muestra empleados:
    resumen_dashboard() retornaba el dict sin la clave 'empleados_activos'.
    La vista admin_dasboard.py mostraba "—" fija en la tarjeta de empleados
    porque esa clave nunca existía en el resultado.

    Solución:
    - Se añade la consulta directa a la tabla empleado a través de
      DatabaseConnection para contar los empleados registrados.
    - El resultado se incluye bajo la clave 'empleados_activos' en el dict.
    - Se mantiene el patrón _safe() para que un fallo parcial no rompa
      la carga del dashboard completo.
"""

from reports.reporte_ventas import ReporteVentas
from reports.reporte_clientes import ReporteClientes
from reports.reporte_inventario import ReporteInventario
from database import DatabaseConnection


class ReporteController:
    """Consolida datos de reportes para las vistas del panel administrador."""

    def __init__(self):
        self._rv = ReporteVentas()
        self._rc = ReporteClientes()
        self._ri = ReporteInventario()
        self._db = DatabaseConnection()

    # ── Dashboard principal ───────────────────────────────────────────────────

    def resumen_dashboard(self) -> dict:
        """
        Recopila todos los KPIs para las tarjetas del dashboard.
        Captura excepciones individualmente para que un fallo parcial
        no rompa la carga del panel.

        CORRECCIÓN #13:
            Se agrega 'empleados_activos' al dict retornado.  Antes esta
            clave faltaba y la tarjeta de empleados mostraba "—" de forma
            permanente aunque hubiera empleados registrados en la BD.

        Retorna:
            dict con claves:
                ventas_hoy, ingresos_totales, total_ventas,
                total_productos, total_clientes, empleados_activos.
        """
        def _safe(fn, default=0):
            try:
                return fn()
            except Exception:
                return default

        return {
            "ventas_hoy":          _safe(self._rv.obtener_ingresos_hoy, 0.0),
            "ingresos_totales":    _safe(self._rv.obtener_total_ingresos, 0.0),
            "total_ventas":        _safe(self._rv.obtener_cantidad_ventas, 0),
            "total_productos":     _safe(self._ri.obtener_total_productos, 0),
            "total_clientes":      _safe(self._rc.obtener_total_clientes, 0),
            # CORRECCIÓN #13: clave añadida — antes siempre faltaba
            "empleados_activos":   _safe(self._contar_empleados, 0),
        }

    # ── Alertas de inventario ─────────────────────────────────────────────────

    def alertas_stock(self) -> list:
        """
        Retorna productos con stock bajo o agotado.
        Lista de (id_producto, nombre, marca, stock).
        """
        try:
            return self._ri.obtener_productos_stock_bajo()
        except Exception:
            return []

    # ── Datos rápidos para reportes ───────────────────────────────────────────

    def top_productos(self, limite: int = 5) -> list:
        try:
            return self._rv.obtener_top_productos_vendidos(limite)
        except Exception:
            return []

    def ventas_por_empleado(self) -> list:
        try:
            return self._rv.obtener_ventas_por_empleado()
        except Exception:
            return []

    def top_clientes(self, limite: int = 5) -> list:
        try:
            return self._rc.obtener_top_clientes(limite)
        except Exception:
            return []

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _contar_empleados(self) -> int:
        """
        CORRECCIÓN #13: consulta directa para contar empleados activos.
        Se hace aquí porque ReporteClientes/Ventas/Inventario no exponen
        este dato, y añadir un método allá violaría su SRP.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM empleado")
            resultado = cursor.fetchone()
            return int(resultado[0]) if resultado else 0
        except Exception:
            return 0
        finally:
            cursor.close()
