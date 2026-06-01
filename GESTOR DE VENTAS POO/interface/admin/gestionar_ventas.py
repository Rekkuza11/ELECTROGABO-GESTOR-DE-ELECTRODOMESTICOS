"""
Vista: Gestión de Ventas (Administrador).
Responsabilidad: registrar nuevas ventas (carrito + cliente + empleado)
y consultar el historial completo de transacciones.

CORRECCIONES:
- _agregar_al_carrito: id_prod se guarda como int (no str) para evitar
  mismatch de tipo al llamar al controller/DAO.
- _confirmar_venta: validación explícita de campos antes de llamar registrar().
- combo_emp pre-seleccionado con el empleado de sesión si se recibe id_empleado_sesion.
- Manejo de excepción más granular para mostrar mensajes útiles al usuario.

CORRECCIÓN #10 — Uso de traceback en producción:
    Se eliminan `import traceback` y `traceback.print_exc()` del bloque
    except de _confirmar_venta().  Exponer el stack trace completo en
    producción filtra rutas internas, nombres de módulos y lógica del
    sistema, lo que representa un riesgo de seguridad real.
    El mensaje de error ya se muestra al usuario a través de
    estado_venta.mostrar(str(e), "error"), que es suficiente.

Fase 9 · Corrección #23 — String incorrecto en diálogo de eliminación:
    El mensaje de confirmación al eliminar una venta decía
    "Esta acción no revierte el stock descontado.", lo cual era
    correcto antes de la corrección #18 pero quedó desactualizado
    una vez que VentaController.eliminar() comenzó a reponer el stock
    de cada producto dentro de la misma transacción atómica.
    Se corrige al texto que refleja el comportamiento real del sistema.
"""

import customtkinter as ctk
from interface.controllers.venta_controller import VentaController
from interface.controllers.producro_controller import ProductoController
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar, fila_seleccionada
from interface.components.formularios import combo_opciones, campo_numero, panel_formulario, limpiar_campos
from interface.components.mensajes import LabelEstado, confirmar, exito, error as msg_error
from interface.components.botones import btn_primario, btn_peligro, btn_secundario, btn_exito
from UTIL.helpers import formatear_moneda
from dao.cliente_dao import ClienteDAO
from dao.empleado_dao import EmpleadoDAO


_CTRL_VENTA = VentaController()
_CTRL_PROD  = ProductoController()

_COLS_HIST   = ("ID", "Fecha", "Total", "Cliente", "Empleado")
_ANCHOS_HIST = [60, 160, 110, 180, 160]


