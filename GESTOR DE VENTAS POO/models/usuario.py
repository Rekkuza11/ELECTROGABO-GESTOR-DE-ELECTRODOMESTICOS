"""
Clase base abstracta Usuario.
Principios aplicados:
  - OCP / LSP: define contrato para subclases sin imponer implementación.
  - Encapsulamiento: id y password son privados; se exponen sólo por propiedades.
"""

from abc import ABC, abstractmethod
from exceptions import ValidacionError


class Usuario(ABC):
    """
    Clase base para todos los usuarios del sistema.

    Atributos:
        __id_usuario  (privado)   — identificador único, inmutable tras creación.
        __password    (privado)   — credencial; sólo modificable mediante método dedicado.
    """

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, id_usuario, password: str):
        self.__id_usuario = id_usuario
        self.__password = self._validar_password(password)

    # ── Propiedades públicas de sólo lectura ──────────────────────────────────

    @property
    def id_usuario(self):
        """Identificador del usuario — sólo lectura."""
        return self.__id_usuario

    @property
    def password(self) -> str:
        """Contraseña actual — sólo lectura (hash)."""
        return self.__password

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def cambiar_password(self, nueva_password: str) -> None:
        """Actualiza la contraseña tras validación."""
        self.__password = self._validar_password(nueva_password)

    # ── Métodos protegidos (disponibles para subclases) ───────────────────────

    def _validar_password(self, password: str) -> str:
        """
        Regla mínima de seguridad.
        Protegido para que subclases puedan sobrescribir la política.
        """
        if not password or len(str(password).strip()) < 4:
            raise ValidacionError("password", "debe tener al menos 4 caracteres")
        return password

    # ── Métodos abstractos (contrato para subclases) ──────────────────────────

    @abstractmethod
    def mostrar(self) -> None:
        """Muestra la información del usuario por consola."""

    # ── Representación ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.__id_usuario}>"