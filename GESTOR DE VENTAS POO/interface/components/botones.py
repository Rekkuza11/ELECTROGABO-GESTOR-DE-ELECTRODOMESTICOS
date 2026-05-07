"""
Componente: Botones reutilizables.
Responsabilidad: fábrica de botones con el estilo visual unificado del sistema.
"""

import customtkinter as ctk


# ── Paleta centralizada ───────────────────────────────────────────────────────
_COLORES = {
    "primario":    ("#2563eb", "#1d4ed8"),
    "peligro":     ("#dc2626", "#b91c1c"),
    "exito":       ("#22c55e", "#16a34a"),
    "advertencia": ("#f97316", "#ea580c"),
    "secundario":  ("#f1f5f9", "#e2e8f0"),
    "gris":        ("#64748b", "#475569"),
}


def btn_primario(parent, texto: str, comando=None,
                 ancho: int = 160, alto: int = 38) -> ctk.CTkButton:
    """Botón de acción principal — azul."""
    fg, hover = _COLORES["primario"]
    return ctk.CTkButton(
        parent, text=texto, width=ancho, height=alto,
        fg_color=fg, hover_color=hover,
        text_color="white", font=("Arial", 12, "bold"),
        command=comando,
    )


def btn_peligro(parent, texto: str, comando=None,
                ancho: int = 160, alto: int = 38) -> ctk.CTkButton:
    """Botón destructivo — rojo."""
    fg, hover = _COLORES["peligro"]
    return ctk.CTkButton(
        parent, text=texto, width=ancho, height=alto,
        fg_color=fg, hover_color=hover,
        text_color="white", font=("Arial", 12, "bold"),
        command=comando,
    )


def btn_exito(parent, texto: str, comando=None,
              ancho: int = 160, alto: int = 38) -> ctk.CTkButton:
    """Botón de confirmación / guardar — verde."""
    fg, hover = _COLORES["exito"]
    return ctk.CTkButton(
        parent, text=texto, width=ancho, height=alto,
        fg_color=fg, hover_color=hover,
        text_color="white", font=("Arial", 12, "bold"),
        command=comando,
    )


def btn_advertencia(parent, texto: str, comando=None,
                    ancho: int = 160, alto: int = 38) -> ctk.CTkButton:
    """Botón de alerta — naranja."""
    fg, hover = _COLORES["advertencia"]
    return ctk.CTkButton(
        parent, text=texto, width=ancho, height=alto,
        fg_color=fg, hover_color=hover,
        text_color="white", font=("Arial", 12, "bold"),
        command=comando,
    )


def btn_secundario(parent, texto: str, comando=None,
                   ancho: int = 160, alto: int = 38) -> ctk.CTkButton:
    """Botón secundario — gris claro con borde."""
    fg, hover = _COLORES["secundario"]
    return ctk.CTkButton(
        parent, text=texto, width=ancho, height=alto,
        fg_color=fg, hover_color=hover,
        text_color="#1e293b", font=("Arial", 12),
        border_width=1, border_color="#cbd5e1",
        command=comando,
    )


def btn_menu(parent, texto: str, comando=None,
             activo: bool = False) -> ctk.CTkButton:
    """Botón de navegación lateral — resaltado si está activo."""
    fg = "#dbeafe" if activo else "transparent"
    text_color = "#2563eb" if activo else "#1e293b"
    weight = "bold" if activo else "normal"
    return ctk.CTkButton(
        parent, text=texto, width=180, height=40,
        fg_color=fg, hover_color="#f1f5f9",
        text_color=text_color,
        font=("Arial", 12, weight),
        anchor="w",
        command=comando,
    )


def btn_icono_texto(parent, icono: str, texto: str,
                    color: str, comando=None,
                    ancho: int = 120, alto: int = 36) -> ctk.CTkButton:
    """Botón compacto con ícono emoji + texto."""
    return ctk.CTkButton(
        parent, text=f"{icono}  {texto}",
        width=ancho, height=alto,
        fg_color=color, hover_color=color,
        text_color="white", font=("Arial", 11, "bold"),
        command=comando,
    )