"""
Vista: Reporte de Inventario.
Responsabilidad: mostrar en la interfaz gráfica el estado del inventario
generado por la capa reports/reporte_inventario.py.
Aplica el mismo estilo visual que admin_dasboard.py (customtkinter).
"""
 
import customtkinter as ctk
from tkinter import ttk
from reports.reporte_inventario import ReporteInventario
from UTIL.helpers import formatear_moneda, obtener_fecha_actual
 
 
def abrir_reporte_inventario(parent: ctk.CTkFrame) -> None:
    """
    Limpia el frame padre y renderiza el reporte de inventario completo.
    Recibe el frame de contenido del dashboard para dibujar dentro de él.
    """
    # Limpiar contenido anterior
    for widget in parent.winfo_children():
        widget.destroy()
 
    reporte = ReporteInventario()
 
    # ── Cabecera ──────────────────────────────────────────────────────────────
    ctk.CTkLabel(parent, text="📦 Reporte de Inventario",
                 font=("Arial", 26, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=30, pady=(30, 5))
 
    ctk.CTkLabel(parent, text=f"Generado el {obtener_fecha_actual()}",
                 font=("Arial", 13),
                 text_color="gray").pack(anchor="w", padx=30, pady=(0, 20))
 
    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    try:
        total_productos  = reporte.obtener_total_productos()
        valor_invertido  = reporte.obtener_valor_total_inventario()
        valor_potencial  = reporte.obtener_valor_potencial_ventas()
        ganancia_pot     = ReporteInventario.calcular_ganancia_potencial(
                               valor_invertido, valor_potencial)
        stock_bajo       = reporte.obtener_productos_stock_bajo()
        sin_stock        = reporte.obtener_productos_sin_stock()
    except Exception:
        total_productos = valor_invertido = valor_potencial = ganancia_pot = 0
        stock_bajo = sin_stock = []
 
    fila_cards = ctk.CTkFrame(parent, fg_color="transparent")
    fila_cards.pack(fill="x", padx=30, pady=(0, 15))
 
    _tarjeta(fila_cards, "📦", "#a855f7",
             str(total_productos), "Total Productos", "En catálogo")
    _tarjeta(fila_cards, "$", "#2563eb",
             formatear_moneda(valor_invertido), "Valor Invertido", "Costo del stock actual")
    _tarjeta(fila_cards, "↗", "#22c55e",
             formatear_moneda(valor_potencial), "Potencial de Venta", "Si se vende todo")
    _tarjeta(fila_cards, "💰", "#f97316",
             formatear_moneda(ganancia_pot), "Ganancia Potencial", "Margen bruto estimado")
 
    # ── Alertas de stock ──────────────────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(parent, fg_color="#f1f5f9")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))
 
    _seccion_titulo(scroll, "⚠ Alertas de Stock")
 
    alerta_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    alerta_frame.pack(fill="x", pady=(0, 10))
 
    if not stock_bajo:
        alerta_ok = ctk.CTkLabel(alerta_frame,
                                 text="✓  Inventario en niveles óptimos",
                                 font=("Arial", 12), text_color="#16a34a",
                                 fg_color="#dcfce7", corner_radius=8)
        alerta_ok.pack(fill="x", padx=15, pady=10)
    else:
        for id_p, nombre, marca, stock in stock_bajo:
            if stock == 0:
                color_bg, color_txt, icono = "#fee2e2", "#dc2626", "✗ AGOTADO"
            else:
                color_bg, color_txt, icono = "#fef9c3", "#ca8a04", f"⚠ Stock: {stock}"
 
            fila = ctk.CTkLabel(alerta_frame,
                                text=f"  {icono}  —  {nombre} ({marca})",
                                font=("Arial", 12), text_color=color_txt,
                                fg_color=color_bg, corner_radius=6, anchor="w")
            fila.pack(fill="x", padx=15, pady=(4, 0))
 
        # padding inferior
        ctk.CTkLabel(alerta_frame, text="", fg_color="white").pack(pady=4)
 
    # ── Tabla: todos los productos ────────────────────────────────────────────
    _seccion_titulo(scroll, "📋 Inventario Completo")
 
    try:
        productos = reporte.obtener_todos_los_productos()
    except Exception:
        productos = []
 
    cols_inv = ("ID", "Nombre", "Marca", "Precio Compra", "Precio Venta", "Stock", "Estado")
    tabla_inv = _crear_tabla(scroll, cols_inv)
 
    if productos:
        for id_p, nombre, marca, p_compra, p_venta, stock in productos:
            estado = ReporteInventario.evaluar_estado_stock(
                int(stock), ReporteInventario.STOCK_MINIMO)
            tabla_inv.insert("", "end", values=(
                id_p, nombre, marca,
                formatear_moneda(float(p_compra)),
                formatear_moneda(float(p_venta)),
                int(stock), estado
            ))
    else:
        tabla_inv.insert("", "end",
                         values=("Sin productos registrados", "-", "-", "-", "-", "-", "-"))
 
    # ── Tabla: top margen ─────────────────────────────────────────────────────
    _seccion_titulo(scroll, "🏆 Top 5 Productos por Mayor Margen")
 
    try:
        top_margen = reporte.obtener_productos_mayor_margen(5)
    except Exception:
        top_margen = []
 
    cols_mar = ("Nombre", "Marca", "Precio Compra", "Precio Venta", "Margen %")
    tabla_mar = _crear_tabla(scroll, cols_mar)
 
    if top_margen:
        for nombre, marca, p_compra, p_venta, margen in top_margen:
            tabla_mar.insert("", "end", values=(
                nombre, marca,
                formatear_moneda(float(p_compra)),
                formatear_moneda(float(p_venta)),
                f"{margen}%"
            ))
    else:
        tabla_mar.insert("", "end", values=("Sin datos", "-", "-", "-", "-"))
 
 
# ── Helpers internos ──────────────────────────────────────────────────────────
 
def _tarjeta(parent, icono: str, color: str,
             valor: str, titulo: str, subtitulo: str) -> None:
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=160)
    card.pack(side="left", expand=True, fill="both", padx=(0, 10))
    card.pack_propagate(False)
 
    ctk.CTkLabel(card, text=icono, font=("Arial", 20, "bold"),
                 fg_color=color, text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20, 10))
    ctk.CTkLabel(card, text=valor, font=("Arial", 20, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=titulo, font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=subtitulo, font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0, 20))
 
 
def _seccion_titulo(parent, texto: str) -> None:
    ctk.CTkLabel(parent, text=texto,
                 font=("Arial", 15, "bold"),
                 text_color="#1e293b").pack(anchor="w", pady=(20, 6))
    ctk.CTkFrame(parent, height=1, fg_color="#e2e8f0").pack(fill="x", pady=(0, 8))
 
 
def _crear_tabla(parent, columnas: tuple) -> ttk.Treeview:
    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure("ElectroGabo.Treeview",
                     background="white", foreground="#1e293b",
                     rowheight=30, fieldbackground="white",
                     font=("Arial", 11))
    estilo.configure("ElectroGabo.Treeview.Heading",
                     background="#f1f5f9", foreground="#64748b",
                     font=("Arial", 11, "bold"))
    estilo.map("ElectroGabo.Treeview",
               background=[("selected", "#dbeafe")])
 
    frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
    frame.pack(fill="x", pady=(0, 10))
 
    tabla = ttk.Treeview(frame, columns=columnas, show="headings",
                         style="ElectroGabo.Treeview", height=6)
 
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=130)
 
    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll_y.set)
 
    tabla.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll_y.pack(side="right", fill="y", pady=10)
 
    return tabla