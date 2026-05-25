"""
Dashboard Empleado.
Responsabilidad: ventana principal del panel de empleado.
- Menú lateral de navegación.
- Frame de contenido intercambiable.
- Carga dinámica de vistas (catálogo, ventas, clientes).
- El empleado NO puede eliminar ventas ya registradas.
"""

import customtkinter as ctk

from interface.components.cards import (
    cabecera_vista,
    tarjeta_stat,
    fila_tarjetas,
    seccion_titulo,
    panel_blanco,
)
from interface.components.botones import btn_menu
from interface.components.mensajes import alerta_inline
from UTIL.helpers import formatear_moneda


# ── Paleta y constantes ───────────────────────────────────────────────────────

_COLOR_SIDEBAR   = "white"
_COLOR_CONTENIDO = "#f1f5f9"
_COLOR_PRIMARIO  = "#0891b2"      # cian — diferencia al empleado del admin
_ANCHO_SIDEBAR   = 220


# ── Punto de entrada ──────────────────────────────────────────────────────────

def abrir_dashboard_empleado(app, id_usuario: str) -> None:
    """
    Oculta la ventana de login y abre el dashboard del empleado.

    Args:
        app        — instancia de App (ctk.CTk).
        id_usuario — ID del empleado autenticado.
    """
    app.withdraw()
    ventana = _VentanaDashboardEmpleado(app, id_usuario)
    ventana.mainloop()


# ── Ventana principal ─────────────────────────────────────────────────────────

class _VentanaDashboardEmpleado(ctk.CTkToplevel):
    """Toplevel del dashboard empleado."""

    def __init__(self, app, id_usuario: str):
        super().__init__()
        self._app        = app
        self._id_usuario = id_usuario

        self.title("ElectroGestión — Empleado")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self.configure(fg_color=_COLOR_CONTENIDO)

        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self._construir_layout()
        self._mostrar_inicio()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _construir_layout(self):
        self._sidebar = ctk.CTkFrame(
            self, fg_color=_COLOR_SIDEBAR,
            width=_ANCHO_SIDEBAR, corner_radius=0,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._construir_sidebar()

        self._contenido = ctk.CTkFrame(self, fg_color=_COLOR_CONTENIDO)
        self._contenido.pack(side="left", fill="both", expand=True)

    def _construir_sidebar(self):
        sb = self._sidebar

        # Marca
        ctk.CTkLabel(
            sb, text="⚡ ElectroGestión",
            font=("Arial", 15, "bold"),
            text_color=_COLOR_PRIMARIO,
        ).pack(pady=(24, 2), padx=16, anchor="w")

        ctk.CTkLabel(
            sb, text="Panel Empleado",
            font=("Arial", 11),
            text_color="gray",
        ).pack(padx=16, anchor="w")

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=12)

        # Perfil
        perfil = ctk.CTkFrame(sb, fg_color="#f0fdff", corner_radius=8)
        perfil.pack(fill="x", padx=10, pady=(0, 4))

        ctk.CTkLabel(
            perfil, text="Empleado",
            font=("Arial", 12, "bold"), text_color="#1e293b",
        ).pack(anchor="w", padx=10, pady=(8, 0))

        ctk.CTkLabel(
            perfil, text=f"ID: {self._id_usuario}",
            font=("Arial", 10), text_color="gray",
        ).pack(anchor="w", padx=10, pady=(0, 8))

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

        # Navegación
        self._botones_nav: dict[str, ctk.CTkButton] = {}

        nav = [
            ("🏠  Inicio",     self._mostrar_inicio),
            ("📦  Catálogo",   self._mostrar_catalogo),
            ("🛒  Ventas",     self._mostrar_ventas),
            ("👥  Clientes",   self._mostrar_clientes),
        ]

        for texto, comando in nav:
            btn = btn_menu(sb, texto, comando, activo=False)
            btn.pack(pady=2, padx=10)
            self._botones_nav[texto] = btn

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

        # Aviso de permisos
        aviso = ctk.CTkFrame(sb, fg_color="#f0f9ff", corner_radius=8)
        aviso.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(
            aviso,
            text="ℹ  Acceso de empleado.\nLas ventas registradas\nno pueden eliminarse.",
            font=("Arial", 9), text_color="#0369a1",
            justify="left",
        ).pack(anchor="w", padx=8, pady=8)

        # Cerrar sesión
        ctk.CTkButton(
            sb, text="🔒  Cerrar Sesión",
            width=180, height=40,
            fg_color="transparent", text_color="#dc2626",
            hover_color="#fee2e2", anchor="w",
            font=("Arial", 12),
            command=self._cerrar_sesion,
        ).pack(padx=10, pady=(0, 16), side="bottom")

    # ── Activación de botón del menú ──────────────────────────────────────────

    def _activar_nav(self, texto_boton: str):
        for txt, btn in self._botones_nav.items():
            activo = txt == texto_boton
            btn.configure(
                fg_color="#cffafe" if activo else "transparent",
                text_color=_COLOR_PRIMARIO if activo else "#1e293b",
                font=("Arial", 12, "bold" if activo else "normal"),
            )

    def _limpiar_contenido(self):
        for w in self._contenido.winfo_children():
            w.destroy()

    # ── Vistas de navegación ──────────────────────────────────────────────────

    def _mostrar_inicio(self):
        self._activar_nav("🏠  Inicio")
        self._limpiar_contenido()
        _vista_inicio_empleado(self._contenido, self._id_usuario)

    def _mostrar_catalogo(self):
        self._activar_nav("📦  Catálogo")
        self._limpiar_contenido()
        from interface.empleado.productos_view import abrir_catalogo_empleado
        abrir_catalogo_empleado(self._contenido)

    def _mostrar_ventas(self):
        self._activar_nav("🛒  Ventas")
        self._limpiar_contenido()
        from interface.empleado.ventas_view import abrir_ventas_empleado
        abrir_ventas_empleado(self._contenido, self._id_usuario)

    def _mostrar_clientes(self):
        self._activar_nav("👥  Clientes")
        self._limpiar_contenido()
        from interface.empleado.clientes_view import abrir_clientes_empleado
        abrir_clientes_empleado(self._contenido)

    # ── Sesión ────────────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        self.destroy()
        self._app.mostrar_login()

    def _cerrar(self):
        self.destroy()
        self._app.mostrar_login()


