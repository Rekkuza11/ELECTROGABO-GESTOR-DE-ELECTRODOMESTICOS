"""
Modelo Sistema — Singleton.
Responsabilidad única: gestionar el ciclo de sesión (login/logout).
Aplica:
  - Patrón Singleton.
  - Encapsulamiento: __usuarios y __usuario_actual privados.
  - Excepciones especializadas de autenticación.
"""

import threading
from exceptions import CredencialesInvalidasError, SesionInactivaError


class Sistema:
    """
    Núcleo del sistema de autenticación. Singleton.

    Atributos de clase:
        _instancia (privado)
        _lock      (privado)

    Atributos de instancia:
        __usuarios        (privado) — diccionario id → usuario.
        __usuario_actual  (privado) — usuario autenticado actualmente.
    """

    _instancia: "Sistema | None" = None
    _lock: threading.Lock = threading.Lock()

    # ── Singleton ─────────────────────────────────────────────────────────────

    def __new__(cls) -> "Sistema":
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    obj = super().__new__(cls)
                    obj.__dict__["_Sistema__usuarios"] = {}
                    obj.__dict__["_Sistema__usuario_actual"] = None
                    cls._instancia = obj
        return cls._instancia

    # ── Métodos de clase ──────────────────────────────────────────────────────

    @classmethod
    def instancia(cls) -> "Sistema":
        return cls()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def agregar_usuario(self, usuario) -> None:
        """Registra un usuario en el sistema (admin operation)."""
        self.__usuarios[usuario.id_usuario] = usuario

    def mostrar_usuarios(self) -> None:
        for usuario in self.__usuarios.values():
            usuario.mostrar()

    def login(self, id_usuario, password) -> bool:
        """
        Intenta autenticar al usuario.
        Lanza CredencialesInvalidasError si las credenciales son incorrectas.
        Retorna True si el login fue exitoso.
        """
        usuario = self.__usuarios.get(id_usuario)
        if usuario and usuario.password == password:
            self.__usuario_actual = usuario
            print(f"Acceso concedido: {id_usuario}")
            return True
        raise CredencialesInvalidasError(id_usuario)

    def logout(self) -> None:
        self.__usuario_actual = None
        print("Sesión cerrada.")

    @property
    def usuario_actual(self):
        return self.__usuario_actual

    def requerir_sesion(self):
        """
        Verifica que haya una sesión activa.
        Lanza SesionInactivaError si no hay usuario autenticado.
        """
        if self.__usuario_actual is None:
            raise SesionInactivaError()
        return self.__usuario_actual

    def __repr__(self) -> str:
        u = self.__usuario_actual
        return f"<Sistema usuarios={len(self.__usuarios)} sesion={u.id_usuario if u else None}>"