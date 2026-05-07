"""
Componente: Tablas Treeview estilizadas.
Responsabilidad: crear y gestionar tablas con el estilo visual unificado.
"""

import customtkinter as ctk
from tkinter import ttk

_ESTILO = "ElectroGabo.Treeview"


def _aplicar_estilo() -> None:
    """Configura el estilo ttk una sola vez."""
    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure(
        _ESTILO,
        background="white",
        foreground="#1e293b",
        rowheight=32,
        fieldbackground="white",
        font=("Arial", 11),
    )
    estilo.configure(
        f"{_ESTILO}.Heading",
        background="#f1f5f9",
        foreground="#64748b",
        font=("Arial", 11, "bold"),
    )
    estilo.map(_ESTILO, background=[("selected", "#dbeafe")])


def crear_tabla(
    parent,
    columnas: tuple,
    altura: int = 8,
    anchos: list = None,
    expandir: bool = True,
) -> ttk.Treeview:
    """
    Crea un Treeview estilizado dentro de un frame blanco.
    Retorna la tabla para manejarla desde el exterior.

    Args:
        columnas  — nombres de columnas.
        altura    — número de filas visibles.
        anchos    — lista de anchos por columna (opcional).
        expandir  — si el frame debe expandirse verticalmente.
    """
    _aplicar_estilo()

    frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
    modo_expand = "both" if expandir else "x"
    frame.pack(fill=modo_expand, expand=expandir, pady=(0, 10))

    tabla = ttk.Treeview(
        frame,
        columns=columnas,
        show="headings",
        style=_ESTILO,
        height=altura,
    )

    for i, col in enumerate(columnas):
        tabla.heading(col, text=col)
        w = anchos[i] if (anchos and i < len(anchos)) else 140
        tabla.column(col, anchor="center", width=w)

    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll_y.set)

    tabla.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll_y.pack(side="right", fill="y", pady=10)

    return tabla


# ── Helpers de gestión ────────────────────────────────────────────────────────

def limpiar(tabla: ttk.Treeview) -> None:
    """Elimina todas las filas de la tabla."""
    for item in tabla.get_children():
        tabla.delete(item)


def fila_seleccionada(tabla: ttk.Treeview) -> list | None:
    """
    Retorna los valores de la fila seleccionada como lista,
    o None si no hay selección.
    """
    seleccion = tabla.selection()
    if not seleccion:
        return None
    return list(tabla.item(seleccion[0])["values"])


def insertar_fila(tabla: ttk.Treeview, valores: tuple, etiqueta: str = "") -> None:
    """Inserta una fila al final de la tabla."""
    tabla.insert("", "end", values=valores, tags=(etiqueta,))


def colorear_filas(tabla: ttk.Treeview,
                   color_par: str = "#f8fafc",
                   color_impar: str = "white") -> None:
    """Aplica colores alternados a las filas para facilitar la lectura."""
    for i, item in enumerate(tabla.get_children()):
        tag = "par" if i % 2 == 0 else "impar"
        tabla.item(item, tags=(tag,))
    tabla.tag_configure("par",   background=color_par)
    tabla.tag_configure("impar", background=color_impar)