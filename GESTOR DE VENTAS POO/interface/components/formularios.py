"""
Componente: Formularios reutilizables.
Responsabilidad: construir campos de entrada con etiqueta alineada,
manteniendo el estilo visual del sistema.
"""

import customtkinter as ctk


# ── Campos individuales ───────────────────────────────────────────────────────

def campo_texto(
    parent,
    etiqueta: str,
    placeholder: str = "",
    ancho: int = 280,
    ancho_etiqueta: int = 130,
) -> ctk.CTkEntry:
    """Campo de texto estándar con etiqueta a la izquierda."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        frame, text=etiqueta,
        font=("Arial", 12), text_color="#475569",
        width=ancho_etiqueta, anchor="w",
    ).pack(side="left")

    entry = ctk.CTkEntry(
        frame, width=ancho,
        placeholder_text=placeholder,
        font=("Arial", 12),
        border_color="#cbd5e1",
    )
    entry.pack(side="left", padx=(10, 0))
    return entry


def campo_password(
    parent,
    etiqueta: str,
    ancho: int = 280,
    ancho_etiqueta: int = 130,
) -> ctk.CTkEntry:
    """Campo de contraseña con texto oculto."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        frame, text=etiqueta,
        font=("Arial", 12), text_color="#475569",
        width=ancho_etiqueta, anchor="w",
    ).pack(side="left")

    entry = ctk.CTkEntry(
        frame, width=ancho,
        show="*", font=("Arial", 12),
        border_color="#cbd5e1",
    )
    entry.pack(side="left", padx=(10, 0))
    return entry


def campo_numero(
    parent,
    etiqueta: str,
    placeholder: str = "0",
    ancho: int = 140,
    ancho_etiqueta: int = 130,
) -> ctk.CTkEntry:
    """Campo numérico (validación en controller)."""
    return campo_texto(parent, etiqueta, placeholder, ancho, ancho_etiqueta)


def combo_opciones(
    parent,
    etiqueta: str,
    opciones: list,
    ancho: int = 280,
    ancho_etiqueta: int = 130,
) -> ctk.CTkComboBox:
    """ComboBox con etiqueta alineada."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=5)

    ctk.CTkLabel(
        frame, text=etiqueta,
        font=("Arial", 12), text_color="#475569",
        width=ancho_etiqueta, anchor="w",
    ).pack(side="left")

    combo = ctk.CTkComboBox(
        frame, values=opciones, width=ancho,
        font=("Arial", 12),
        border_color="#cbd5e1",
        button_color="#2563eb",
        dropdown_hover_color="#dbeafe",
    )
    combo.pack(side="left", padx=(10, 0))
    return combo


# ── Contenedor de formulario ──────────────────────────────────────────────────

def panel_formulario(parent, titulo: str, pady=(0, 15)) -> ctk.CTkFrame:
    """
    Crea un panel blanco con encabezado para agrupar campos.
    Retorna el frame interno donde se colocan los campos.
    """
    outer = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)
    outer.pack(fill="x", pady=pady, padx=0)

    # Encabezado del panel
    header = ctk.CTkFrame(outer, fg_color="#f8fafc", corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(
        header, text=titulo,
        font=("Arial", 13, "bold"), text_color="#1e293b",
    ).pack(anchor="w", padx=20, pady=12)
    ctk.CTkFrame(outer, height=1, fg_color="#e2e8f0").pack(fill="x")

    # Cuerpo del panel
    body = ctk.CTkFrame(outer, fg_color="transparent")
    body.pack(fill="x", padx=20, pady=15)
    return body


def limpiar_campos(*entries) -> None:
    """Limpia el contenido de todos los campos recibidos."""
    for entry in entries:
        if isinstance(entry, ctk.CTkEntry):
            entry.delete(0, "end")
        elif isinstance(entry, ctk.CTkComboBox):
            entry.set("")


def rellenar_campos(valores: dict) -> None:
    """
    Rellena campos a partir de un diccionario {entry_widget: valor}.
    """
    for entry, valor in valores.items():
        if isinstance(entry, ctk.CTkEntry):
            entry.delete(0, "end")
            entry.insert(0, str(valor))
        elif isinstance(entry, ctk.CTkComboBox):
            entry.set(str(valor))