"""
Social Media Content Scheduler - Toko Ban Murah Anugerah
========================================================
Schedule posts, generate captions, manage content calendar.
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


CAPTION_TEMPLATES = {
    "promo_harga": 
        "🔥 PROMO SPESIAL {date} 🔥\n\n"
        "{business_name} kembali dengan promo gila-gilaan!\n\n"
        "🏷️ {product}\n"
        "💰 Harga spesial: Rp {price:,}\n"
        "📦 Stok terbatas!\n\n"
        "Jangan sampai kehabisan! Kunjungi toko kami sekarang juga.\n\n"
        "#PromoBan #BanMurah #TokoBan #SpesialPromo #{city}",
    
    "new_stock":
        "📦 STOK BARU DATANG! 📦\n\n"
        "{business_name} sekarang menyediakan:\n"
        "✅ {product}\n"
        "✅ Ukuran: {size}\n"
        "✅ Harga mulai Rp {price:,}\n\n"
        "Kualitas terjamin, harga bersahabat!\n"
        "Langsung cek ke toko kami ya! 🏪\n\n"
        "#BanBaru #StokBaru #TokoBan #BanMobil #BanMotor",
    
    "tips_ban":
        "💡 TIPS MERAWAT BAN {date} 💡\n\n"
        "{tip}\n\n"
        "Ada pertanyaan seputar ban? Langsung chat kami ya!\n"
        "{business_name} siap membantu. 💪\n\n"
        "#TipsBan #MerawatBan #TokoBan #TipsMobil #TipsMotor",
    
    "testimoni":
        "⭐ TESTIMONI PELANGGAN ⭐\n\n"
        "\"{quote}\"\n"
        "- {customer}\n\n"
        "Terima kasih atas kepercayaannya! 🙏\n"
        "{business_name} selalu berusaha memberikan yang terbaik.\n\n"
        "#Testimoni #PelangganPuas #TokoBan #BanBerkualitas",
    
    "produk_unggulan":
        "🏆 PRODUK UNGGULAN KAMI 🏆\n\n"
        "{product}\n"
        "✅ Ukuran: {size}\n"
        "✅ Tipe: {tipe}\n"
        "✅ Harga spesial: Rp {price:,}\n\n"
        "Kualitas premium dengan harga pas di kantong!\n"
        "Cocok untuk mobil {car_type} Anda.\n\n"
        "Segera dapatkan di {business_name}! 🚗💨\n\n"
        "#ProdukUnggulan #BanPremium #TokoBan #RekomendasiBan",
    
    "hari_libur":
        "📅 INFO JADWAL OPERASIONAL 📅\n\n"
        "Yuk catat jadwal {business_name}:\n\n"
        "🕐 Senin - Sabtu: 08:00 - 20:00\n"
        "🕐 Minggu: 09:00 - 17:00\n"
        "📞 Hubungi kami untuk info lebih lanjut!\n\n"
        "#JamKerja #TokoBan #InfoToko #JamBuka"
}

TIPS_BAN = [
    "Periksa tekanan angin ban minimal 2 minggu sekali. Tekanan yang tepat bisa menghemat BBM hingga 5%!",
    "Lakukan rotasi ban setiap 10.000 km untuk memastikan keausan yang merata pada semua ban.",
    "Perhatikan tread depth ban. Jika sudah mencapai 1.6mm, segera ganti ban baru demi keselamatan!",
    "Jangan lupa lakukan spooring & balancing setiap 10.000 km atau setelah ban dibongkar.",
    "Ban memiliki usia pakai maksimal 4 tahun, meskipun masih terlihat bagus. Segera ganti jika sudah tua!",
    "Hindari parkir di bawah sinar matahari langsung terlalu lama untuk mencegah retak pada ban.",
    "Beban berlebih bisa merusak ban dan membahayakan keselamatan. Perhatikan batas maksimal beban!",
    "Setiap 6 bulan, periksa kondisi ban serep (cadangan) jangan sampai kempes saat dibutuhkan.",
]


class SocialMediaScheduler:
    """Manage social media content for the tire shop."""

    def __init__(self, business_name: str = "Toko Ban Murah Anugerah",
                 city: str = "", data_path: str = "../data/social_posts.xlsx"):
        self.business_name = business_name
        self.city = city
        self.data_path = Path(data_path)
        self.posts = []
        self.captions = CAPTION_TEMPLATES
        self.tips = TIPS_BAN

    def generate_caption(self, template_key: str, **kwargs) -> str:
        """Generate a social media caption from template."""
        template = self.captions.get(template_key, "")
        if not template:
            return "Template tidak ditemukan."
        
        kwargs.setdefault("business_name", self.business_name)
        kwargs.setdefault("city", self.city)
        kwargs.setdefault("date", datetime.now().strftime("%d-%m-%Y"))
        kwargs.setdefault("tip", self.tips[hash(str(kwargs)) % len(self.tips)])
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Caption perlu diisi: {e}\n\n{template}"

    def get_random_tip(self) -> str:
        """Get a random tire care tip."""
        import random
        return random.choice(self.tips)

    def schedule_post(self, platform: str, content: str, 
                      scheduled_date: str) -> dict:
        """Schedule a post for later."""
        post = {
            "id": f"POST-{len(self.posts) + 1:04d}",
            "platform": platform,
            "content": content,
            "scheduled_date": scheduled_date,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Scheduled"
        }
        self.posts.append(post)
        return post

    def get_upcoming_posts(self, days: int = 7) -> list:
        """Get upcoming scheduled posts."""
        today = datetime.now()
        cutoff = today + timedelta(days=days)
        
        upcoming = []
        for post in self.posts:
            if post.get("status") == "Scheduled":
                try:
                    post_date = datetime.strptime(
                        post.get("scheduled_date", ""), "%Y-%m-%d"
                    )
                    if today <= post_date <= cutoff:
                        upcoming.append(post)
                except ValueError:
                    pass
        return sorted(upcoming, key=lambda p: p.get("scheduled_date", ""))

    def get_all_templates(self) -> dict:
        """Get all caption templates with descriptions."""
        return {
            "promo_harga": "Promo harga spesial",
            "new_stock": "Info stok baru datang",
            "tips_ban": "Tips perawatan ban",
            "testimoni": "Testimoni pelanggan",
            "produk_unggulan": "Produk unggulan",
            "hari_libur": "Info jam operasional"
        }

    def generate_content_plan(self, days: int = 7) -> list:
        """Auto-generate a content plan for N days."""
        template_keys = list(self.captions.keys())
        import random
        plan = []
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            template_key = template_keys[i % len(template_keys)]
            
            content = self.generate_caption(
                template_key,
                product="Ban Michelin Energy XM2",
                price=750000,
                size="185/65R14",
                tipe="Energy XM2+",
                car_type="Sedan/MPV",
                customer="Bapak Budi",
                quote="Ban-ya awet banget, udah setahun masih bagus!"
            )
            
            plan.append({
                "date": date,
                "day": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][datetime.now().weekday() + i % 7],
                "template": template_key,
                "content": content
            })
        
        return plan
