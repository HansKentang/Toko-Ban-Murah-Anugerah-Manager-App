"""
QR Code Tire Catalog - Toko Ban Murah Anugerah
===============================================
Generate QR codes that customers scan to view your full tire catalog
with prices on their phone. Works without an app install!
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import qrcode
    from qrcode.image.pil import PilImage
    from PIL import Image, ImageDraw, ImageFont
    _has_qr = True
except ImportError:
    _has_qr = False


# ─── HTML Template for QR Landing Page ──────────────────────────────────────
CATALOG_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_name} - Katalog Ban</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; color: #333; }}
        .header {{ background: linear-gradient(135deg, #1B5E20, #43A047); color: white; padding: 30px 20px; text-align: center; }}
        .header h1 {{ font-size: 24px; margin-bottom: 5px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .stats {{ display: flex; justify-content: space-around; background: white; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #2E7D32; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }}
        .product-card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .product-card:hover {{ transform: translateY(-3px); }}
        .product-body {{ padding: 15px; }}
        .product-brand {{ font-size: 18px; font-weight: bold; color: #2E7D32; }}
        .product-spec {{ font-size: 13px; color: #666; margin: 5px 0; }}
        .product-price {{ font-size: 20px; font-weight: bold; color: #28a745; margin: 10px 0; }}
        .product-stock {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; }}
        .stock-available {{ background: #d4edda; color: #155724; }}
        .stock-low {{ background: #fff3cd; color: #856404; }}
        .stock-empty {{ background: #f8d7da; color: #721c24; }}
        .contact-bar {{ background: #2E7D32; color: white; padding: 20px; text-align: center; position: sticky; bottom: 0; }}
        .contact-bar a {{ color: #FFD700; text-decoration: none; font-weight: bold; font-size: 16px; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #999; }}
        @media (max-width: 600px) {{ .product-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{business_name}</h1>
        <p>Katalog Ban Lengkap - Harga Terbaru</p>
        <p style="margin-top:5px;">Update: {update_date}</p>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{total_products}</div>
                <div class="stat-label">Total Produk</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{available_products}</div>
                <div class="stat-label">Stok Tersedia</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_brands}</div>
                <div class="stat-label">Merek Tersedia</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{lowest_price}</div>
                <div class="stat-label">Mulai Dari</div>
            </div>
        </div>

        <h2 style="color: #2E7D32; margin-bottom: 15px;">Katalog Produk</h2>
        <div class="product-grid">
            {product_cards}
        </div>
    </div>
    <div class="contact-bar">
        📞 Hubungi Kami: <a href="https://wa.me/{whatsapp}?text=Halo%20saya%20lihat%20dari%20katalog">Chat WhatsApp</a>
    </div>
    <div class="footer">
        {business_name} &copy; {year} | Harga dapat berubah sewaktu-waktu
    </div>
</body>
</html>"""


PRODUCT_CARD_TEMPLATE = """
            <div class="product-card">
                <div class="product-body">
                    <div class="product-brand">{brand}</div>
                    <div class="product-spec">{spec}</div>
                    <div class="product-spec">Ring {ring} | {tipe}</div>
                    <div class="product-price">Rp {price:,.0f}</div>
                    <div class="product-stock {stock_class}">{stock_text}</div>
                </div>
            </div>"""


