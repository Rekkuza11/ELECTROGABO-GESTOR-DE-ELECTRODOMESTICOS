"""
Jerarquía de excepciones especializadas del dominio.
Principio SRP: cada excepción tiene una única responsabilidad semántica.
"""


# ─── Raíz del dominio ────────────────────────────────────────────────────────

class GestorVentasError(Exception):
    """Base de todas las excepciones del sistema. Nunca se lanza directamente."""

    def __init__(self, mensaje: str, codigo: int = 0):
        super().__init__(mensaje)
        self._mensaje = mensaje
        self._codigo = codigo

    @property
    def mensaje(self) -> str:
        return self._mensaje

    @property
    def codigo(self) -> int:
        return self._codigo

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] {self._mensaje}"


# ─── Excepciones de autenticación ────────────────────────────────────────────

class AutenticacionError(GestorVentasError):
    """Errores relacionados con el acceso y la identidad."""


class CredencialesInvalidasError(AutenticacionError):
    """Usuario o contraseña incorrectos."""

    def __init__(self, id_usuario: str):
        super().__init__(
            f"Credenciales inválidas para el usuario '{id_usuario}'.",
            codigo=401
        )
        self._id_usuario = id_usuario

    @property
    def id_usuario(self) -> str:
        return self._id_usuario


class PermisoInsuficienteError(AutenticacionError):
    """El usuario autenticado no tiene privilegios para esta acción."""

    def __init__(self, rol: str, accion: str):
        super().__init__(
            f"El rol '{rol}' no tiene permiso para ejecutar '{accion}'.",
            codigo=403
        )


class SesionInactivaError(AutenticacionError):
    """Se intentó realizar una operación sin sesión activa."""

    def __init__(self):
        super().__init__("No hay una sesión activa en el sistema.", codigo=401)


# ─── Excepciones de producto / inventario ────────────────────────────────────

class ProductoError(GestorVentasError):
    """Errores relacionados con productos."""


class ProductoNoEncontradoError(ProductoError):
    """El producto solicitado no existe en el inventario."""

    def __init__(self, id_producto):
        super().__init__(
            f"Producto con ID '{id_producto}' no encontrado.",
            codigo=404
        )
        self._id_producto = id_producto

    @property
    def id_producto(self):
        return self._id_producto


class StockInsuficienteError(ProductoError):
    """El stock disponible es menor a la cantidad solicitada."""

    def __init__(self, nombre_producto: str, stock_disponible: int, cantidad_solicitada: int):
        super().__init__(
            f"Stock insuficiente para '{nombre_producto}': "
            f"disponible={stock_disponible}, solicitado={cantidad_solicitada}.",
            codigo=409
        )
        self._stock_disponible = stock_disponible
        self._cantidad_solicitada = cantidad_solicitada

    @property
    def stock_disponible(self) -> int:
        return self._stock_disponible

    @property
    def cantidad_solicitada(self) -> int:
        return self._cantidad_solicitada


class PrecioInvalidoError(ProductoError):
    """Precio negativo o cero proporcionado."""

    def __init__(self, valor):
        super().__init__(
            f"El precio '{valor}' no es válido. Debe ser un número positivo.",
            codigo=422
        )


# ─── Excepciones de venta ─────────────────────────────────────────────────────

class VentaError(GestorVentasError):
    """Errores relacionados con ventas."""


class VentaNoEncontradaError(VentaError):
    """La venta solicitada no existe."""

    def __init__(self, id_venta):
        super().__init__(
            f"Venta con ID '{id_venta}' no encontrada.",
            codigo=404
        )


class VentaVaciaError(VentaError):
    """Se intentó confirmar una venta sin detalles."""

    def __init__(self):
        super().__init__("No se puede confirmar una venta sin productos.", codigo=422)


class DescuentoInvalidoError(VentaError):
    """Factor de descuento fuera del rango [0, 1]."""

    def __init__(self, descuento):
        super().__init__(
            f"Descuento '{descuento}' inválido. Debe estar entre 0.0 y 1.0.",
            codigo=422
        )


# ─── Excepciones de cliente ───────────────────────────────────────────────────

class ClienteError(GestorVentasError):
    """Errores relacionados con clientes."""


class ClienteNoEncontradoError(ClienteError):
    """El cliente solicitado no existe."""

    def __init__(self, id_cliente):
        super().__init__(
            f"Cliente con ID '{id_cliente}' no encontrado.",
            codigo=404
        )


class ClienteDuplicadoError(ClienteError):
    """Ya existe un cliente con ese identificador."""

    def __init__(self, id_cliente):
        super().__init__(
            f"Ya existe un cliente registrado con ID '{id_cliente}'.",
            codigo=409
        )


# ─── Excepciones de base de datos ────────────────────────────────────────────

class BaseDatosError(GestorVentasError):
    """Errores de infraestructura: conexión, consultas, integridad."""


class ConexionBaseDatosError(BaseDatosError):
    """No se pudo establecer conexión con la base de datos."""

    def __init__(self, detalle: str = ""):
        super().__init__(
            f"Error al conectar con la base de datos. {detalle}".strip(),
            codigo=503
        )


class IntegridadDatosError(BaseDatosError):
    """Violación de restricción de integridad referencial o unicidad."""

    def __init__(self, detalle: str):
        super().__init__(
            f"Violación de integridad de datos: {detalle}",
            codigo=409
        )


# ─── Excepciones de validación ───────────────────────────────────────────────

class ValidacionError(GestorVentasError):
    """Datos de entrada inválidos o incompletos."""

    def __init__(self, campo: str, razon: str):
        super().__init__(
            f"Campo '{campo}' inválido: {razon}",
            codigo=422
        )
        self._campo = campo

    @property
    def campo(self) -> str:
        return self._campo