# ── Vista de Inicio del Empleado ──────────────────────────────────────────────

def _vista_inicio_empleado(parent: ctk.CTkFrame, id_usuario: str) -> None:
    """Panel de inicio con KPIs relevantes para el empleado."""

    cabecera_vista(parent,
                   "Panel de Empleado",
                   f"Bienvenido — ElectroGabo  ·  Sesión: {id_usuario}")

    try:
        from interface.controllers.reporte_controller import ReporteController
        ctrl    = ReporteController()
        datos   = ctrl.resumen_dashboard()
        alertas = ctrl.alertas_stock()
    except Exception:
        datos   = {}
        alertas = []

    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    fila1 = fila_tarjetas(parent)

    tarjeta_stat(
        fila1, "↗", "#22c55e",
        formatear_moneda(datos.get("ventas_hoy", 0.0)),
        "Ventas del Día",
        "Ingresos generados hoy",
    )
    tarjeta_stat(
        fila1, "🛒", "#0891b2",
        str(datos.get("total_ventas", 0)),
        "Total Ventas",
        "Transacciones registradas",
    )
    tarjeta_stat(
        fila1, "📦", "#a855f7",
        str(datos.get("total_productos", 0)),
        "Productos",
        "En catálogo activo",
        padx=(0, 0),
    )

    fila2 = fila_tarjetas(parent)

    tarjeta_stat(
        fila2, "👥", "#ec4899",
        str(datos.get("total_clientes", 0)),
        "Clientes",
        "Registrados en el sistema",
    )
    tarjeta_stat(
        fila2, "⚠", "#f97316",
        str(len(alertas)),
        "Alertas de Stock",
        "Productos con stock bajo",
    )
    tarjeta_stat(
        fila2, "$", "#2563eb",
        formatear_moneda(datos.get("ingresos_totales", 0.0)),
        "Ingresos Totales",
        "Acumulado histórico",
        padx=(0, 0),
    )

    # ── Alertas de inventario ─────────────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    seccion_titulo(scroll, "⚠  Alertas de Inventario")
    panel = panel_blanco(scroll, pady=(0, 12))

    if not alertas:
        alerta_inline(panel, "Inventario en niveles óptimos — sin alertas", tipo="exito")
    else:
        for id_p, nombre, marca, stock in alertas:
            tipo   = "error" if stock == 0 else "advertencia"
            estado = "AGOTADO" if stock == 0 else f"Stock restante: {stock}"
            alerta_inline(panel, f"[{id_p}] {nombre} ({marca}) — {estado}", tipo=tipo)

    ctk.CTkLabel(panel, text="", fg_color="transparent").pack(pady=4)