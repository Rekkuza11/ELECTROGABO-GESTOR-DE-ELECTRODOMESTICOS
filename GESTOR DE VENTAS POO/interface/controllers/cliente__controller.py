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

    def listar(self) -> list:
        """Retorna todos los clientes registrados."""
        return self._dao.obtener_todos()

    def obtener(self, id_cliente) -> Cliente:
        """
        Retorna un cliente por ID.
        Lanza ClienteNoEncontradoError si no existe.
        """
        return self._dao.obtener_por_id(id_cliente)

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
        El password puede ser generado automáticamente por la vista (admin)
        o ingresado directamente por el cliente en su propio portal.
        Lanza ValidacionError si algún campo obligatorio está vacío.
        Lanza ClienteDuplicadoError si el ID ya existe.
        """
        # Validar sólo campos visibles al admin — password viene siempre del sistema
        campos_obligatorios = {
            "ID Cliente": id_cliente,
            "Nombre":     nombre,
            "Teléfono":   telefono,
            "Dirección":  direccion,
        }
        for campo, valor in campos_obligatorios.items():
            if not validar_no_vacio(valor):
                raise ValidacionError(campo, "no puede estar vacío")

        # El password viene generado; mínimo seguro de 4 chars
        if not password or len(str(password).strip()) < 4:
            raise ValidacionError("Contraseña", "debe tener al menos 4 caracteres")

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
