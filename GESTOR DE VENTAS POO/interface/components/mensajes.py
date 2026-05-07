"""
Componente: Mensajes y diálogos.
Responsabilidad: centralizar la presentación de alertas, confirmaciones
y mensajes de estado al usuario.
"""

import customtkinter as ctk
from tkinter import messagebox


# ── Diálogos nativos (messagebox) ─────────────────────────────────────────────

def exito(titulo: str, mensaje: str) -> None:
    """Diálogo de éxito."""
    messagebox.showinfo(titulo, mensaje)


def error(titulo: str, mensaje: str) -> None:
    """Diálogo de error."""
    messagebox.showerror(titulo, mensaje)


def advertencia(titulo: str, mensaje: str) -> None:
    """Diálogo de advertencia."""
    messagebox.showwarning(titulo, mensaje)


def confirmar(titulo: str, mensaje: str) -> bool:
    """Diálogo de confirmación Sí/No. Retorna True si el usuario acepta."""
    return messagebox.askyesno(titulo, mensaje)


# ── Alertas inline (dentro de la interfaz) ────────────────────────────────────

_ESTILOS_ALERTA = {
    "exito":       ("#dcfce7", "#16a34a", "✓"),
    "error":       ("#fee2e2", "#dc2626", "✗"),
    "advertencia": ("#fef9c3", "#ca8a04", "⚠"),
    "info":        ("#dbeafe", "#1d4ed8", "ℹ"),
}


def alerta_inline(
    parent,
    texto: str,
    tipo: str = "info",
    pady: int = 5,
) -> ctk.CTkLabel:
    """
    Muestra una alerta estilizada dentro del frame padre.
    Tipos: 'exito', 'error', 'advertencia', 'info'.
    Retorna el label para poder destruirlo o actualizar su texto.
    """
    bg, fg, icono = _ESTILOS_ALERTA.get(tipo, ("#f1f5f9", "#1e293b", "•"))
    lbl = ctk.CTkLabel(
        parent,
        text=f"  {icono}  {texto}",
        font=("Arial", 11),
        text_color=fg,
        fg_color=bg,
        corner_radius=8,
        anchor="w",
    )
    lbl.pack(fill="x", pady=pady)
    return lbl


class LabelEstado:
    """
    Widget de estado dinámico: muestra mensajes de éxito/error
    dentro de un formulario sin abrir diálogos externos.
    """

    def __init__(self, parent, pady: int = 5):
        self._lbl = ctk.CTkLabel(
            parent,
            text="",
            font=("Arial", 11),
            text_color="gray",
            anchor="w",
        )
        self._lbl.pack(anchor="w", pady=pady)

    def mostrar(self, texto: str, tipo: str = "info") -> None:
        _, color, icono = _ESTILOS_ALERTA.get(tipo, ("#f1f5f9", "gray", "•"))
        self._lbl.configure(text=f"  {icono}  {texto}", text_color=color)

    def limpiar(self) -> None:
        self._lbl.configure(text="", text_color="gray")

    @property
    def widget(self) -> ctk.CTkLabel:
        return self._lbl