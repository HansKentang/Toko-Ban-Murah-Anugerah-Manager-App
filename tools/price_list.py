"""
Price List Generator - Toko Ban Murah Anugerah
===============================================
Generate professional PDF price lists and promo flyers.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from fpdf import FPDF
    _has_fpdf = True
except ImportError:
    _has_fpdf = False

try:
    from PIL import Image, ImageDraw, ImageFont
    _has_pillow = True
except ImportError:
    _has_pillow = False


class PriceListGenerator:
    """Generate PDF price lists and promo flyers for tire shop."""

    def __init__(self, business_name: str = "Toko Ban Murah Anugerah",
                 output_dir: str = "../output/price_lists"):
        self.business_name = business_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ─── PDF Price List ──────────────────────────────────────────────────
    def generate_pdf(self, products: list, title: str = "DAFTAR HARGA BAN",
                     filename: Optional[str] = None) -> Optional[str]:
        """Generate a professional PDF price list."""
        if not _has_fpdf:
            return None

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        # Header
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 15, self.business_name, new_x="LMARGIN", new_y="NEXT", 
                 align="C")
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Update: {datetime.now().strftime('%d %B %Y')}", 
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # Table Header
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        
        col_widths = [50, 40, 30, 35, 35]  # Merek, Ukuran, Ring, Harga, Stok
        headers = ["MEREK", "UKURAN", "RING", "HARGA", "STOK"]
        
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
        pdf.ln()

        # Table Body
        pdf.set_font("Helvetica", "", 9)
        for i, prod in enumerate(products):
            if i % 2 == 0:
                pdf.set_fill_color(230, 240, 255)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            pdf.set_text_color(0, 0, 0)
            
            merek = prod.get("Merek", "-")[:20]
            ukuran = prod.get("Ukuran", "-")[:15]
            ring = str(prod.get("Ring", "-"))
            harga = f"Rp {prod.get('Harga Jual', 0):,.0f}"
            stok = str(prod.get("Stok", 0))
            
            pdf.cell(col_widths[0], 7, merek, border=1, fill=True, align="C")
            pdf.cell(col_widths[1], 7, ukuran, border=1, fill=True, align="C")
            pdf.cell(col_widths[2], 7, ring, border=1, fill=True, align="C")
            pdf.cell(col_widths[3], 7, harga, border=1, fill=True, align="C")
            pdf.cell(col_widths[4], 7, stok, border=1, fill=True, align="C")
            pdf.ln()

        # Footer
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 7, "*Harga dapat berubah sewaktu-waktu tanpa pemberitahuan", 
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 7, "Hubungi kami untuk info lebih lanjut.", 
                 new_x="LMARGIN", new_y="NEXT", align="C")

        # Save
        if not filename:
            filename = f"price_list_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        filepath = self.output_dir / filename
        pdf.output(str(filepath))
        return str(filepath)

    # ─── Promo Flyer (Image) ────────────────────────────────────────────
    def generate_flyer(self, promo_text: str, price: str = "",
                       filename: Optional[str] = None) -> Optional[str]:
        """Generate a promo flyer image for social media."""
        if not _has_pillow:
            return None

        width, height = 1080, 1080  # Instagram square
        img = Image.new("RGB", (width, height), color=(0, 51, 102))
        draw = ImageDraw.Draw(img)

        # Try to load font, fallback to default
        try:
            font_large = ImageFont.truetype("arial.ttf", 72)
            font_medium = ImageFont.truetype("arial.ttf", 48)
            font_small = ImageFont.truetype("arial.ttf", 32)
        except (IOError, OSError):
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large

        # Background gradient effect (simple overlay)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Decorative circle
        draw_overlay.ellipse([-100, -100, 400, 400], fill=(255, 255, 255, 20))
        draw_overlay.ellipse([700, 600, 1200, 1200], fill=(255, 255, 255, 15))
        
        img = Image.alpha_composite(img.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(img)

        # Business Name
        draw.text((540, 80), self.business_name, fill=(255, 215, 0), 
                  font=font_medium, anchor="mt")

        # Promo Label
        draw.text((540, 200), "PROMO SPESIAL!", fill=(255, 255, 255), 
                  font=font_large, anchor="mt")

        # Promo Text
        draw.text((540, 400), promo_text, fill=(255, 255, 255), 
                  font=font_medium, anchor="mt")

        # Price
        if price:
            # Price background
            draw.rounded_rectangle(
                [340, 500, 740, 600], radius=20, fill=(255, 215, 0)
            )
            draw.text((540, 550), price, fill=(0, 51, 102), 
                      font=font_large, anchor="mt")

        # Footer
        draw.text((540, 800), "Hubungi Kami Segera!", fill=(255, 255, 180), 
                  font=font_small, anchor="mt")
        draw.text((540, 860), "Stok Terbatas!", fill=(255, 200, 200), 
                  font=font_small, anchor="mt")

        # Save
        if not filename:
            filename = f"flyer_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        
        filepath = self.output_dir.parent / "flyers" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        img = img.convert("RGB")
        img.save(str(filepath), "PNG")
        return str(filepath)

    # ─── Simple Text Price List ──────────────────────────────────────────
    def generate_text(self, products: list) -> str:
        """Generate a plain text price list for WhatsApp sharing."""
        lines = [
            "=" * 40,
            f"  {self.business_name}",
            "=" * 40,
            f"  DAFTAR HARGA BAN",
            f"  {datetime.now().strftime('%d-%m-%Y')}",
            "-" * 40,
            ""
        ]
        
        for prod in products:
            merek = prod.get("Merek", "-")
            ukuran = prod.get("Ukuran", "-")
            harga = f"Rp {prod.get('Harga Jual', 0):,.0f}"
            stok = "✓ Stok Ada" if prod.get("Stok", 0) > 0 else "✗ Stok Habis"
            lines.append(f"  {merek} - {ukuran}")
            lines.append(f"  Harga: {harga} | {stok}")
            lines.append("")

        lines.extend([
            "-" * 40,
            "  Hubungi: WhatsApp Toko",
            "  *Harga dapat berubah sewaktu-waktu*",
            "=" * 40,
        ])
        
        return "\n".join(lines)
