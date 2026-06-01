"""
UTIL/security.py — Utilitario de seguridad para contraseñas.

CORRECCIÓN #6 (Fase 2): hashear() implementa HMAC-SHA256 con APP_SECRET.

CORRECCIÓN NE-2 (Fase 7) — Fallback para contraseñas sin migrar:
    La migración migrar_passwords.py debe ejecutarse en cada nuevo despliegue,
    pero si por algún motivo se omite (entorno de desarrollo recién clonado,
    restauración de backup antiguo, etc.), verificar() comparaba el HMAC del
    password ingresado contra el texto plano almacenado y devolvía False,
    bloqueando el acceso a todos los usuarios.

    Solución:
    - verificar() detecta si hash_guardado ES ya un hash (64 hex chars via
      es_hash()) o es texto plano (longitud distinta o chars no-hex).
    - Si es texto plano: comparación directa con hmac.compare_digest para
      mantener resistencia a timing attacks, y aviso en stderr para que el
      operador sepa que hay contraseñas sin migrar.
    - Si es hash: camino normal con HMAC.

    NOTA: el fallback NO es una puerta trasera — sigue siendo una comparación
    estricta. Solo evita que un despliegue sin migración bloquee el sistema.
    La solución definitiva siempre es ejecutar migrar_passwords.py.
"""

import hashlib
import hmac
import os
import sys

_APP_SECRET: str = os.environ.get("APP_SECRET", "electrogabo_2026_s3cr3t_k3y")


def hashear(password: str) -> str:
    """
    Genera el hash HMAC-SHA256 de una contraseña en texto plano.

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

    CORRECCIÓN NE-2 (Fase 7):
        Si hash_guardado no es un hash SHA-256 válido (es decir, la BD aún
        tiene contraseñas en texto plano porque no se ejecutó la migración),
        se realiza una comparación directa con hmac.compare_digest para
        evitar ataques de timing.  Se emite una advertencia a stderr para
        que el operador sepa que debe ejecutar migrar_passwords.py.

    Args:
        password_plano — contraseña ingresada por el usuario.
        hash_guardado  — valor almacenado en la BD (hash o texto plano).

    Returns:
        True si la contraseña coincide, False en caso contrario.
    """
    if not password_plano or not hash_guardado:
        return False

    try:
        if not es_hash(hash_guardado):
            # ── Fallback: contraseña sin migrar (texto plano en BD) ───────────
            # Advertencia visible en consola/logs para el operador del sistema.
            print(
                "[SECURITY WARNING] Contraseña sin hashear detectada en BD. "
                "Ejecute: python scripts/migrar_passwords.py",
                file=sys.stderr,
            )
            # Comparación de texto plano resistente a timing attacks
            return hmac.compare_digest(
                password_plano.encode("utf-8"),
                hash_guardado.encode("utf-8"),
            )

        # ── Camino normal: comparación con hash ───────────────────────────────
        hash_calculado = hashear(password_plano)
        return hmac.compare_digest(hash_calculado, hash_guardado)

    except Exception:
        return False


def es_hash(valor: str) -> bool:
    """
    Heurística: detecta si un valor ya es un hash SHA-256 (64 chars hex).
    Usada durante la migración para no hashear dos veces, y en verificar()
    para el fallback NE-2.
    """
    if not valor or not isinstance(valor, str):
        return False
    return len(valor) == 64 and all(c in "0123456789abcdef" for c in valor.lower())