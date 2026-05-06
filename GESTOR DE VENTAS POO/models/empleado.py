"""
Modelo Empleado.
Aplica:
  - Encapsulamiento: nombre y rol privados.
  - Miembro estático: roles permitidos y contador de empleados.
  - Método de clase: fábrica desde fila de BD.
  - Excepción especializada para rol inválido.
"""

from models.usuario import Usuario
from exceptions import ValidacionError


class Empleado(Usuario):
    """
    Representa a un empleado del sistema.

    Atributos de clase (estáticos):
        ROLES_PERMITIDOS  — conjunto inmutable de roles válidos (público).
        _total_empleados  — contador de instancias (protegido).

    Atributos de instancia:
        __nombre   (privado)
        __rol      (privado)
    """

    # ── Miembros estáticos de clase ───────────────────────────────────────────
    ROLES_PERMITIDOS: frozenset = frozenset({"vendedor", "supervisor", "almacenista"})
    _total_empleados: int = 0

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(
        self,
        nombre: str,
        rol: str,
        password: str,
        id_empleado=None,
    ):
        super().__init__(id_empleado, password)
        self.__nombre = self._validar_nombre(nombre)
        self.__rol = self._validar_rol(rol)
        Empleado._total_empleados += 1

    # ── Propiedades públicas ──────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = self._validar_nombre(valor)

    @property
    def rol(self) -> str:
        return self.__rol

    @rol.setter
    def rol(self, valor: str) -> None:
        self.__rol = self._validar_rol(valor)

    # ── Métodos de clase ──────────────────────────────────────────────────────

    @classmethod
    def desde_fila_bd(cls, fila: tuple) -> "Empleado":
        """Fábrica: (id_empleado, nombre, rol, password_hash)"""
        id_e, nombre, rol, password = fila
        return cls(nombre, rol, password, id_e)

    @classmethod
    def total_creados(cls) -> int:
        """Retorna el número total de empleados creados."""
        return cls._total_empleados

    @classmethod
    def agregar_rol(cls, nuevo_rol: str) -> None:
        """Extiende los roles permitidos (requiere redefinir frozenset)."""
        cls.ROLES_PERMITIDOS = cls.ROLES_PERMITIDOS | {nuevo_rol.lower()}

    # ── Métodos estáticos ────────────────────────────────────────────────────

    @staticmethod
    def es_rol_valido(rol: str) -> bool:
        """Verifica si un rol pertenece a los roles permitidos."""
        return rol.lower() in Empleado.ROLES_PERMITIDOS

    # ── Métodos protegidos ────────────────────────────────────────────────────

    def _validar_nombre(self, nombre: str) -> str:
        if not nombre or not nombre.strip():
            raise ValidacionError("nombre", "no puede estar vacío")
        return nombre.strip()

    def _validar_rol(self, rol: str) -> str:
        rol_lower = str(rol).lower().strip()
        if rol_lower not in self.ROLES_PERMITIDOS:
            raise ValidacionError(
                "rol",
                f"'{rol}' no es válido. Roles aceptados: {sorted(self.ROLES_PERMITIDOS)}"
            )
        return rol_lower

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def mostrar(self) -> None:
        print(f"Empleado: {self.id_usuario} | {self.__nombre} | {self.__rol}")

    def __repr__(self) -> str:
        return f"<Empleado id={self.id_usuario} nombre={self.__nombre} rol={self.__rol}>"