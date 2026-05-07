"""
Controller: Cliente.
Responsabilidad: mediar entre la vista de gestión de clientes y el ClienteDAO.
Aplica SRP — sólo orquesta operaciones CRUD sobre clientes.
"""

from dao.cliente_dao import ClienteDAO
from models.cliente import Cliente
from exceptions import (
    ClienteNoEncontradoError,
    ClienteDuplicadoError,
    BaseDatosError,
    ValidacionError,
)
from UTIL.helpers import validar_no_vacio


class ClienteController:
    """Coordina la lógica de negocio entre la vista y el DAO de Cliente."""

    def __init__(self):
        self._dao = ClienteDAO()

    # ── Consultas ─────────────────────────────────────────────────────────────

    def listar(self) -> list[Cliente]:
        """Retorna todos los clientes registrados."""
        return self._dao.obtener_todos()

    def obtener(self, id_cliente) -> Cliente:
        """
        Retorna un cliente por ID.
        Lanza ClienteNoEncontradoError si no existe.
        """
        return self._dao.obtener_por_id(id_cliente)

    # ── Mutaciones ────────────────────────────────────────────────────────────

    def agregar(
        self,
        id_cliente: str,
        nombre: str,
        telefono: str,
        direccion: str,
        password: str,
    ) -> None:
        """
        Valida y registra un nuevo cliente.
        Lanza ValidacionError si algún campo es inválido.
        Lanza ClienteDuplicadoError si el ID ya existe.
        """
        self._validar_campos(id_cliente, nombre, telefono, direccion, password)
        cliente = Cliente(
            nombre.strip(),
            telefono.strip(),
            direccion.strip(),
            password.strip(),
            id_cliente.strip(),
        )
        self._dao.insertar(cliente)

    def eliminar(self, id_cliente) -> None:
        """
        Elimina un cliente por ID.
        Lanza ClienteNoEncontradoError si no existe.
        """
        self._dao.eliminar(id_cliente)

    # ── Validación privada ────────────────────────────────────────────────────

    @staticmethod
    def _validar_campos(id_c, nombre, telefono, direccion, password) -> None:
        campos = {
            "ID Cliente": id_c,
            "Nombre":     nombre,
            "Teléfono":   telefono,
            "Dirección":  direccion,
            "Contraseña": password,
        }
        for campo, valor in campos.items():
            if not validar_no_vacio(valor):
                raise ValidacionError(campo, "no puede estar vacío")

        if len(str(password).strip()) < 4:
            raise ValidacionError("Contraseña", "debe tener al menos 4 caracteres")