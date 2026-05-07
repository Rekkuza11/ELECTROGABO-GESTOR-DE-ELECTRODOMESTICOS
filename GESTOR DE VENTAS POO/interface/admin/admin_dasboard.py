"""
Dashboard Administrador.
Responsabilidad: ventana principal del panel administrador.
- Menú lateral de navegación.
- Frame de contenido intercambiable.
- Carga dinámica de vistas (productos, clientes, empleados, ventas, reportes).
- Usa únicamente componentes de interface/components/.
"""

import customtkinter as ctk

from interface.components.cards import (
    cabecera_vista,
    tarjeta_stat,
    fila_tarjetas,
    seccion_titulo,
    panel_blanco,
)
from interface.components.botones import btn_menu, btn_primario
from interface.components.mensajes import alerta_inline
from UTIL.helpers import formatear_moneda


# ── Paleta y constantes ───────────────────────────────────────────────────────

_COLOR_SIDEBAR   = "white"
_COLOR_CONTENIDO = "#f1f5f9"
_COLOR_PRIMARIO  = "#2563eb"
_ANCHO_SIDEBAR   = 220


# ── Punto de entrada ──────────────────────────────────────────────────────────

def abrir_dashboard(app, id_usuario: str = "admin") -> None:
    """
    Oculta la ventana de login y abre el dashboard del administrador.

    Args:
        app        — instancia de App (ctk.CTk), se oculta durante el dashboard.
        id_usuario — ID del administrador autenticado.
    """
    app.withdraw()

    ventana = _VentanaDashboard(app, id_usuario)
    ventana.mainloop()


# ── Ventana principal ─────────────────────────────────────────────────────────

class _VentanaDashboard(ctk.CTkToplevel):
    """Toplevel del dashboard administrador."""

    def __init__(self, app, id_usuario: str):
        super().__init__()
        self._app        = app
        self._id_usuario = id_usuario
        self._btn_activo : ctk.CTkButton | None = None

        self.title("ElectroGestión — Administrador")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self.configure(fg_color=_COLOR_CONTENIDO)

        # Al cerrar la ventana → volver al login
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self._construir_layout()
        self._mostrar_inicio()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _construir_layout(self):
        """Divide la ventana en sidebar + área de contenido."""
        # ── Sidebar ──
        self._sidebar = ctk.CTkFrame(
            self, fg_color=_COLOR_SIDEBAR,
            width=_ANCHO_SIDEBAR, corner_radius=0,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        self._construir_sidebar()

        # ── Contenido ──
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
            sb, text="Panel Administrador",
            font=("Arial", 11),
            text_color="gray",
        ).pack(padx=16, anchor="w")

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=12)

        # Perfil
        perfil = ctk.CTkFrame(sb, fg_color="#f1f5f9", corner_radius=8)
        perfil.pack(fill="x", padx=10, pady=(0, 4))

        ctk.CTkLabel(
            perfil, text="Administrador",
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
            ("📦  Productos",  self._mostrar_productos),
            ("👥  Clientes",   self._mostrar_clientes),
            ("👤  Empleados",  self._mostrar_empleados),
            ("🛒  Ventas",     self._mostrar_ventas),
            ("📈  Reportes",   self._mostrar_reportes),
        ]

        for texto, comando in nav:
            btn = btn_menu(sb, texto, comando, activo=False)
            btn.pack(pady=2, padx=10)
            self._botones_nav[texto] = btn

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

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
        """Resalta el botón activo y quita el resaltado de los demás."""
        for txt, btn in self._botones_nav.items():
            activo = txt == texto_boton
            btn.configure(
                fg_color="#dbeafe" if activo else "transparent",
                text_color=_COLOR_PRIMARIO if activo else "#1e293b",
                font=("Arial", 12, "bold" if activo else "normal"),
            )

    # ── Utilidad para limpiar el contenido ───────────────────────────────────

    def _limpiar_contenido(self):
        for w in self._contenido.winfo_children():
            w.destroy()

    # ── Vistas de navegación ──────────────────────────────────────────────────

    def _mostrar_inicio(self):
        self._activar_nav("🏠  Inicio")
        self._limpiar_contenido()
        _vista_inicio(self._contenido)

    def _mostrar_productos(self):
        self._activar_nav("📦  Productos")
        self._limpiar_contenido()
        from interface.admin.gestionar_productos import abrir_gestionar_productos
        abrir_gestionar_productos(self._contenido)

    def _mostrar_clientes(self):
        self._activar_nav("👥  Clientes")
        self._limpiar_contenido()
        from interface.admin.gestionar_clientes import abrir_gestionar_clientes
        abrir_gestionar_clientes(self._contenido)

    def _mostrar_empleados(self):
        self._activar_nav("👤  Empleados")
        self._limpiar_contenido()
        from interface.admin.gestionar_empleados import abrir_gestionar_empleados
        abrir_gestionar_empleados(self._contenido)

    def _mostrar_ventas(self):
        self._activar_nav("🛒  Ventas")
        self._limpiar_contenido()
        from interface.admin.gestionar_ventas import abrir_gestionar_ventas
        abrir_gestionar_ventas(self._contenido, self._id_usuario)

    def _mostrar_reportes(self):
        self._activar_nav("📈  Reportes")
        self._limpiar_contenido()
        from interface.admin.reportes_view import abrir_reportes_view
        abrir_reportes_view(self._contenido)

    # ── Sesión ────────────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        self.destroy()
        self._app.mostrar_login()

    def _cerrar(self):
        self.destroy()
        self._app.mostrar_login()


