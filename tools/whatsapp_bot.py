"""
WhatsApp Auto-Reply Bot & Bulk Messenger - Toko Ban Murah Anugerah
===============================================================
Features:
- Message template library (common tire questions & answers)
- Quick-send via WhatsApp Web / Desktop
- Bulk promotional messaging to customer list
- Scheduled message sending
- Auto-reply keyword matching system
"""

import os
import csv
import json
import datetime
import webbrowser
from pathlib import Path
from typing import Optional

try:
    import pywhatkit as kit
    _has_pywhatkit = True
except ImportError:
    _has_pywhatkit = False


# ─── Message Templates ──────────────────────────────────────────────────────
TIRE_TEMPLATES = {
    "halo": "Halo! 👋 Selamat datang di *Toko Ban Murah Anugerah*!\n"
            "Ada yang bisa kami bantu?\n\n"
            "💬 Ketik nomor untuk info:\n"
            "1 → Daftar Harga Ban\n"
            "2 → Stok Ban Tersedia\n"
            "3 → Lokasi Toko\n"
            "4 → Promo Hari Ini",
    
    "harga": "Berikut daftar harga ban pilihan kami:\n\n"
             "🚗 *Ban Mobil:*\n"
             "- Ring 13: Rp 350.000 - Rp 600.000\n"
             "- Ring 14: Rp 400.000 - Rp 750.000\n"
             "- Ring 15: Rp 500.000 - Rp 900.000\n"
             "- Ring 16: Rp 600.000 - Rp 1.200.000\n\n"
             "🏍 *Ban Motor:*\n"
             "- Ring 14: Rp 120.000 - Rp 200.000\n"
             "- Ring 17: Rp 150.000 - Rp 350.000\n\n"
             "📞 Untuk info lebih detail, hubungi kami langsung!",
    
    "lokasi": "📍 *Lokasi Toko Ban Murah Anugerah*\n\n"
              "Kami melayani:\n"
              "✅ Pemasangan ban\n"
              "✅ Spooring & balancing\n"
              "✅ Tambal ban\n"
              "✅ Ganti oli\n\n"
              "🕐 Jam Buka: Senin - Sabtu (08:00 - 20:00)\n"
              "📞 Hubungi kami untuk alamat lengkap!",
    
    "promo": "🎉 *PROMO SPESIAL Toko Ban Murah Anugerah!* 🎉\n\n"
             "Tersedia berbagai promo menarik:\n"
             "🔥 Diskon up to 20% untuk ban pilihan\n"
             "🎁 Gratis balancing untuk pembelian 2 ban\n"
             "💰 Cicilan 0% (kartu kredit terpilih)\n\n"
             "🚨 *Stok terbatas!* Hubungi kami sekarang!",
    
    "stok": "Kami memiliki stok ban dari berbagai merek:\n\n"
            "🏆 *Merek Tersedia:*\n"
            "• Bridgestone ✓\n"
            "• Michelin ✓\n"
            "• Dunlop ✓\n"
            "• GT Radial ✓\n"
            "• Achilles ✓\n"
            "• IRC (Motor) ✓\n"
            "• Michelin (Motor) ✓\n\n"
            "Ketik *HARGA* untuk info harga terbaru!",
    
    "terima_kasih": "Terima kasih telah menghubungi *Toko Ban Murah Anugerah*! 🙏\n\n"
                    "Kami siap membantu kebutuhan ban Anda.\n"
                    "✅ Harga Murah\n"
                    "✅ Kualitas Terjamin\n"
                    "✅ Pelayanan Ramah\n\n"
                    "Jangan ragu untuk menghubungi kami lagi!"
}


