"""
Vista: Ventas (Empleado).
Responsabilidad: permitir al empleado registrar nuevas ventas mediante
un carrito de compras. El empleado NO puede eliminar ventas ya registradas.
"""

import customtkinter as ctk

from interface.controllers.venta_controller import VentaController
from interface.controllers.producro_controller import ProductoController
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar
from interface.components.formularios import (
    combo_opciones, campo_numero, panel_formulario, limpiar_campos,
)
from interface.components.mensajes import LabelEstado, confirmar, exito, error as msg_error
from interface.components.botones import btn_primario, btn_secundario, btn_exito
from UTIL.helpers import formatear_moneda
from dao.cliente_dao import ClienteDAO


_CTRL_VENTA = VentaController()
_CTRL_PROD  = ProductoController()

_COLS_HIST  = ("ID", "Fecha", "Total", "Cliente")
_ANCHOS_HIST = [60, 160, 120, 200]


def abrir_ventas_empleado(parent: ctk.CTkFrame, id_empleado: str) -> None:
    """Limpia el frame padre y renderiza la vista de ventas del empleado."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(
        parent,
        "🛒 Registro de Ventas",
        f"Registra nuevas ventas — sesión empleado: {id_empleado}",
    )

    # Aviso de permisos
    aviso = ctk.CTkFrame(parent, fg_color="#f0f9ff", corner_radius=8)
    aviso.pack(fill="x", padx=30, pady=(0, 10))
    ctk.CTkLabel(
        aviso,
        text="ℹ  Las ventas registradas no pueden eliminarse desde este panel.",
        font=("Arial", 11), text_color="#0369a1", anchor="w",
    ).pack(anchor="w", padx=16, pady=8)

    # ── Layout: izquierda historial / derecha nueva venta ─────────────────────
    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ══════════════════════════════════════════════════════════════════════════
    # Panel izquierdo — Historial (solo las ventas del empleado)
    # ══════════════════════════════════════════════════════════════════════════
    panel_hist = ctk.CTkFrame(layout, fg_color="transparent")
    panel_hist.pack(side="left", fill="both", expand=True, padx=(0, 12))

    barra_hist = ctk.CTkFrame(panel_hist, fg_color="white", corner_radius=10)
    barra_hist.pack(fill="x", pady=(0, 8))

    entry_buscar = ctk.CTkEntry(
        barra_hist, width=220,
        placeholder_text="🔍  Buscar por cliente...",
        font=("Arial", 12), border_color="#cbd5e1",
    )
    entry_buscar.pack(side="left", padx=12, pady=10)

    lbl_conteo = ctk.CTkLabel(
        barra_hist, text="",
        font=("Arial", 11), text_color="#64748b",
    )
    lbl_conteo.pack(side="right", padx=12)

    seccion_titulo(panel_hist, "📋 Mis Ventas Registradas")
    tabla_hist = crear_tabla(panel_hist, _COLS_HIST, altura=14,
                             anchos=_ANCHOS_HIST, expandir=True)

    # ── Resumen del empleado ──────────────────────────────────────────────────
    resumen_frame = ctk.CTkFrame(panel_hist, fg_color="white", corner_radius=10)
    resumen_frame.pack(fill="x", pady=(8, 0))

    lbl_resumen = ctk.CTkLabel(
        resumen_frame, text="",
        font=("Arial", 12), text_color="#1e293b", anchor="w",
    )
    lbl_resumen.pack(anchor="w", padx=15, pady=10)

    # ══════════════════════════════════════════════════════════════════════════
    # Panel derecho — Nueva Venta
    # ══════════════════════════════════════════════════════════════════════════
    panel_nueva = ctk.CTkFrame(layout, fg_color="transparent", width=400)
    panel_nueva.pack(side="right", fill="y")
    panel_nueva.pack_propagate(False)

    # ── Datos de la venta ─────────────────────────────────────────────────────
    form_venta = panel_formulario(panel_nueva, "🧾 Nueva Venta")

    try:
        clientes_raw = ClienteDAO().obtener_todos()
        opciones_cli = [f"{c.id_usuario} — {c.nombre}" for c in clientes_raw]
    except Exception:
        opciones_cli = []

    combo_cli = combo_opciones(form_venta, "Cliente:", opciones_cli, ancho=260)

    # ── Agregar productos al carrito ──────────────────────────────────────────
    form_prod = panel_formulario(panel_nueva, "➕ Agregar Producto", pady=(8, 8))

    try:
        productos_raw = _CTRL_PROD.listar()
        opciones_prod = [
            f"{p.id_producto} — {p.nombre}  (${p.precio_venta:,.0f} | Stock:{p.stock})"
            for p in productos_raw
        ]
    except Exception:
        opciones_prod = []

    combo_prod = combo_opciones(form_prod, "Producto:", opciones_prod, ancho=260)
    entry_cant = campo_numero(form_prod, "Cantidad:", "1", ancho=80)

    estado_prod = LabelEstado(form_prod)

    # ── Carrito ───────────────────────────────────────────────────────────────
    carrito_frame = ctk.CTkFrame(panel_nueva, fg_color="white", corner_radius=12)
    carrito_frame.pack(fill="x", pady=(0, 8))

    ctk.CTkLabel(carrito_frame, text="🛒 Carrito",
                 font=("Arial", 13, "bold"), text_color="#1e293b").pack(
                     anchor="w", padx=15, pady=(12, 4))
    ctk.CTkFrame(carrito_frame, height=1, fg_color="#e2e8f0").pack(fill="x")

    scroll_carrito = ctk.CTkScrollableFrame(carrito_frame, fg_color="transparent",
                                            height=150)
    scroll_carrito.pack(fill="x", padx=10, pady=5)

    lbl_total = ctk.CTkLabel(carrito_frame,
                              text="Total:  $0.00",
                              font=("Arial", 14, "bold"),
                              text_color="#0891b2")
    lbl_total.pack(anchor="e", padx=20, pady=(4, 12))

    estado_venta = LabelEstado(panel_nueva)

    # ── Estado interno del carrito ────────────────────────────────────────────
    _carrito: list[dict] = []

    def _actualizar_total():
        total = sum(item["subtotal"] for item in _carrito)
        lbl_total.configure(text=f"Total:  {formatear_moneda(total)}")

    def _redibujar_carrito():
        for w in scroll_carrito.winfo_children():
            w.destroy()

        if not _carrito:
            ctk.CTkLabel(scroll_carrito,
                         text="Sin productos agregados.",
                         font=("Arial", 11), text_color="gray").pack(pady=10)
            _actualizar_total()
            return

        for i, item in enumerate(_carrito):
            fila = ctk.CTkFrame(scroll_carrito, fg_color="#f0fdff",
                                corner_radius=6)
            fila.pack(fill="x", pady=2)

            ctk.CTkLabel(fila,
                         text=item["nombre"],
                         font=("Arial", 11, "bold"), text_color="#1e293b",
                         anchor="w").pack(side="left", padx=8, pady=6)

            ctk.CTkLabel(fila,
                         text=f"x{item['cantidad']}  ·  {formatear_moneda(item['subtotal'])}",
                         font=("Arial", 11), text_color="#64748b").pack(
                             side="left", padx=4)

            idx = i
            ctk.CTkButton(fila, text="✕", width=28, height=28,
                          fg_color="#fee2e2", text_color="#dc2626",
                          hover_color="#fecaca", font=("Arial", 10, "bold"),
                          command=lambda n=idx: _quitar_item(n)).pack(
                              side="right", padx=6, pady=4)

        _actualizar_total()

    def _quitar_item(indice: int):
        if 0 <= indice < len(_carrito):
            _carrito.pop(indice)
            _redibujar_carrito()
            estado_venta.limpiar()

    def _agregar_al_carrito():
        sel = combo_prod.get()
        cant_str = entry_cant.get().strip()

        if not sel:
            estado_prod.mostrar("Selecciona un producto.", "advertencia")
            return
        try:
            cant = int(cant_str)
            if cant <= 0:
                raise ValueError
        except ValueError:
            estado_prod.mostrar("Ingresa una cantidad válida.", "error")
            return

        id_prod = sel.split(" — ")[0].strip()

        try:
            prod = _CTRL_PROD.obtener(id_prod)
        except Exception as e:
            estado_prod.mostrar(str(e), "error")
            return

        if prod.stock < cant:
            estado_prod.mostrar(
                f"Stock insuficiente. Disponible: {prod.stock}", "error")
            return

        # Si ya está en carrito, sumar cantidad
        for item in _carrito:
            if item["id_prod"] == id_prod:
                nueva_cant = item["cantidad"] + cant
                if prod.stock < nueva_cant:
                    estado_prod.mostrar(
                        f"Stock insuficiente para {nueva_cant} unidades.", "error")
                    return
                item["cantidad"] = nueva_cant
                item["subtotal"] = round(nueva_cant * item["precio"], 2)
                _redibujar_carrito()
                estado_prod.mostrar(f"Cantidad actualizada a {nueva_cant}.", "exito")
                limpiar_campos(entry_cant)
                entry_cant.insert(0, "1")
                return

        _carrito.append({
            "id_prod":  id_prod,
            "nombre":   prod.nombre,
            "cantidad": cant,
            "precio":   prod.precio_venta,
            "subtotal": round(cant * prod.precio_venta, 2),
        })
        _redibujar_carrito()
        estado_prod.mostrar(f"'{prod.nombre}' agregado.", "exito")
        limpiar_campos(entry_cant)
        entry_cant.insert(0, "1")

    def _confirmar_venta():
        sel_cli = combo_cli.get()

        if not sel_cli:
            estado_venta.mostrar("Selecciona un cliente.", "advertencia")
            return
        if not _carrito:
            estado_venta.mostrar("El carrito está vacío.", "advertencia")
            return

        id_cli = sel_cli.split(" — ")[0].strip()
        items  = [(item["id_prod"], item["cantidad"]) for item in _carrito]
        total  = sum(item["subtotal"] for item in _carrito)

        if not confirmar("Confirmar venta",
                         f"¿Registrar venta por {formatear_moneda(total)}?\n"
                         f"Cliente: {sel_cli}\n"
                         f"Productos: {len(_carrito)} línea(s)"):
            return

        try:
            id_venta = _CTRL_VENTA.registrar(id_cli, id_empleado, items)
            exito("Venta registrada",
                  f"Venta #{id_venta} registrada por {formatear_moneda(total)}.")
            _carrito.clear()
            _redibujar_carrito()
            combo_cli.set("")
            estado_venta.mostrar(f"✓  Venta #{id_venta} completada.", "exito")
            _recargar_historial()
        except Exception as e:
            estado_venta.mostrar(str(e), "error")

    def _limpiar_carrito():
        _carrito.clear()
        _redibujar_carrito()
        combo_cli.set("")
        estado_venta.limpiar()

    # ── Recarga del historial ─────────────────────────────────────────────────
    def _recargar_historial(filtro: str = ""):
        limpiar(tabla_hist)
        try:
            todas_ventas = _CTRL_VENTA.listar()
        except Exception as e:
            msg_error("Error", str(e))
            return

        # Filtrar por id_empleado (columna 4 = empleado nombre, usamos el dao directo)
        try:
            from database import DatabaseConnection
            conn = DatabaseConnection().obtener_conexion()
            cur  = conn.cursor()
            cur.execute("""
                SELECT v.id_venta, v.fecha, v.total, c.nombre AS cliente
                FROM venta v
                JOIN cliente c ON v.id_cliente = c.id_cliente
                WHERE v.id_empleado = %s
                ORDER BY v.fecha DESC
            """, (id_empleado,))
            mis_ventas = cur.fetchall()
            cur.close()
        except Exception:
            # Fallback: mostrar todas
            mis_ventas = [(r[0], r[1], r[2], r[3]) for r in todas_ventas]

        filtro_lower = filtro.strip().lower()
        total_acum   = 0.0
        mostrados    = 0

        for id_v, fecha, total, cliente in mis_ventas:
            if filtro_lower and filtro_lower not in str(cliente).lower():
                continue
            tabla_hist.insert("", "end", values=(
                id_v, str(fecha)[:16],
                formatear_moneda(float(total)),
                cliente,
            ))
            total_acum += float(total)
            mostrados  += 1

        lbl_conteo.configure(text=f"{mostrados} venta(s)")
        lbl_resumen.configure(
            text=(
                f"  📊  Ventas: {mostrados}  ·  "
                f"Total generado: {formatear_moneda(total_acum)}"
            )
        )

    # ── Botón agregar al carrito ──────────────────────────────────────────────
    btn_primario(form_prod, "➕  Agregar al carrito",
                 _agregar_al_carrito, ancho=200, alto=36).pack(
                     anchor="w", pady=(8, 0))

    # ── Botones finales ───────────────────────────────────────────────────────
    fila_final = ctk.CTkFrame(panel_nueva, fg_color="transparent")
    fila_final.pack(fill="x", pady=(4, 0))

    btn_exito(fila_final, "✔  Confirmar Venta",
              _confirmar_venta, ancho=185, alto=40).pack(side="left", padx=(0, 8))
    btn_secundario(fila_final, "✕  Limpiar",
                   _limpiar_carrito, ancho=120, alto=40).pack(side="left")

    btn_secundario(barra_hist, "↺  Recargar",
                   _recargar_historial, ancho=110, alto=34).pack(
                       side="left", padx=(0, 8), pady=10)

    entry_buscar.bind("<KeyRelease>",
                      lambda e: _recargar_historial(entry_buscar.get()))

    # ── Carga inicial ─────────────────────────────────────────────────────────
    _redibujar_carrito()
    _recargar_historial()
