"""
Vista: Navegación de Reportes.
Responsabilidad: presentar los tres módulos de reporte disponibles
y cargar cada uno dentro del frame de contenido.
"""

import customtkinter as ctk
from interface.components.cards import cabecera_vista
from interface.reportes.ventas_report import abrir_reporte_ventas
from interface.reportes.clientes_report import abrir_reporte_clientes
from interface.reportes.inventario_report import abrir_reporte_inventario


# ── Definición de los módulos de reporte disponibles ─────────────────────────
_MODULOS = [
    {
        "icono":     "📊",
        "color":     "#22c55e",
        "titulo":    "Reporte de Ventas",
        "desc":      "Ingresos, top productos, ticket promedio y ventas por empleado.",
        "funcion":   abrir_reporte_ventas,
    },
    {
        "icono":     "👥",
        "color":     "#ec4899",
        "titulo":    "Reporte de Clientes",
        "desc":      "Actividad, top clientes, clientes inactivos y gasto promedio.",
        "funcion":   abrir_reporte_clientes,
    },
    {
        "icono":     "📦",
        "color":     "#a855f7",
        "titulo":    "Reporte de Inventario",
        "desc":      "Estado del stock, alertas, margen por producto y valor total.",
        "funcion":   abrir_reporte_inventario,
    },
]


def abrir_reportes_view(parent: ctk.CTkFrame) -> None:
    """
    Limpia el frame padre y renderiza la pantalla de selección de reportes.
    Al hacer clic en un módulo, recarga el mismo frame con ese reporte.
    """
    _mostrar_selector(parent)


def _mostrar_selector(parent: ctk.CTkFrame) -> None:
    """Dibuja las tarjetas de selección de reporte."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "📈 Centro de Reportes",
                   "Selecciona el módulo que deseas consultar")

    contenedor = ctk.CTkScrollableFrame(parent, fg_color="#f1f5f9")
    contenedor.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Tarjetas de módulo ────────────────────────────────────────────────────
    for mod in _MODULOS:
        _tarjeta_reporte(contenedor, mod, parent)

    # ── Resumen rápido con KPIs ───────────────────────────────────────────────
    _panel_kpi_rapido(contenedor)


def _tarjeta_reporte(contenedor, mod: dict, parent: ctk.CTkFrame) -> None:
    """Crea una tarjeta clickeable para un módulo de reporte."""
    card = ctk.CTkFrame(contenedor, fg_color="white", corner_radius=14,
                        cursor="hand2")
    card.pack(fill="x", pady=(0, 12))

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=20, pady=18)

    # Ícono
    ctk.CTkLabel(inner, text=mod["icono"],
                 font=("Arial", 28),
                 fg_color=mod["color"], text_color="white",
                 width=60, height=60, corner_radius=12).pack(side="left", padx=(0, 18))

    # Texto
    texto = ctk.CTkFrame(inner, fg_color="transparent")
    texto.pack(side="left", fill="both", expand=True)

    ctk.CTkLabel(texto, text=mod["titulo"],
                 font=("Arial", 16, "bold"),
                 text_color="#1e293b", anchor="w").pack(anchor="w")
    ctk.CTkLabel(texto, text=mod["desc"],
                 font=("Arial", 12),
                 text_color="#64748b", anchor="w",
                 wraplength=480).pack(anchor="w", pady=(4, 0))

    # Botón
    ctk.CTkButton(inner, text="Ver reporte →",
                  width=130, height=36,
                  fg_color=mod["color"], hover_color=mod["color"],
                  text_color="white", font=("Arial", 12, "bold"),
                  command=lambda fn=mod["funcion"]: fn(parent)).pack(
                      side="right")

    # Toda la tarjeta también es clickeable
    def _abrir(event, fn=mod["funcion"]):
        fn(parent)
    card.bind("<Button-1>", _abrir)
    inner.bind("<Button-1>", _abrir)
    texto.bind("<Button-1>", _abrir)


def _panel_kpi_rapido(contenedor: ctk.CTkFrame) -> None:
    """Muestra un resumen ejecutivo rápido de los tres módulos."""
    from interface.controllers.reporte_controller import ReporteController

    panel = ctk.CTkFrame(contenedor, fg_color="white", corner_radius=14)
    panel.pack(fill="x", pady=(0, 12))

    header = ctk.CTkFrame(panel, fg_color="#f8fafc", corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(header, text="⚡ Resumen Ejecutivo",
                 font=("Arial", 14, "bold"), text_color="#1e293b").pack(
                     anchor="w", padx=20, pady=12)
    ctk.CTkFrame(panel, height=1, fg_color="#e2e8f0").pack(fill="x")

    try:
        ctrl = ReporteController()
        datos = ctrl.resumen_dashboard()
        alertas = ctrl.alertas_stock()
    except Exception:
        datos = {}
        alertas = []

    from UTIL.helpers import formatear_moneda

    kpis = [
        ("💰 Ingresos totales",  formatear_moneda(datos.get("ingresos_totales", 0))),
        ("🛒 Ventas registradas", str(datos.get("total_ventas", 0))),
        ("👥 Clientes activos",   str(datos.get("total_clientes", 0))),
        ("📦 Productos en catálogo", str(datos.get("total_productos", 0))),
        ("⚠ Alertas de stock",   str(len(alertas))),
    ]

    grid = ctk.CTkFrame(panel, fg_color="transparent")
    grid.pack(fill="x", padx=20, pady=15)

    for etiqueta, valor in kpis:
        fila = ctk.CTkFrame(grid, fg_color="#f8fafc", corner_radius=8)
        fila.pack(fill="x", pady=3)
        ctk.CTkLabel(fila, text=etiqueta,
                     font=("Arial", 12), text_color="#64748b",
                     anchor="w").pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(fila, text=valor,
                     font=("Arial", 12, "bold"), text_color="#1e293b",
                     anchor="e").pack(side="right", padx=12)