# ── Vista de Inicio ───────────────────────────────────────────────────────────

def _vista_inicio(parent: ctk.CTkFrame) -> None:
    """
    Renderiza el panel de inicio con KPIs y alertas de inventario.
    Usa exclusivamente los componentes de interface/components/.
    """
    # Encabezado
    cabecera_vista(parent,
                   "Dashboard Administrador",
                   "Resumen general del sistema — ElectroGabo")

    # Intentar cargar KPIs desde el ReporteController
    try:
        from interface.controllers.reporte_controller import ReporteController
        ctrl   = ReporteController()
        datos  = ctrl.resumen_dashboard()
        alertas = ctrl.alertas_stock()
    except Exception:
        datos   = {}
        alertas = []

    # ── Fila 1 de tarjetas ────────────────────────────────────────────────────
    fila1 = fila_tarjetas(parent)

    tarjeta_stat(
        fila1, "↗", "#22c55e",
        formatear_moneda(datos.get("ventas_hoy", 0.0)),
        "Ventas del Día",
        "Ingresos de hoy",
    )
    tarjeta_stat(
        fila1, "$", "#2563eb",
        formatear_moneda(datos.get("ingresos_totales", 0.0)),
        "Ingresos Totales",
        "Acumulado histórico",
    )
    tarjeta_stat(
        fila1, "📦", "#a855f7",
        str(datos.get("total_productos", 0)),
        "Productos",
        "En catálogo",
        padx=(0, 0),
    )

    # ── Fila 2 de tarjetas ────────────────────────────────────────────────────
    fila2 = fila_tarjetas(parent)

    tarjeta_stat(
        fila2, "👤", "#f97316",
        "—",
        "Empleados",
        "Personal activo",
    )
    tarjeta_stat(
        fila2, "👥", "#ec4899",
        str(datos.get("total_clientes", 0)),
        "Clientes",
        "Registrados",
    )
    tarjeta_stat(
        fila2, "🛒", "#06b6d4",
        str(datos.get("total_ventas", 0)),
        "Ventas Totales",
        "Transacciones",
        padx=(0, 0),
    )

    # ── Panel de alertas de inventario ────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    seccion_titulo(scroll, "⚠  Alertas de Inventario")

    panel = panel_blanco(scroll, pady=(0, 12))

    if not alertas:
        alerta_inline(panel, "Inventario en niveles óptimos", tipo="exito")
    else:
        for id_p, nombre, marca, stock in alertas:
            tipo   = "error" if stock == 0 else "advertencia"
            estado = "AGOTADO" if stock == 0 else f"Stock: {stock}"
            alerta_inline(panel, f"[{id_p}] {nombre} ({marca}) — {estado}", tipo=tipo)

    # Padding interior inferior
    ctk.CTkLabel(panel, text="", fg_color="transparent").pack(pady=4)