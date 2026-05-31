"""
Controller: Cliente.
Responsabilidad: mediar entre la vista de gestión de clientes y el ClienteDAO.
Aplica SRP — sólo orquesta operaciones CRUD sobre clientes.

CORRECCIONES — Fase 3:
  - #8: agregar() valida que id_cliente sea un entero positivo antes de
        enviarlo al DAO.  La columna usuario.id_usuario es int NOT NULL;
        pasar un string como 'CLI001' causaba error de tipo en la BD.
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

        CORRECCIÓN #8:
            id_cliente se convierte a int antes de persistir.
            La tabla usuario usa id_usuario int NOT NULL; un valor como
            'CLI001' era rechazado por el motor con error de tipo.
            Ahora se lanza ValidacionError con mensaje claro si el valor
            no es un entero positivo, antes de tocar la BD.

        Lanza:
            ValidacionError    — campo obligatorio vacío o ID no entero.
            ClienteDuplicadoError — el ID ya existe.
        """
        # Validar campos de texto obligatorios
        campos_texto = {
            "Nombre":    nombre,
            "Teléfono":  telefono,
            "Dirección": direccion,
        }
        for campo, valor in campos_texto.items():
            if not validar_no_vacio(valor):
                raise ValidacionError(campo, "no puede estar vacío")

        # CORRECCIÓN #8: id_cliente debe ser int positivo (int NOT NULL en BD)
        id_entero = self._validar_id_entero(id_cliente, "ID Cliente")

        if not password or len(str(password).strip()) < 4:
            raise ValidacionError("Contraseña", "debe tener al menos 4 caracteres")

        cliente = Cliente(
            nombre.strip(),
            telefono.strip(),
            direccion.strip(),
            password.strip(),
            id_entero,          # int — compatible con la columna int NOT NULL
        )
        self._dao.insertar(cliente)

    def eliminar(self, id_cliente) -> None:
        """
        Elimina un cliente por ID.
        Lanza ClienteNoEncontradoError si no existe.
        """
        self._dao.eliminar(id_cliente)

    # ── Validaciones privadas ─────────────────────────────────────────────────

    @staticmethod
    def _validar_id_entero(valor: str, campo: str) -> int:
        """
        Valida que `valor` sea un entero positivo.
        La BD define id_usuario/id_cliente como int NOT NULL.
        """
        try:
            v = int(str(valor).strip())
        except (ValueError, TypeError):
            raise ValidacionError(campo, "debe ser un número entero (ej: 443322)")
        if v <= 0:
            raise ValidacionError(campo, "debe ser mayor que cero")
        return v