"""
Controller: Reportes.
Responsabilidad: agregar datos de los tres módulos de reporte
(ventas, clientes, inventario) para alimentar el dashboard y las vistas.
Aplica SRP — sólo consolida información para presentación.
"""

from reports.reporte_ventas import ReporteVentas
from reports.reporte_clientes import ReporteClientes
from reports.reporte_inventario import ReporteInventario


class ReporteController:
    """Consolida datos de reportes para las vistas del panel administrador."""

    def __init__(self):
        self._rv = ReporteVentas()
        self._rc = ReporteClientes()
        self._ri = ReporteInventario()

    # ── Dashboard principal 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n────────

    def resumen_dashboard(self) -> dict:
        """
        Recopila todos los KPIs para las tarjetas del dashboard.
        Captura excepciones individualmente para que un fallo parcial
        no rompa la carga del panel.

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
            "ventas_hoy":       _safe(self._rv.obtener_ingresos_hoy, 0.0),
            "ingresos_totales": _safe(self._rv.obtener_total_ingresos, 0.0),
            "total_ventas":     _safe(self._rv.obtener_cantidad_ventas, 0),
            "total_productos":  _safe(self._ri.obtener_total_productos, 0),
            "total_clientes":   _safe(self._rc.obtener_total_clientes, 0),
        }

    # ── Alertas de inventario 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n──────

    def alertas_stock(self) -> list:
        """
        Retorna productos con stock bajo o agotado.
        Lista de (id_producto, nombre, marca, stock).
        """
        try:
            return self._ri.obtener_productos_stock_bajo()
        except Exception:
            return []

    # ── Datos rápidos para reportes 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n

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