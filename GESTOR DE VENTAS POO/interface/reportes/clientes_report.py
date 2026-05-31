"""
Vista: Reporte de Clientes.
Responsabilidad: mostrar en la interfaz gráfica los datos de clientes
generados por la capa reports/reporte_clientes.py.

Fase 6 · Corrección #20:
  - Se elimina la función local _crear_tabla() duplicada.
    Ahora se usa crear_tabla() de interface.components.tablas.
"""

import customtkinter as ctk
from tkinter import ttk
from reports.reporte_clientes import ReporteClientes
from interface.components.tablas import crear_tabla
from UTIL.helpers import formatear_moneda, obtener_fecha_actual


def abrir_reporte_clientes(parent: ctk.CTkFrame) -> None:
    """
    Limpia el frame padre y renderiza el reporte de clientes completo.
    """
    for widget in parent.winfo_children():
        widget.destroy()

    reporte = ReporteClientes()

    # ── Cabecera ──────────────────────────────────────────────────────────────
    ctk.CTkLabel(parent, text="👥 Reporte de Clientes",
                 font=("Arial", 26, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=30, pady=(30, 5))

    ctk.CTkLabel(parent, text=f"Generado el {obtener_fecha_actual()}",
                 font=("Arial", 13),
                 text_color="gray").pack(anchor="w", padx=30, pady=(0, 20))

    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    try:
        total_clientes = reporte.obtener_total_clientes()
        sin_compras    = reporte.obtener_clientes_sin_compras()
        gasto_prom     = reporte.obtener_gasto_promedio_por_cliente()
        nuevos_mes     = reporte.obtener_clientes_nuevos_mes()
        activos        = total_clientes - len(sin_compras)
        tasa           = ReporteClientes.calcular_tasa_actividad(total_clientes, activos)
    except Exception:
        total_clientes = activos = nuevos_mes = 0
        gasto_prom = tasa = 0.0
        sin_compras = []

    fila_cards = ctk.CTkFrame(parent, fg_color="transparent")
    fila_cards.pack(fill="x", padx=30, pady=(0, 15))

    _tarjeta(fila_cards, "👥", "#ec4899", str(total_clientes),
             "Total Clientes", "Registrados en el sistema")
    _tarjeta(fila_cards, "✓", "#22c55e", str(activos),
             "Clientes Activos", f"{tasa}% con compras")
    _tarjeta(fila_cards, "🆕", "#06b6d4", str(nuevos_mes),
             "Nuevos Este Mes", "Primera compra en el mes")
    _tarjeta(fila_cards, "$", "#2563eb", formatear_moneda(gasto_prom),
             "Gasto Promedio", "Por cliente activo")

    # ── Área scrollable ───────────────────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(parent, fg_color="#f1f5f9")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Tabla: top clientes ───────────────────────────────────────────────────
    _seccion_titulo(scroll, "🏆 Top 5 Mejores Clientes")

    try:
        top = reporte.obtener_top_clientes(5)
    except Exception:
        top = []

    cols_top = ("ID", "Nombre", "Teléfono", "Compras", "Total Gastado", "Segmento")
    tabla_top = crear_tabla(scroll, cols_top, altura=6, expandir=False)

    if top:
        for id_c, nombre, telefono, compras, monto in top:
            segmento = ReporteClientes.clasificar_cliente(float(monto))
            tabla_top.insert("", "end", values=(
                id_c, nombre, telefono,
                int(compras), formatear_moneda(float(monto)), segmento
            ))
    else:
        tabla_top.insert("", "end", values=("Sin datos", "-", "-", "-", "-", "-"))

    # ── Panel: clientes sin compras ───────────────────────────────────────────
    _seccion_titulo(scroll, "😴 Clientes Sin Actividad")

    inactivos_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    inactivos_frame.pack(fill="x", pady=(0, 10))

    if not sin_compras:
        ctk.CTkLabel(inactivos_frame,
                     text="✓  Todos los clientes han realizado al menos una compra.",
                     font=("Arial", 12), text_color="#16a34a",
                     fg_color="#dcfce7", corner_radius=8).pack(
                         fill="x", padx=15, pady=10)
    else:
        for id_c, nombre, telefono in sin_compras:
            ctk.CTkLabel(inactivos_frame,
                         text=f"  •  [{id_c}]  {nombre}  —  Tel: {telefono}",
                         font=("Arial", 12), text_color="#92400e",
                         fg_color="#fef3c7", corner_radius=6, anchor="w").pack(
                             fill="x", padx=15, pady=(4, 0))
        ctk.CTkLabel(inactivos_frame, text="", fg_color="white").pack(pady=4)

    # ── Tabla: listado completo ───────────────────────────────────────────────
    _seccion_titulo(scroll, "📋 Listado Completo de Clientes")

    try:
        todos = reporte.obtener_todos_los_clientes()
    except Exception:
        todos = []

    cols_all = ("ID", "Nombre", "Teléfono", "Dirección")
    tabla_all = crear_tabla(scroll, cols_all, altura=6, expandir=False)

    if todos:
        for id_c, nombre, telefono, direccion in todos:
            tabla_all.insert("", "end", values=(id_c, nombre, telefono, direccion))
    else:
        tabla_all.insert("", "end", values=("Sin clientes registrados", "-", "-", "-"))

    # ── Buscar historial de cliente ───────────────────────────────────────────
    _seccion_titulo(scroll, "🔍 Buscar Historial de Cliente")

    busqueda_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    busqueda_frame.pack(fill="x", pady=(0, 10))

    fila_busqueda = ctk.CTkFrame(busqueda_frame, fg_color="transparent")
    fila_busqueda.pack(fill="x", padx=15, pady=15)

    ctk.CTkLabel(fila_busqueda, text="ID Cliente:",
                 font=("Arial", 12), text_color="#1e293b").pack(side="left", padx=(0, 8))

    entry_id = ctk.CTkEntry(fila_busqueda, width=120, placeholder_text="Ej: 1",
                            font=("Arial", 12))
    entry_id.pack(side="left", padx=(0, 10))

    cols_hist = ("ID Venta", "Fecha", "Total", "Empleado")
    tabla_hist_frame = ctk.CTkFrame(busqueda_frame, fg_color="white", corner_radius=8)
    tabla_hist_frame.pack(fill="x", padx=15, pady=(0, 15))

    tabla_hist = crear_tabla(tabla_hist_frame, cols_hist, altura=4, expandir=False)

    lbl_estado = ctk.CTkLabel(busqueda_frame, text="",
                              font=("Arial", 11), text_color="gray")
    lbl_estado.pack(anchor="w", padx=15, pady=(0, 8))

    def _buscar_historial():
        id_val = entry_id.get().strip()
        for row in tabla_hist.get_children():
            tabla_hist.delete(row)
        if not id_val:
            lbl_estado.configure(text="Ingresa un ID de cliente.", text_color="gray")
            return
        try:
            historial = reporte.obtener_historial_cliente(id_val)
            if historial:
                for id_v, fecha, total, empleado in historial:
                    tabla_hist.insert("", "end", values=(
                        id_v, str(fecha), formatear_moneda(float(total)), empleado
                    ))
                lbl_estado.configure(
                    text=f"{len(historial)} venta(s) encontrada(s).",
                    text_color="#16a34a")
            else:
                tabla_hist.insert("", "end",
                                  values=("Sin compras registradas", "-", "-", "-"))
                lbl_estado.configure(text="El cliente no tiene compras.", text_color="gray")
        except Exception as e:
            lbl_estado.configure(text=f"Error: {e}", text_color="#dc2626")

    ctk.CTkButton(fila_busqueda, text="Buscar", width=100, height=34,
                  fg_color="#2563eb", text_color="white",
                  hover_color="#1d4ed8", font=("Arial", 12),
                  command=_buscar_historial).pack(side="left")


# ── Helpers internos ──────────────────────────────────────────────────────────

def _tarjeta(parent, icono, color, valor, titulo, subtitulo) -> None:
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=160)
    card.pack(side="left", expand=True, fill="both", padx=(0, 10))
    card.pack_propagate(False)
    ctk.CTkLabel(card, text=icono, font=("Arial", 20, "bold"),
                 fg_color=color, text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20, 10))
    ctk.CTkLabel(card, text=valor,   font=("Arial", 20, "bold"), text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=titulo,  font=("Arial", 13, "bold"), text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=subtitulo, font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 20))


def _seccion_titulo(parent, texto: str) -> None:
    ctk.CTkLabel(parent, text=texto, font=("Arial", 15, "bold"),
                 text_color="#1e293b").pack(anchor="w", pady=(20, 6))
    ctk.CTkFrame(parent, height=1, fg_color="#e2e8f0").pack(fill="x", pady=(0, 8))