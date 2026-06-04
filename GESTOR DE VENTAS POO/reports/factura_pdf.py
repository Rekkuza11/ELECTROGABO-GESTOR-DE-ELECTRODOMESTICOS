# reports/factura_pdf.py
import unicodedata
from fpdf import FPDF
from UTIL.helpers import formatear_moneda


class FacturaPDF:

    def __init__(self, empresa: dict):
        """
        Args:
            empresa — dict con claves: nombre, nit, direccion, ciudad,
                      telefono, regimen.  Ver UTIL/config_empresa.py.
        """
        self._empresa = empresa

    # ── Normalización de texto ────────────────────────────────────────────────

    @staticmethod
    def _txt(texto) -> str:
        """
        Convierte cualquier valor a str ASCII puro compatible con Helvetica.
        Elimina tildes, eñes y símbolos Unicode que fpdf2 no soporta en
        fuentes estándar (Helvetica, Courier, Times).
        Ejemplo: 'Dirección' → 'Direccion', '—' → '-'
        """
        s = str(texto)
        # Descompone caracteres acentuados (NFD) y descarta los diacríticos
        s = unicodedata.normalize("NFD", s)
        s = s.encode("ascii", "ignore").decode("ascii")
        # Reemplazos manuales de símbolos que NFD no resuelve
        s = s.replace("\u2014", "-").replace("\u2013", "-").replace("\u00b0", "o")
        return s

    # ── API pública ───────────────────────────────────────────────────────────

    def generar(self, venta: dict, detalles: list, ruta_salida: str) -> str:
        """
        Genera el PDF de la factura y lo guarda en ruta_salida.
        Retorna la ruta del archivo generado.

        Args:
            venta    — dict con id_venta, fecha, total, cliente (dict), empleado
            detalles — lista de (nombre, cantidad, precio_unitario, subtotal)
            ruta_salida — carpeta donde guardar el PDF
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        self._encabezado(pdf, venta["id_venta"], venta["fecha"])
        self._datos_empresa(pdf)
        self._datos_cliente(pdf, venta["cliente"])
        self._tabla_productos(pdf, detalles)
        self._totales(pdf, venta["total"])
        self._pie(pdf)

        nombre_archivo = f"{ruta_salida}/Factura_{venta['id_venta']}.pdf"
        pdf.output(nombre_archivo)
        return nombre_archivo

    # ── Secciones internas ────────────────────────────────────────────────────

    def _encabezado(self, pdf, id_venta, fecha):
        pdf.set_fill_color(31, 56, 100)
        pdf.rect(0, 0, 210, 30, "F")
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, "FACTURA DE VENTA", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"No. {id_venta:06d}   |   {str(fecha)[:10]}", ln=True, align="C")
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)

    def _datos_empresa(self, pdf):
        e = self._empresa
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 6, self._txt(e["nombre"]), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, f"NIT: {self._txt(e['nit'])}", ln=True)
        pdf.cell(0, 5, f"{self._txt(e['direccion'])} - {self._txt(e['ciudad'])}", ln=True)
        pdf.cell(0, 5, f"Tel: {self._txt(e['telefono'])}", ln=True)
        pdf.cell(0, 5, self._txt(e["regimen"]), ln=True)
        pdf.ln(4)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    def _datos_cliente(self, pdf, cliente):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "DATOS DEL CLIENTE", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, f"Nombre: {self._txt(cliente['nombre'])}", ln=True)
        pdf.cell(0, 5,
                 f"Tel: {self._txt(cliente['telefono'])}"
                 f"   Direccion: {self._txt(cliente['direccion'])}",
                 ln=True)
        pdf.ln(4)

    def _tabla_productos(self, pdf, detalles):
        pdf.set_fill_color(31, 56, 100)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(80, 7, "Producto",     border=1, fill=True)
        pdf.cell(25, 7, "Cant.",        border=1, fill=True, align="C")
        pdf.cell(40, 7, "Precio Unit.", border=1, fill=True, align="R")
        pdf.cell(45, 7, "Subtotal",     border=1, fill=True, align="R", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        for i, (nombre, cant, precio, sub) in enumerate(detalles):
            fill = i % 2 == 0
            if fill:
                pdf.set_fill_color(238, 243, 251)
            pdf.cell(80, 6, self._txt(nombre),              border=1, fill=fill)
            pdf.cell(25, 6, str(cant),                      border=1, fill=fill, align="C")
            pdf.cell(40, 6, formatear_moneda(float(precio)),border=1, fill=fill, align="R")
            pdf.cell(45, 6, formatear_moneda(float(sub)),   border=1, fill=fill, align="R", ln=True)
        pdf.ln(3)

    def _totales(self, pdf, total):
        total_f = float(total)
        iva     = round(total_f * 0.19, 2)
        base    = round(total_f - iva, 2)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(145); pdf.cell(20, 6, "Base:",    align="R")
        pdf.cell(25, 6, formatear_moneda(base),    align="R", ln=True)
        pdf.cell(145); pdf.cell(20, 6, "IVA 19%:", align="R")
        pdf.cell(25, 6, formatear_moneda(iva),     align="R", ln=True)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(145); pdf.cell(20, 7, "TOTAL:",   align="R")
        pdf.cell(25, 7, formatear_moneda(total_f), align="R", ln=True)
        pdf.ln(4)

    def _pie(self, pdf):
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(130, 130, 130)
        pdf.cell(0, 5,
                 "Generado por ElectroGestion - Gracias por su compra.",
                 align="C", ln=True)