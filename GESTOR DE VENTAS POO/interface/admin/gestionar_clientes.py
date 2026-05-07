"""
Vista: Gestión de Clientes.
Responsabilidad: renderizar el CRUD de clientes dentro del frame de contenido
del dashboard administrador.
"""

import customtkinter as ctk
from interface.controllers.cliente__controller import ClienteController
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar, fila_seleccionada
from interface.components.formularios import (
    campo_texto, campo_password, panel_formulario, limpiar_campos
)
from interface.components.mensajes import LabelEstado, confirmar, exito, error as msg_error
from interface.components.botones import btn_exito, btn_peligro, btn_secundario


_CTRL = ClienteController()

_COLS   = ("ID", "Nombre", "Teléfono", "Dirección")
_ANCHOS = [100, 220, 130, 260]


def abrir_gestionar_clientes(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza la vista de gestión de clientes."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "👥 Gestión de Clientes",
                   "Registra, consulta y elimina clientes del sistema")

    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Panel izquierdo — tabla 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n───
    panel_izq = ctk.CTkFrame(layout, fg_color="transparent")
    panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    barra = ctk.CTkFrame(panel_izq, fg_color="white", corner_radius=10)
    barra.pack(fill="x", pady=(0, 8))

    entry_buscar = ctk.CTkEntry(barra, width=220,
                                placeholder_text="🔍  Buscar cliente...",
                                font=("Arial", 12), border_color="#cbd5e1")
    entry_buscar.pack(side="left", padx=12, pady=10)

    seccion_titulo(panel_izq, "📋 Listado de Clientes")
    tabla = crear_tabla(panel_izq, _COLS, altura=12, anchos=_ANCHOS, expandir=True)

    # ── Panel derecho — formulario 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n
    panel_der = ctk.CTkFrame(layout, fg_color="transparent", width=340)
    panel_der.pack(side="right", fill="y")
    panel_der.pack_propagate(False)

    form_body = panel_formulario(panel_der, "➕ Registrar Nuevo Cliente")

    entry_id       = campo_texto(form_body,    "ID Cliente:",  "Ej: CLI001")
    entry_nombre   = campo_texto(form_body,    "Nombre:",      "Nombre completo")
    entry_telefono = campo_texto(form_body,    "Teléfono:",    "Ej: 3001234567")
    entry_dir      = campo_texto(form_body,    "Dirección:",   "Calle / barrio")
    entry_pwd      = campo_password(form_body, "Contraseña:")

    estado = LabelEstado(form_body)

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _limpiar_form():
        limpiar_campos(entry_id, entry_nombre, entry_telefono,
                       entry_dir, entry_pwd)
        estado.limpiar()

    def _recargar_tabla(filtro: str = ""):
        limpiar(tabla)
        try:
            clientes = _CTRL.listar()
        except Exception as e:
            msg_error("Error", str(e))
            return
        for c in clientes:
            if (filtro.lower() in c.nombre.lower()
                    or filtro.lower() in str(c.id_usuario).lower()):
                tabla.insert("", "end", values=(
                    c.id_usuario, c.nombre, c.telefono, c.direccion
                ))

    def _registrar():
        try:
            _CTRL.agregar(
                entry_id.get(), entry_nombre.get(),
                entry_telefono.get(), entry_dir.get(), entry_pwd.get(),
            )
            estado.mostrar("Cliente registrado correctamente.", "exito")
            _limpiar_form()
            _recargar_tabla()
        except Exception as e:
            estado.mostrar(str(e), "error")

    def _eliminar():
        fila = fila_seleccionada(tabla)
        if not fila:
            estado.mostrar("Selecciona un cliente de la tabla.", "advertencia")
            return
        if not confirmar("Eliminar cliente",
                         f"¿Eliminar al cliente '{fila[1]}' permanentemente?\n"
                         f"Se eliminarán también sus datos de acceso."):
            return
        try:
            _CTRL.eliminar(fila[0])
            exito("Eliminado", f"Cliente '{fila[1]}' eliminado correctamente.")
            _limpiar_form()
            _recargar_tabla()
        except Exception as e:
            msg_error("Error", str(e))

    def _cargar_en_form(event=None):
        fila = fila_seleccionada(tabla)
        if not fila:
            return
        limpiar_campos(entry_id, entry_nombre, entry_telefono, entry_dir, entry_pwd)
        entry_id.insert(0, str(fila[0]))
        entry_nombre.insert(0, str(fila[1]))
        entry_telefono.insert(0, str(fila[2]))
        entry_dir.insert(0, str(fila[3]))
        estado.mostrar(f"Datos del cliente ID {fila[0]} cargados.", "info")

    # Botones del formulario
    fila_btns = ctk.CTkFrame(form_body, fg_color="transparent")
    fila_btns.pack(fill="x", pady=(12, 0))
    btn_exito(fila_btns,     "💾 Registrar", _registrar, ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_peligro(fila_btns,   "🗑 Eliminar",  _eliminar,  ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_secundario(fila_btns, "✕ Limpiar",   _limpiar_form, ancho=100, alto=36).pack(side="left")

    entry_buscar.bind("<KeyRelease>", lambda e: _recargar_tabla(entry_buscar.get()))
    tabla.bind("<Double-1>", _cargar_en_form)

    _recargar_tabla()