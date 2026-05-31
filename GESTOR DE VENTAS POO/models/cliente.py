"""
Modelo Cliente.
Aplica:
  - Encapsulamiento completo (private/protected/public).
  - Miembro estático: contador de instancias creadas.
  - Método de clase: fábrica desde tupla de BD.
  - Excepciones especializadas para validación.
"""

from models.usuario import Usuario
from exceptions import ValidacionError


class Cliente(Usuario):
    """
    Representa un cliente del sistema.

    Atributos de clase (estáticos):
        _total_clientes  — contador de instancias (protegido, compartido).

    Atributos de instancia:
        __nombre     (privado)
        __telefono   (privado)
        __direccion  (privado)
    """

    # ── Miembro estático de clase ─────────────────────────────────────────────
    _total_clientes: int = 0

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(
        self,
        nombre: str,
        telefono: str,
        direccion: str,
        password: str,
        id_cliente=None,
    ):
        super().__init__(id_cliente, password)
        self.__nombre = self._validar_nombre(nombre)
        self.__telefono = self._validar_telefono(telefono)
        self.__direccion = self._validar_direccion(direccion)
        Cliente._total_clientes += 1

    # ── Propiedades públicas ──────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = self._validar_nombre(valor)

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self.__telefono = self._validar_telefono(valor)

    @property
    def direccion(self) -> str:
        return self.__direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        self.__direccion = self._validar_direccion(valor)

    # ── Métodos de clase (fábricas) ───────────────────────────────────────────

    @classmethod
    def desde_fila_bd(cls, fila: tuple) -> "Cliente":
        """
        Método de clase: crea un Cliente a partir de una fila de BD.
        Orden esperado: (id_cliente, nombre, telefono, direccion, password_hash)
        """
        id_c, nombre, telefono, direccion, password = fila
        return cls(nombre, telefono, direccion, password, id_c)

    @classmethod
    def total_creados(cls) -> int:
        """Método de clase: retorna el contador global de clientes creados."""
        return cls._total_clientes

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def validar_telefono_formato(telefono: str) -> bool:
        """
        Método estático: verifica formato de teléfono colombiano.
        No requiere instancia ni acceso a la clase.
        """
        limpio = str(telefono).replace(" ", "").replace("-", "")
        return limpio.isdigit() and 7 <= len(limpio) <= 12

    # ── Métodos protegidos (validaciones reutilizables por subclases) ─────────

    def _validar_nombre(self, nombre: str) -> str:
        if not nombre or not nombre.strip():
            raise ValidacionError("nombre", "no puede estar vacío")
        return nombre.strip()

    def _validar_telefono(self, telefono: str) -> str:
        if not telefono or not str(telefono).strip():
            raise ValidacionError("telefono", "no puede estar vacío")
        return str(telefono).strip()

    def _validar_direccion(self, direccion: str) -> str:
        if not direccion or not str(direccion).strip():
            raise ValidacionError("direccion", "no puede estar vacía")
        return str(direccion).strip()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def mostrar(self) -> None:
        print(
            f"Cliente: {self.id_usuario} | {self.__nombre} | "
            f"{self.__telefono} | {self.__direccion}"
        )

    def __repr__(self) -> str:
        return f"<Cliente id={self.id_usuario} nombre={self.__nombre}>"