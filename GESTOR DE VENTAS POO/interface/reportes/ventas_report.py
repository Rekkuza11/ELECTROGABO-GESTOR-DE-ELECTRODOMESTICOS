"""
Vista: Reporte de Ventas.
Responsabilidad: mostrar en la interfaz gráfica los datos de ventas
generados por la capa reports/reporte_ventas.py.

Fase 6 · Corrección #20:
  - Se elimina la función local _crear_tabla() duplicada.
    Ahora se usa crear_tabla() de interface.components.tablas.
"""

import customtkinter as ctk
from reports.reporte_ventas import ReporteVentas
from interface.components.tablas import crear_tabla
from UTIL.helpers import formatear_moneda, obtener_fecha_actual


def abrir_reporte_ventas(parent: ctk.CTkFrame) -> None:
    """
    Limpia el frame padre y renderiza el reporte de ventas completo.
    """
    for widget in parent.winfo_children():
        widget.destroy()

    reporte = ReporteVentas()

    # ── Cabecera ──────────────────────────────────────────────────────────────
    ctk.CTkLabel(parent, text="📊 Reporte de Ventas",
                 font=("Arial", 26, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=30, pady=(30, 5))

    ctk.CTkLabel(parent, text=f"Generado el {obtener_fecha_actual()}",
                 font=("Arial", 13),
                 text_color="gray").pack(anchor="w", padx=30, pady=(0, 20))

    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    try:
        total_ventas     = reporte.obtener_cantidad_ventas()
        ingresos_totales = reporte.obtener_total_ingresos()
        ingresos_hoy     = reporte.obtener_ingresos_hoy()
        promedio         = reporte.obtener_venta_promedio()
    except Exception:
        total_ventas = ingresos_totales = ingresos_hoy = promedio = 0.0

    fila_cards = ctk.CTkFrame(parent, fg_color="transparent")
    fila_cards.pack(fill="x", padx=30, pady=(0, 15))

    _tarjeta(fila_cards, "↗", "#22c55e",
             formatear_moneda(ingresos_hoy), "Ingresos Hoy", "Del día actual")
    _tarjeta(fila_cards, "$", "#2563eb",
             formatear_moneda(ingresos_totales), "Ingresos Totales", "Acumulado histórico")
    _tarjeta(fila_cards, "🛒", "#06b6d4",
             str(total_ventas), "Total Ventas", "Transacciones registradas")
    _tarjeta(fila_cards, "~", "#a855f7",
             formatear_moneda(promedio), "Ticket Promedio", "Por transacción")

    # ── Área scrollable ───────────────────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(parent, fg_color="#f1f5f9")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Tabla: top productos ──────────────────────────────────────────────────
    _seccion_titulo(scroll, "🏆 Top 5 Productos Más Vendidos")

    try:
        top_productos = reporte.obtener_top_productos_vendidos(5)
    except Exception:
        top_productos = []

    cols_prod = ("Producto", "Marca", "Unidades Vendidas", "Ingresos Generados")
    tabla_prod = crear_tabla(scroll, cols_prod, altura=6, expandir=False)

    if top_productos:
        for producto, marca, unidades, ingresos in top_productos:
            tabla_prod.insert("", "end", values=(
                producto, marca, int(unidades), formatear_moneda(float(ingresos))
            ))
    else:
        tabla_prod.insert("", "end", values=("Sin datos", "-", "-", "-"))

    # ── Tabla: ventas por empleado ────────────────────────────────────────────
    _seccion_titulo(scroll, "👤 Ventas por Empleado")

    try:
        por_empleado = reporte.obtener_ventas_por_empleado()
    except Exception:
        por_empleado = []

    cols_emp = ("Empleado", "Total Ventas", "Monto Total")
    tabla_emp = crear_tabla(scroll, cols_emp, altura=6, expandir=False)

    if por_empleado:
        for empleado, total_v, monto in por_empleado:
            tabla_emp.insert("", "end", values=(
                empleado, int(total_v), formatear_moneda(float(monto))
            ))
    else:
        tabla_emp.insert("", "end", values=("Sin datos", "-", "-"))

    # ── Tabla: historial completo ─────────────────────────────────────────────
    _seccion_titulo(scroll, "📋 Historial Completo de Ventas")

    try:
        ventas = reporte.obtener_ventas_completas()
    except Exception:
        ventas = []

    cols_ven = ("ID", "Fecha", "Total", "Cliente", "Empleado")
    tabla_ven = crear_tabla(scroll, cols_ven, altura=6, expandir=False)

    if ventas:
        for id_v, fecha, total, cliente, empleado in ventas:
            tabla_ven.insert("", "end", values=(
                id_v, str(fecha), formatear_moneda(float(total)), cliente, empleado
            ))
    else:
        tabla_ven.insert("", "end",
                         values=("Sin ventas registradas", "-", "-", "-", "-"))


# ── Helpers internos ──────────────────────────────────────────────────────────

def _tarjeta(parent, icono, color, valor, titulo, subtitulo) -> None:
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=160)
    card.pack(side="left", expand=True, fill="both", padx=(0, 10))
    card.pack_propagate(False)
    ctk.CTkLabel(card, text=icono, font=("Arial", 20, "bold"),
                 fg_color=color, text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20, 10))
    ctk.CTkLabel(card, text=valor,    font=("Arial", 20, "bold"), text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=titulo,   font=("Arial", 13, "bold"), text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=subtitulo, font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 20))


def _seccion_titulo(parent, texto: str) -> None:
    ctk.CTkLabel(parent, text=texto, font=("Arial", 15, "bold"),
                 text_color="#1e293b").pack(anchor="w", pady=(20, 6))
    ctk.CTkFrame(parent, height=1, fg_color="#e2e8f0").pack(fill="x", pady=(0, 8))