class QRCatalog:
    """Generate QR code catalogs for the tire shop."""

    def __init__(self, business_name: str = "Toko Ban Murah Anugerah",
                 whatsapp: str = "",
                 output_dir: str = "../output/qr_codes"):
        self.business_name = business_name
        self.whatsapp = whatsapp
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_catalog(self, products: list) -> str:
        """Generate an HTML catalog page."""
        total = len(products)
        available = sum(1 for p in products if p.get("Stok", 0) > 0)
        brands = len(set(p.get("Merek", "") for p in products))
        
        prices = [p.get("Harga Jual", 0) for p in products if p.get("Harga Jual", 0) > 0]
        lowest = min(prices) if prices else 0
        
        # Generate product cards
        product_cards = ""
        for prod in products:
            stock = prod.get("Stok", 0)
            if stock > 5:
                stock_class = "stock-available"
                stock_text = f"✓ Stok: {stock}"
            elif stock > 0:
                stock_class = "stock-low"
                stock_text = f"⚠️ Sisa: {stock}"
            else:
                stock_class = "stock-empty"
                stock_text = "✗ Stok Habis"
            
            card = PRODUCT_CARD_TEMPLATE.format(
                brand=prod.get("Merek", "-"),
                spec=prod.get("Ukuran", "-"),
                ring=prod.get("Ring", "-"),
                tipe=prod.get("Tipe", "-"),
                price=prod.get("Harga Jual", 0),
                stock_class=stock_class,
                stock_text=stock_text
            )
            product_cards += card
        
        html = CATALOG_HTML_TEMPLATE.format(
            business_name=self.business_name,
            update_date=datetime.now().strftime("%d %B %Y"),
            total_products=total,
            available_products=available,
            total_brands=brands,
            lowest_price=f"Rp {lowest:,.0f}",
            product_cards=product_cards,
            whatsapp=self.whatsapp,
            year=datetime.now().year
        )
        
        return html

    def save_catalog(self, products: list, filename: Optional[str] = None) -> str:
        """Save catalog HTML file."""
        html = self.generate_html_catalog(products)
        
        if not filename:
            filename = f"catalog_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        
        return str(filepath)

    def generate_qr(self, data_url: str, label: str = "",
                    filename: Optional[str] = None) -> Optional[str]:
        """Generate a QR code image that points to the catalog."""
        if not _has_qr:
            return None
        
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=2,
        )
        qr.add_data(data_url)
        qr.make(fit=True)
        
        # Generate QR code image
        qr_img = qr.make_image(fill_color="#2E7D32", back_color="white")
        qr_img = qr_img.convert("RGB")
        
        # Add label if provided
        if label:
            # Add padding for label
            qr_width, qr_height = qr_img.size
            new_height = qr_height + 80
            final_img = Image.new("RGB", (qr_width, new_height), "white")
            final_img.paste(qr_img, (0, 0))
            
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except (IOError, OSError):
                font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(final_img)
            # Draw business name at top
            draw.text((qr_width // 2, 10), self.business_name, 
                     fill="#2E7D32", font=font, anchor="mt")
            # Draw instruction below QR
            draw.text((qr_width // 2, qr_height + 30), 
                     "Scan untuk lihat katalog!", 
                     fill="#666666", font=font, anchor="mt")
            
            qr_img = final_img

        if not filename:
            filename = f"qr_catalog_{datetime.now().strftime('%Y%m%d')}.png"
        
        filepath = self.output_dir / filename
        qr_img.save(str(filepath), "PNG")
        return str(filepath)

    def generate_sticker_sheet(self, products: list, 
                                items_per_sheet: int = 8) -> Optional[str]:
        """Generate a sticker sheet with individual QR codes for top products."""
        if not _has_qr:
            return None
        
        # Generate individual QR codes for top products
        stickers = []
        for prod in products[:items_per_sheet]:
            name = f"{prod.get('Merek', '')} {prod.get('Ukuran', '')}"
            price = f"Rp {prod.get('Harga Jual', 0):,.0f}"
            
            text = f"{self.business_name}\n{name}\n{price}"
            
            qr = qrcode.QRCode(box_size=6, border=1)
            qr.add_data(text)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#2E7D32").convert("RGB")
            stickers.append(qr_img)
        
        # Arrange in grid
        if not stickers:
            return None
        
        cols = 2
        rows = (len(stickers) + cols - 1) // cols
        sticker_w, sticker_h = stickers[0].size
        
        sheet = Image.new("RGB", (sticker_w * cols + 60, sticker_h * rows + 60), "white")
        
        for i, sticker in enumerate(stickers):
            x = 30 + (i % cols) * sticker_w
            y = 30 + (i // cols) * sticker_h
            sheet.paste(sticker, (x, y))
        
        filepath = self.output_dir / f"sticker_sheet_{datetime.now().strftime('%Y%m%d')}.png"
        sheet.save(str(filepath), "PNG")
        return str(filepath)
