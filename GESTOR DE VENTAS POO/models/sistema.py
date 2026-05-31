"""
LEGACY / DESCONECTADO — models/sistema.py
Fase 6 · Corrección #16.

Esta clase gestiona la sesión EN MEMORIA mediante un Singleton.
El flujo real del sistema usa AuthController + DatabaseConnection
para autenticar contra la base de datos.

Este módulo NO es invocado por ningún controller, DAO ni vista activa.
Se conserva como referencia de diseño OOP pero NO debe usarse en producción.

Autenticación real:
    from interface.controllers.auth_controller import AuthController
    AuthController().login(usuario, password)
"""

import warnings
warnings.warn(
    "models.sistema está desconectado del flujo real. "
    "Usa interface.controllers.auth_controller.AuthController para autenticación.",
    DeprecationWarning,
    stacklevel=2,
)

import threading
from exceptions import CredencialesInvalidasError, SesionInactivaError


class Sistema:
    """
    [LEGACY] Núcleo de autenticación en memoria. Singleton.
    Ver advertencia del módulo — no usar en código nuevo.
    """

    _instancia: "Sistema | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "Sistema":
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    obj = super().__new__(cls)
                    obj.__dict__["_Sistema__usuarios"] = {}
                    obj.__dict__["_Sistema__usuario_actual"] = None
                    cls._instancia = obj
        return cls._instancia

    @classmethod
    def instancia(cls) -> "Sistema":
        return cls()

    def agregar_usuario(self, usuario) -> None:
        self.__usuarios[usuario.id_usuario] = usuario

    def mostrar_usuarios(self) -> None:
        for usuario in self.__usuarios.values():
            usuario.mostrar()

    def login(self, id_usuario, password) -> bool:
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
        if self.__usuario_actual is None:
            raise SesionInactivaError()
        return self.__usuario_actual

    def __repr__(self) -> str:
        u = self.__usuario_actual
        return f"<Sistema [LEGACY] sesion={u.id_usuario if u else None}>"