"""
Componente: Tarjetas de estadística y encabezados de sección.
Responsabilidad: widgets reutilizables de presentación visual.
"""

import customtkinter as ctk


def tarjeta_stat(
    parent,
    icono: str,
    color_icono: str,
    valor: str,
    titulo: str,
    subtitulo: str,
    padx=(0, 10),
) -> ctk.CTkLabel:
    """
    Crea una tarjeta de estadística (igual al dashboard principal).
    Retorna la etiqueta del valor para poder actualizarla dinámicamente.
    """
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=160)
    card.pack(side="left", expand=True, fill="both", padx=padx)
    card.pack_propagate(False)

    ctk.CTkLabel(
        card, text=icono,
        font=("Arial", 20, "bold"),
        fg_color=color_icono, text_color="white",
        width=45, height=45, corner_radius=10,
    ).pack(anchor="w", padx=20, pady=(20, 10))

    lbl_valor = ctk.CTkLabel(
        card, text=valor,
        font=("Arial", 22, "bold"),
        text_color="#1e293b",
    )
    lbl_valor.pack(anchor="w", padx=20)

    ctk.CTkLabel(
        card, text=titulo,
        font=("Arial", 13, "bold"),
        text_color="#1e293b",
    ).pack(anchor="w", padx=20)

    ctk.CTkLabel(
        card, text=subtitulo,
        font=("Arial", 11),
        text_color="gray",
    ).pack(anchor="w", padx=20, pady=(0, 20))

    return lbl_valor


def fila_tarjetas(parent) -> ctk.CTkFrame:
    """Crea y retorna un frame horizontal transparente para contener tarjetas."""
    fila = ctk.CTkFrame(parent, fg_color="transparent")
    fila.pack(fill="x", padx=30, pady=(0, 10))
    return fila


def seccion_titulo(parent, texto: str) -> None:
    """Título de sección con separador horizontal."""
    ctk.CTkLabel(
        parent, text=texto,
        font=("Arial", 15, "bold"),
        text_color="#1e293b",
    ).pack(anchor="w", pady=(20, 6))
    ctk.CTkFrame(parent, height=1, fg_color="#e2e8f0").pack(fill="x", pady=(0, 8))


def panel_blanco(parent, esquinas: int = 12, pady=(0, 10)) -> ctk.CTkFrame:
    """Frame blanco con bordes redondeados — contenedor genérico."""
    frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=esquinas)
    frame.pack(fill="x", pady=pady)
    return frame


def cabecera_vista(parent, titulo: str, subtitulo: str) -> None:
    """Encabezado principal de una vista (título grande + subtítulo gris)."""
    ctk.CTkLabel(
        parent, text=titulo,
        font=("Arial", 26, "bold"),
        text_color="#1e293b",
    ).pack(anchor="w", padx=30, pady=(30, 5))

    ctk.CTkLabel(
        parent, text=subtitulo,
        font=("Arial", 13),
        text_color="gray",
    ).pack(anchor="w", padx=30, pady=(0, 20))


def badge(parent, texto: str, color_bg: str, color_texto: str) -> ctk.CTkLabel:
    """Etiqueta de estado tipo badge."""
    return ctk.CTkLabel(
        parent, text=f"  {texto}  ",
        font=("Arial", 11, "bold"),
        fg_color=color_bg, text_color=color_texto,
        corner_radius=6,
    )