def abrir_gestionar_ventas(parent: ctk.CTkFrame, id_empleado_sesion=None) -> None:
    """Limpia el frame padre y renderiza la vista de gestión de ventas."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "🛒 Gestión de Ventas",
                   "Registra nuevas ventas y consulta el historial de transacciones")

    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ══════════════════════════════════════════════════════════════════════════
    # Panel izquierdo — Historial
    # ══════════════════════════════════════════════════════════════════════════
    panel_hist = ctk.CTkFrame(layout, fg_color="transparent")
    panel_hist.pack(side="left", fill="both", expand=True, padx=(0, 12))

    seccion_titulo(panel_hist, "📋 Historial de Ventas")
    tabla_hist = crear_tabla(panel_hist, _COLS_HIST, altura=14,
                             anchos=_ANCHOS_HIST, expandir=True)

    barra_hist = ctk.CTkFrame(panel_hist, fg_color="white", corner_radius=10)
    barra_hist.pack(fill="x", pady=(8, 0))

    estado_hist = LabelEstado(barra_hist, pady=8)

    def _recargar_historial():
        limpiar(tabla_hist)
        try:
            ventas = _CTRL_VENTA.listar()
        except Exception as e:
            msg_error("Error", str(e))
            return
        for id_v, fecha, total, cliente, empleado in ventas:
            tabla_hist.insert("", "end", values=(
                id_v, str(fecha)[:16],
                formatear_moneda(float(total)),
                cliente, empleado,
            ))

    def _eliminar_venta():
        fila = fila_seleccionada(tabla_hist)
        if not fila:
            estado_hist.mostrar("Selecciona una venta del historial.", "advertencia")
            return

        # CORRECCIÓN #23: el mensaje original decía "Esta acción no revierte
        # el stock descontado." — incorrecto desde la corrección #18, que
        # implementó la reversión atómica del stock al eliminar una venta.
        if not confirmar("Eliminar venta",
                         f"¿Eliminar la venta ID {fila[0]} por {fila[2]}?\n"
                         "El stock de los productos será repuesto automáticamente."):
            return
        try:
            _CTRL_VENTA.eliminar(fila[0])
            exito("Eliminada", f"Venta ID {fila[0]} eliminada y stock repuesto.")
            _recargar_historial()
        except Exception as e:
            msg_error("Error", str(e))

    fila_acc = ctk.CTkFrame(barra_hist, fg_color="transparent")
    fila_acc.pack(fill="x", padx=12, pady=(0, 10))
    btn_secundario(fila_acc, "↺  Recargar", _recargar_historial, ancho=120, alto=34).pack(side="left", padx=(0, 8))
    btn_peligro(fila_acc,   "🗑  Eliminar", _eliminar_venta,     ancho=120, alto=34).pack(side="left")

    # ══════════════════════════════════════════════════════════════════════════
    # Panel derecho — Nueva Venta
    # ══════════════════════════════════════════════════════════════════════════
    panel_nueva = ctk.CTkScrollableFrame(layout, fg_color="transparent", width=400)
    panel_nueva.pack(side="right", fill="y")

    # ── Datos de la venta ─────────────────────────────────────────────────────
    form_venta = panel_formulario(panel_nueva, "🧾 Nueva Venta")

    try:
        clientes_raw  = ClienteDAO().obtener_todos()
        opciones_cli  = [f"{c.id_usuario} — {c.nombre}" for c in clientes_raw]
    except Exception:
        opciones_cli = []

    try:
        empleados_raw = EmpleadoDAO().obtener_todos()
        opciones_emp  = [f"{e.id_usuario} — {e.nombre}" for e in empleados_raw]
    except Exception:
        opciones_emp = []

    try:
        from database import DatabaseConnection
        _conn = DatabaseConnection().obtener_conexion()
        _cur  = _conn.cursor()
        _cur.execute("SELECT id_usuario FROM usuario WHERE tipo = 'admin'")
        for (id_admin,) in _cur.fetchall():
            opciones_emp.append(f"{id_admin} — {id_admin} (Admin)")
        _cur.close()
    except Exception:
        pass

    combo_cli = combo_opciones(form_venta, "Cliente:",  opciones_cli, ancho=250)
    combo_emp = combo_opciones(form_venta, "Empleado:", opciones_emp, ancho=250)

    if id_empleado_sesion and opciones_emp:
        for opcion in opciones_emp:
            if str(opcion).startswith(str(id_empleado_sesion) + " —"):
                combo_emp.set(opcion)
                break

    # ── Agregar productos al carrito ──────────────────────────────────────────
    form_prod = panel_formulario(panel_nueva, "➕ Agregar Producto al Carrito", pady=(8, 8))

    try:
        productos_raw = _CTRL_PROD.listar()
        opciones_prod = [
            f"{p.id_producto} — {p.nombre}  (${p.precio_venta:,.0f} | Stock:{p.stock})"
            for p in productos_raw
        ]
    except Exception:
        opciones_prod = []

    combo_prod = combo_opciones(form_prod, "Producto:", opciones_prod, ancho=250)
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
                                            height=80)
    scroll_carrito.pack(fill="x", padx=10, pady=5)

    lbl_total = ctk.CTkLabel(carrito_frame,
                              text="Total:  $0.00",
                              font=("Arial", 14, "bold"),
                              text_color="#1e293b")
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
            fila = ctk.CTkFrame(scroll_carrito, fg_color="#f8fafc", corner_radius=6)
            fila.pack(fill="x", pady=2)

            ctk.CTkLabel(fila,
                         text=f"{item['nombre']}",
                         font=("Arial", 11, "bold"), text_color="#1e293b",
                         anchor="w").pack(side="left", padx=8, pady=6)

            ctk.CTkLabel(fila,
                         text=f"x{item['cantidad']}  ·  {formatear_moneda(item['subtotal'])}",
                         font=("Arial", 11), text_color="#64748b").pack(side="left", padx=4)

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
        sel      = combo_prod.get()
        cant_str = entry_cant.get().strip()

        if not sel:
            estado_prod.mostrar("Selecciona un producto.", "advertencia")
            return
        try:
            cant = int(cant_str)
            if cant <= 0:
                raise ValueError
        except ValueError:
            estado_prod.mostrar("Cantidad inválida.", "error")
            return

        id_prod_str = sel.split(" — ")[0].strip()
        try:
            id_prod = int(id_prod_str)
        except ValueError:
            id_prod = id_prod_str

        try:
            prod = _CTRL_PROD.obtener(id_prod)
        except Exception as e:
            estado_prod.mostrar(str(e), "error")
            return

        if prod.stock < cant:
            estado_prod.mostrar(
                f"Stock insuficiente. Disponible: {prod.stock}", "error")
            return

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
        estado_prod.mostrar(f"'{prod.nombre}' agregado al carrito.", "exito")
        limpiar_campos(entry_cant)
        entry_cant.insert(0, "1")

    def _confirmar_venta():
        sel_cli = combo_cli.get()
        sel_emp = combo_emp.get()

        if not sel_cli:
            estado_venta.mostrar("Selecciona un cliente.", "advertencia")
            return
        if not sel_emp:
            estado_venta.mostrar("Selecciona un empleado.", "advertencia")
            return
        if not _carrito:
            estado_venta.mostrar("El carrito está vacío.", "advertencia")
            return

        id_cli = sel_cli.split(" — ")[0].strip()
        id_emp = sel_emp.split(" — ")[0].strip()
        items  = [(item["id_prod"], item["cantidad"]) for item in _carrito]
        total  = sum(item["subtotal"] for item in _carrito)

        if not confirmar("Confirmar venta",
                         f"¿Registrar venta por {formatear_moneda(total)}?\n"
                         f"Cliente: {sel_cli}\n"
                         f"Productos: {len(_carrito)} línea(s)"):
            return

        try:
            id_venta = _CTRL_VENTA.registrar(id_cli, id_emp, items)
            exito("Venta registrada",
                  f"Venta #{id_venta} registrada por {formatear_moneda(total)}.")
            _carrito.clear()
            _redibujar_carrito()
            combo_cli.set("")
            if not id_empleado_sesion:
                combo_emp.set("")
            estado_venta.mostrar(f"Venta #{id_venta} completada.", "exito")
            _recargar_historial()
        except Exception as e:
            # CORRECCIÓN #10: eliminados import traceback y traceback.print_exc().
            # Exponer el stack trace en producción filtra información interna
            # del sistema. El mensaje de excepción es suficiente para el usuario.
            estado_venta.mostrar(str(e), "error")

    def _limpiar_carrito():
        _carrito.clear()
        _redibujar_carrito()
        combo_cli.set("")
        if not id_empleado_sesion:
            combo_emp.set("")
        estado_venta.limpiar()

    # ── Botón agregar ─────────────────────────────────────────────────────────
    btn_primario(form_prod, "➕  Agregar al carrito",
                 _agregar_al_carrito, ancho=200, alto=36).pack(anchor="w", pady=(8, 0))

    # ── Botones finales ───────────────────────────────────────────────────────
    fila_final = ctk.CTkFrame(panel_nueva, fg_color="transparent")
    fila_final.pack(fill="x", pady=(4, 0))

    btn_exito(fila_final,    "✔  Confirmar Venta", _confirmar_venta, ancho=180, alto=40).pack(
        side="left", padx=(0, 8))
    btn_secundario(fila_final, "✕  Limpiar",       _limpiar_carrito, ancho=120, alto=40).pack(
        side="left")

    # ── Carga inicial ─────────────────────────────────────────────────────────
    _redibujar_carrito()
    _recargar_historial()