class WhatsAppBot:
    """WhatsApp bot manager for Toko Ban Murah Anugerah."""

    def __init__(self, config_path: str = "../config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.templates = TIRE_TEMPLATES
        self.keywords = self._build_keyword_map()

    def _load_config(self) -> dict:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "business": {"name": "Toko Ban Murah Anugerah", "phone": ""},
                "whatsapp": {
                    "auto_reply_enabled": False,
                    "business_hours_start": "08:00",
                    "business_hours_end": "20:00",
                    "default_reply": "Terima kasih sudah menghubungi kami!"
                }
            }

    def _build_keyword_map(self) -> dict:
        """Map keywords to template keys for auto-reply matching."""
        return {
            "halo": "halo", "hai": "halo", "siang": "halo", "pagi": "halo",
            "assalamualaikum": "halo", "selamat": "halo",
            "harga": "harga", "price": "harga", "berapa": "harga",
            "lokasi": "lokasi", "alamat": "lokasi", "dimana": "lokasi",
            "promo": "promo", "diskon": "promo", "murah": "promo",
            "stok": "stok", "stock": "stok", "ada": "stok", "tersedia": "stok",
            "makasih": "terima_kasih", "terima kasih": "terima_kasih",
            "thanks": "terima_kasih", "ok": "terima_kasih",
        }

    def match_template(self, message: str) -> Optional[str]:
        """Match user message to best template."""
        message_lower = message.lower().strip()
        for keyword, template_key in self.keywords.items():
            if keyword in message_lower:
                return self.templates.get(template_key)
        return None

    # ─── Send via WhatsApp ──────────────────────────────────────────────
    def send_whatsapp(self, phone: str, message: str, wait_time: int = 15):
        """Send a WhatsApp message using pywhatkit (opens WhatsApp Web)."""
        if not _has_pywhatkit:
            return self._send_via_link(phone, message)
        
        try:
            now = datetime.datetime.now()
            send_time = now + datetime.timedelta(minutes=1)
            kit.sendwhatmsg(
                phone, message,
                send_time.hour, send_time.minute,
                wait_time=wait_time,
                tab_close=True
            )
            return True
        except Exception as e:
            return self._send_via_link(phone, message)

    def _send_via_link(self, phone: str, message: str) -> bool:
        """Fallback: open wa.me link in browser."""
        import urllib.parse
        phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        msg_encoded = urllib.parse.quote(message)
        url = f"https://wa.me/{phone_clean}?text={msg_encoded}"
        webbrowser.open(url)
        return True

    # ─── Bulk Send ──────────────────────────────────────────────────────
    def bulk_send(self, contacts: list, message: str, delay_seconds: int = 30):
        """
        Send bulk messages. contacts is a list of dicts: [{"name": "...", "phone": "..."}]
        """
        results = []
        for i, contact in enumerate(contacts):
            phone = contact.get("phone", "")
            if not phone:
                results.append({"name": contact.get("name", "?"), "status": "no_phone"})
                continue
            
            personalized = message.replace("{name}", contact.get("name", "Pelanggan"))
            try:
                self.send_whatsapp(phone, personalized, wait_time=delay_seconds)
                results.append({"name": contact.get("name", "?"), "status": "sent"})
            except Exception as e:
                results.append({"name": contact.get("name", "?"), "status": f"error: {e}"})
        
        return results

    # ─── Schedule Message ──────────────────────────────────────────────
    def schedule_message(self, phone: str, message: str, 
                         hour: int, minute: int):
        """Schedule a WhatsApp message for a specific time."""
        if not _has_pywhatkit:
            return False, "pywhatkit tidak terinstall"
        
        try:
            kit.sendwhatmsg(phone, message, hour, minute, wait_time=15)
            return True, f"Pesan terjadwal: {hour:02d}:{minute:02d}"
        except Exception as e:
            return False, str(e)

    # ─── Promo Blast ────────────────────────────────────────────────────
    def promo_blast(self, contacts: list, promo_type: str = "promo"):
        """Send a promo template to all contacts."""
        message = self.templates.get(promo_type, self.templates["promo"])
        message += "\n\n📢 *PROMO TERBATAS! Hubungi sekarang juga!*"
        return self.bulk_send(contacts, message)


# ─── Utility Functions ──────────────────────────────────────────────────────
def get_all_templates() -> dict:
    """Get all available message templates."""
    return TIRE_TEMPLATES


def get_template_keys() -> list:
    """Get list of template key names."""
    return list(TIRE_TEMPLATES.keys())
