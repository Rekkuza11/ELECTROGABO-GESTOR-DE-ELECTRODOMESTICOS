"""
Vista: Clientes (Empleado).
Responsabilidad: mostrar el listado de clientes y su historial de compras
al empleado. Solo lectura — sin CRUD.

Fase 6 · Corrección #20:
  - Se elimina la función local _crear_tabla() duplicada.
    Ahora se usa crear_tabla() de interface.components.tablas.
"""

import customtkinter as ctk
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar
from interface.components.botones import btn_secundario
from interface.components.mensajes import alerta_inline
from UTIL.helpers import formatear_moneda


def abrir_clientes_empleado(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza la vista de clientes (solo lectura)."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(
        parent,
        "👥 Clientes",
        "Consulta el listado de clientes y su historial — vista de solo lectura",
    )

    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    try:
        from reports.reporte_clientes import ReporteClientes
        rc = ReporteClientes()
        total_c     = rc.obtener_total_clientes()
        sin_compras = rc.obtener_clientes_sin_compras()
        activos     = total_c - len(sin_compras)
        tasa        = ReporteClientes.calcular_tasa_actividad(total_c, activos)
        nuevos_mes  = rc.obtener_clientes_nuevos_mes()
    except Exception:
        total_c = activos = nuevos_mes = 0
        tasa = 0.0
        sin_compras = []

    fila_cards = ctk.CTkFrame(parent, fg_color="transparent")
    fila_cards.pack(fill="x", padx=30, pady=(0, 12))

    _tarjeta(fila_cards, "👥", "#ec4899", str(total_c),
             "Total Clientes", "Registrados en el sistema")
    _tarjeta(fila_cards, "✓", "#22c55e", str(activos),
             "Clientes Activos", f"{tasa}% con compras")
    _tarjeta(fila_cards, "🆕", "#06b6d4", str(nuevos_mes),
             "Nuevos Este Mes", "Primera compra en el mes")

    # ── Layout ────────────────────────────────────────────────────────────────
    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Panel izquierdo — listado de clientes ─────────────────────────────────
    panel_izq = ctk.CTkFrame(layout, fg_color="transparent")
    panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    barra = ctk.CTkFrame(panel_izq, fg_color="white", corner_radius=10)
    barra.pack(fill="x", pady=(0, 8))

    entry_buscar = ctk.CTkEntry(
        barra, width=230,
        placeholder_text="🔍  Buscar por nombre o ID...",
        font=("Arial", 12), border_color="#cbd5e1",
    )
    entry_buscar.pack(side="left", padx=12, pady=10)

    ctk.CTkLabel(
        barra, text="🔒  Solo lectura",
        font=("Arial", 11), text_color="#0369a1",
        fg_color="#e0f2fe", corner_radius=6,
    ).pack(side="right", padx=12, pady=10)

    seccion_titulo(panel_izq, "📋 Listado de Clientes")

    _COLS   = ("ID", "Nombre", "Teléfono", "Dirección")
    _ANCHOS = [90, 200, 120, 220]
    tabla_cli = crear_tabla(panel_izq, _COLS, altura=13, anchos=_ANCHOS, expandir=True)

    lbl_conteo = ctk.CTkLabel(panel_izq, text="",
                               font=("Arial", 11), text_color="#64748b")
    lbl_conteo.pack(anchor="w", pady=(4, 0))

    # ── Panel derecho — historial ─────────────────────────────────────────────
    panel_der = ctk.CTkFrame(layout, fg_color="transparent", width=380)
    panel_der.pack(side="right", fill="y")
    panel_der.pack_propagate(False)

    seccion_titulo(panel_der, "🧾 Historial del Cliente")

    info_frame = ctk.CTkFrame(panel_der, fg_color="white", corner_radius=10)
    info_frame.pack(fill="x", pady=(0, 8))

    lbl_cliente_sel = ctk.CTkLabel(
        info_frame,
        text="  Haz doble clic en un cliente para ver su historial.",
        font=("Arial", 12), text_color="#64748b", anchor="w",
    )
    lbl_cliente_sel.pack(anchor="w", padx=15, pady=10)

    resumen_frame = ctk.CTkFrame(panel_der, fg_color="white", corner_radius=10)
    resumen_frame.pack(fill="x", pady=(0, 8))

    lbl_resumen = ctk.CTkLabel(resumen_frame, text="",
                                font=("Arial", 11), text_color="#1e293b",
                                justify="left", anchor="w")
    lbl_resumen.pack(anchor="w", padx=15, pady=8)

    _COLS_H  = ("ID Venta", "Fecha", "Total")
    _ANCH_H  = [90, 150, 110]
    tabla_hist = crear_tabla(panel_der, _COLS_H, altura=10, anchos=_ANCH_H, expandir=True)

    lbl_total_cli = ctk.CTkLabel(panel_der, text="",
                                  font=("Arial", 13, "bold"), text_color="#1e293b")
    lbl_total_cli.pack(anchor="e", padx=8, pady=(4, 0))

    # ── Lógica ────────────────────────────────────────────────────────────────
    _todos: list = []

    def _recargar(filtro: str = ""):
        limpiar(tabla_cli)
        _todos.clear()
        try:
            from dao.cliente_dao import ClienteDAO
            clientes = ClienteDAO().obtener_todos()
        except Exception as e:
            alerta_inline(panel_izq, f"Error al cargar clientes: {e}", tipo="error")
            return

        _todos.extend(clientes)
        filtro_lower = filtro.strip().lower()
        mostrados = 0
        for c in clientes:
            if filtro_lower and (
                filtro_lower not in c.nombre.lower()
                and filtro_lower not in str(c.id_usuario).lower()
            ):
                continue
            tabla_cli.insert("", "end", values=(
                c.id_usuario, c.nombre, c.telefono, c.direccion
            ))
            mostrados += 1
        lbl_conteo.configure(text=f"{mostrados} cliente(s) encontrado(s)")

    def _ver_historial(event=None):
        sel = tabla_cli.selection()
        if not sel:
            return
        valores = tabla_cli.item(sel[0])["values"]
        if not valores:
            return
        id_cli, nombre, telefono, _ = valores

        for row in tabla_hist.get_children():
            tabla_hist.delete(row)
        lbl_total_cli.configure(text="")
        lbl_resumen.configure(text="")
        lbl_cliente_sel.configure(
            text=f"  👤  {nombre}  —  Tel: {telefono}",
            text_color="#1e293b",
        )
        try:
            from reports.reporte_clientes import ReporteClientes
            rc = ReporteClientes()
            historial = rc.obtener_historial_cliente(id_cli)
            segmento  = ReporteClientes.clasificar_cliente(
                sum(float(r[2]) for r in historial) if historial else 0.0
            )
            if historial:
                monto_total = 0.0
                for id_v, fecha, total, empleado in historial:
                    tabla_hist.insert("", "end", values=(
                        id_v, str(fecha)[:16], formatear_moneda(float(total)),
                    ))
                    monto_total += float(total)
                lbl_resumen.configure(
                    text=(f"  Compras: {len(historial)}  ·  "
                          f"Segmento: {segmento}  ·  "
                          f"Total: {formatear_moneda(monto_total)}"),
                    text_color="#1e293b",
                )
                lbl_total_cli.configure(
                    text=f"Total acumulado:  {formatear_moneda(monto_total)}")
            else:
                tabla_hist.insert("", "end", values=("Sin compras", "-", "-"))
                lbl_resumen.configure(
                    text="  Este cliente aún no tiene compras registradas.",
                    text_color="#64748b",
                )
        except Exception as e:
            tabla_hist.insert("", "end", values=(f"Error: {e}", "-", "-"))

    entry_buscar.bind("<KeyRelease>", lambda e: _recargar(entry_buscar.get()))
    tabla_cli.bind("<Double-1>", _ver_historial)

    btn_secundario(barra, "↺  Recargar", _recargar, ancho=110, alto=34).pack(
        side="left", padx=(0, 8), pady=10
    )
    _recargar()


# ── Helpers internos ──────────────────────────────────────────────────────────

def _tarjeta(parent, icono, color, valor, titulo, subtitulo):
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=145)
    card.pack(side="left", expand=True, fill="both", padx=(0, 10))
    card.pack_propagate(False)
    ctk.CTkLabel(card, text=icono, font=("Arial", 20, "bold"),
                 fg_color=color, text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(16, 8))
    ctk.CTkLabel(card, text=valor,    font=("Arial", 20, "bold"), text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=titulo,   font=("Arial", 13, "bold"), text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=subtitulo, font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 16))