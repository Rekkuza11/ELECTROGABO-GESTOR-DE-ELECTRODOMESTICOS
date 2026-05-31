"""
UTIL/security.py — Utilitario de seguridad para contraseñas.

CORRECCIÓN #6 — Contraseñas en texto plano:
    Este módulo centraliza toda la lógica de hashing de contraseñas.
    Se usa hashlib.sha256 con un salt fijo por aplicación (HMAC-like),
    lo que es significativamente más seguro que texto plano sin requerir
    librerías externas adicionales como bcrypt.

    Para una implementación de mayor seguridad en producción avanzada,
    se puede reemplazar el cuerpo de hashear() por bcrypt.hashpw(),
    sin cambiar ningún otro archivo del proyecto.

Uso:
    from UTIL.security import hashear, verificar

    hash_guardado = hashear("mi_password")      # al registrar / cambiar clave
    es_valido     = verificar("mi_password", hash_guardado)  # al hacer login
"""

import hashlib
import hmac
import os

# Salt de aplicación: se puede sobreescribir con variable de entorno APP_SECRET.
# No es un salt por-usuario (para eso se necesitaría bcrypt), pero es
# infinitamente mejor que texto plano.
_APP_SECRET: str = os.environ.get("APP_SECRET", "electrogabo_2026_s3cr3t_k3y")


def hashear(password: str) -> str:
    """
    Genera el hash SHA-256 (HMAC) de una contraseña en texto plano.

    Args:
        password — contraseña original del usuario.

    Returns:
        Cadena hexadecimal de 64 caracteres con el hash resultante.

    Raises:
        ValueError — si password está vacío o no es una cadena.
    """
    if not password or not isinstance(password, str):
        raise ValueError("La contraseña no puede estar vacía.")

    digest = hmac.new(
        _APP_SECRET.encode("utf-8"),
        password.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def verificar(password_plano: str, hash_guardado: str) -> bool:
    """
    Compara una contraseña en texto plano con su hash almacenado.
    Usa comparación segura (hmac.compare_digest) para prevenir ataques de timing.

    Args:
        password_plano — contraseña ingresada por el usuario.
        hash_guardado  — hash almacenado en la base de datos.

    Returns:
        True si la contraseña coincide con el hash, False en caso contrario.
    """
    if not password_plano or not hash_guardado:
        return False
    try:
        hash_calculado = hashear(password_plano)
        return hmac.compare_digest(hash_calculado, hash_guardado)
    except Exception:
        return False


def es_hash(valor: str) -> bool:
    """
    Heurística para detectar si un valor ya está hasheado (sha256 = 64 hex chars).
    Se usa durante la migración para no hashear dos veces.
    """
    if not valor or not isinstance(valor, str):
        return False
    return len(valor) == 64 and all(c in "0123456789abcdef" for c in valor.lower())
