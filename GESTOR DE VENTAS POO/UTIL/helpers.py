from datetime import datetime


def formatear_precio(valor):
    return f"${valor:,.0f}"


def formatear_moneda(valor):
    return f"${valor:,.2f}"


def obtener_fecha_actual():
    return datetime.now().strftime("%Y-%m-%d")


def validar_no_vacio(valor):
    return valor is not None and str(valor).strip() != ""


def convertir_a_float(valor):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return 0.0


def convertir_a_int(valor):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0


def es_numero_positivo(valor):
    try:
        return float(valor) > 0
    except (ValueError, TypeError):
        return False


def generar_id_simple(prefijo):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefijo}_{timestamp}"