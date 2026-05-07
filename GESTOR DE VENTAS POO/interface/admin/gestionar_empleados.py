"""
Vista: Gestión de Empleados.
Responsabilidad: renderizar el CRUD de empleados dentro del frame de contenido
del dashboard administrador.
"""

import customtkinter as ctk
from dao.empleado_dao import EmpleadoDAO
from models.empleado import Empleado
from exceptions import ValidacionError, BaseDatosError
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar, fila_seleccionada
from interface.components.formularios import (
    campo_texto, campo_password, combo_opciones,
    panel_formulario, limpiar_campos
)
from interface.components.mensajes import LabelEstado, confirmar, exito, error as msg_error
from interface.components.botones import btn_exito, btn_peligro, btn_secundario
from UTIL.helpers import validar_no_vacio


_DAO = EmpleadoDAO()

_COLS   = ("ID", "Nombre", "Rol")
_ANCHOS = [120, 260, 140]
_ROLES  = ["vendedor", "supervisor", "almacenista"]


def abrir_gestionar_empleados(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza la vista de gestión de empleados."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "👤 Gestión de Empleados",
                   "Administra el personal activo del sistema")

    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Panel izquierdo — tabla 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n───
    panel_izq = ctk.CTkFrame(layout, fg_color="transparent")
    panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    barra = ctk.CTkFrame(panel_izq, fg_color="white", corner_radius=10)
    barra.pack(fill="x", pady=(0, 8))
    entry_buscar = ctk.CTkEntry(barra, width=220,
                                placeholder_text="🔍  Buscar empleado...",
                                font=("Arial", 12), border_color="#cbd5e1")
    entry_buscar.pack(side="left", padx=12, pady=10)

    seccion_titulo(panel_izq, "📋 Personal Registrado")
    tabla = crear_tabla(panel_izq, _COLS, altura=12, anchos=_ANCHOS, expandir=True)

    # ── Panel derecho — formulario 8387rcPNz8SRX6pYXgdxCZg3VMLFwtdJB3Z9LeX8Ge2n
    panel_der = ctk.CTkFrame(layout, fg_color="transparent", width=340)
    panel_der.pack(side="right", fill="y")
    panel_der.pack_propagate(False)

    form_body = panel_formulario(panel_der, "➕ Registrar Nuevo Empleado")

    entry_id     = campo_texto(form_body,     "ID Empleado:",  "Ej: EMP002")
    entry_nombre = campo_texto(form_body,     "Nombre:",       "Nombre completo")
    combo_rol    = combo_opciones(form_body,  "Rol:",          _ROLES)
    entry_pwd    = campo_password(form_body,  "Contraseña:")

    estado = LabelEstado(form_body)

    # ── Nota informativa sobre roles ──────────────────────────────────────────
    nota = ctk.CTkFrame(form_body, fg_color="#f0f9ff", corner_radius=8)
    nota.pack(fill="x", pady=(8, 0))
    ctk.CTkLabel(nota,
                 text="ℹ  Roles: vendedor · supervisor · almacenista",
                 font=("Arial", 10), text_color="#0369a1").pack(
                     anchor="w", padx=10, pady=6)

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _limpiar_form():
        limpiar_campos(entry_id, entry_nombre, entry_pwd)
        combo_rol.set("")
        estado.limpiar()

    def _recargar_tabla(filtro: str = ""):
        limpiar(tabla)
        try:
            empleados = _DAO.obtener_todos()
        except Exception as e:
            msg_error("Error", str(e))
            return
        for emp in empleados:
            if (filtro.lower() in emp.nombre.lower()
                    or filtro.lower() in str(emp.id_usuario).lower()):
                tabla.insert("", "end", values=(
                    emp.id_usuario, emp.nombre, emp.rol
                ))

    def _registrar():
        id_emp   = entry_id.get().strip()
        nombre   = entry_nombre.get().strip()
        rol      = combo_rol.get().strip()
        password = entry_pwd.get().strip()

        # Validaciones básicas antes de construir el modelo
        for campo, val in [("ID", id_emp), ("Nombre", nombre),
                            ("Rol", rol), ("Contraseña", password)]:
            if not validar_no_vacio(val):
                estado.mostrar(f"El campo '{campo}' no puede estar vacío.", "error")
                return

        try:
            emp = Empleado(nombre, rol, password, id_emp)
            _DAO.insertar(emp)
            estado.mostrar("Empleado registrado correctamente.", "exito")
            _limpiar_form()
            _recargar_tabla()
        except ValidacionError as e:
            estado.mostrar(str(e), "error")
        except Exception as e:
            estado.mostrar(str(e), "error")

    def _eliminar():
        fila = fila_seleccionada(tabla)
        if not fila:
            estado.mostrar("Selecciona un empleado de la tabla.", "advertencia")
            return
        if not confirmar("Eliminar empleado",
                         f"¿Eliminar al empleado '{fila[1]}' permanentemente?"):
            return
        try:
            _DAO.eliminar(fila[0])
            exito("Eliminado", f"Empleado '{fila[1]}' eliminado.")
            _limpiar_form()
            _recargar_tabla()
        except Exception as e:
            msg_error("Error", str(e))

    def _cargar_en_form(event=None):
        fila = fila_seleccionada(tabla)
        if not fila:
            return
        limpiar_campos(entry_id, entry_nombre, entry_pwd)
        entry_id.insert(0, str(fila[0]))
        entry_nombre.insert(0, str(fila[1]))
        combo_rol.set(str(fila[2]))
        estado.mostrar(f"Datos del empleado ID {fila[0]} cargados.", "info")

    # Botones
    fila_btns = ctk.CTkFrame(form_body, fg_color="transparent")
    fila_btns.pack(fill="x", pady=(12, 0))
    btn_exito(fila_btns,     "💾 Registrar", _registrar, ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_peligro(fila_btns,   "🗑 Eliminar",  _eliminar,  ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_secundario(fila_btns, "✕ Limpiar",   _limpiar_form, ancho=100, alto=36).pack(side="left")

    entry_buscar.bind("<KeyRelease>", lambda e: _recargar_tabla(entry_buscar.get()))
    tabla.bind("<Double-1>", _cargar_en_form)

    _recargar_tabla()