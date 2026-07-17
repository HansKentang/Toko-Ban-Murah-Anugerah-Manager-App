"""
Customer Loyalty Program - Toko Ban Murah Anugerah
===================================================
Points-based loyalty system: earn points on purchases, redeem for discounts.
Birthday promos, referral bonuses, and tiered membership.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

try:
    import pandas as pd
    _has_pandas = True
except ImportError:
    _has_pandas = False


MEMBERSHIP_TIERS = [
    {"name": "Reguler", "min_points": 0, "color": "#808080", 
     "benefits": ["Poin belanja 1%", "Welcome bonus 100 poin"]},
    {"name": "Silver", "min_points": 500, "color": "#C0C0C0",
     "benefits": ["Poin belanja 2%", "Diskon 5% setiap checkout", "Gratis balancing 1x"]},
    {"name": "Gold", "min_points": 1500, "color": "#FFD700",
     "benefits": ["Poin belanja 3%", "Diskon 10% setiap checkout", 
                  "Gratis spooring & balancing 1x", "Prioritas service"]},
    {"name": "Platinum", "min_points": 5000, "color": "#E5E4E2",
     "benefits": ["Poin belanja 5%", "Diskon 15% setiap checkout",
                  "Gratis spooring & balancing 2x", "Undangan event spesial",
                  "Free ganti oli 1x/tahun"]}
]


class LoyaltyProgram:
    """Customer loyalty program with points and tiers."""

    def __init__(self, config_path: str = "../config.json",
                 data_path: str = "../data/customers.xlsx"):
        self.config = self._load_config(config_path)
        self.data_path = Path(data_path)
        self.customers = []
        self._load_customers()

    def _load_config(self, path: str) -> dict:
        import json
        try:
            with open(path, "r") as f:
                return json.load(f).get("loyalty", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "points_per_purchase": 10,
                "points_to_rupiah": 100,
                "welcome_bonus": 100
            }

    def _load_customers(self):
        """Load customer data from Excel."""
        if self.data_path.exists() and _has_pandas:
            try:
                df = pd.read_excel(self.data_path)
                self.customers = df.to_dict("records")
                return
            except Exception:
                pass
        self.customers = []

    def _save_customers(self):
        """Save customer data to Excel."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if _has_pandas:
            required_cols = [
                "Nama", "Telepon", "Total Poin", "Tier", 
                "Total Belanja", "Terakhir Belanja", "Tanggal Daftar",
                "Tanggal Lahir", "Total Transaksi", "Referral Code"
            ]
            df = pd.DataFrame(self.customers)
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""
            df.to_excel(self.data_path, index=False)

    def register_customer(self, name: str, phone: str, 
                          birth_date: str = "") -> dict:
        """Register a new customer with welcome bonus."""
        import random
        customer = {
            "Nama": name,
            "Telepon": phone,
            "Total Poin": self.config.get("welcome_bonus", 100),
            "Tier": "Reguler",
            "Total Belanja": 0,
            "Total Transaksi": 0,
            "Terakhir Belanja": "-",
            "Tanggal Daftar": datetime.now().strftime("%Y-%m-%d"),
            "Tanggal Lahir": birth_date,
            "Referral Code": f"TB{phone[-4:]}{random.randint(100,999)}"
        }
        self.customers.append(customer)
        self._save_customers()
        return customer

    def get_customer(self, phone: str) -> Optional[dict]:
        """Find customer by phone number."""
        for c in self.customers:
            if c.get("Telepon", "") == phone:
                return c
        return None

    def get_customer_by_name(self, name: str) -> Optional[dict]:
        """Find customer by name."""
        for c in self.customers:
            if c.get("Nama", "").lower() == name.lower():
                return c
        return None

    def add_points(self, phone: str, purchase_amount: float) -> Optional[dict]:
        """Add points based on purchase amount."""
        customer = self.get_customer(phone)
        if not customer:
            return None
        
        # Calculate points based on tier
        tier_name = customer.get("Tier", "Reguler")
        multiplier = {
            "Reguler": 1, "Silver": 2, "Gold": 3, "Platinum": 5
        }.get(tier_name, 1)
        
        points_earned = int(purchase_amount * multiplier / 1000)
        customer["Total Poin"] = customer.get("Total Poin", 0) + points_earned
        customer["Total Belanja"] = customer.get("Total Belanja", 0) + purchase_amount
        customer["Total Transaksi"] = customer.get("Total Transaksi", 0) + 1
        customer["Terakhir Belanja"] = datetime.now().strftime("%Y-%m-%d")
        
        # Update tier
        customer["Tier"] = self._calculate_tier(customer["Total Poin"])
        
        self._save_customers()
        return customer

    def _calculate_tier(self, points: int) -> str:
        """Determine membership tier based on points."""
        for tier in reversed(MEMBERSHIP_TIERS):
            if points >= tier["min_points"]:
                return tier["name"]
        return "Reguler"

    def redeem_points(self, phone: str, points: int) -> Optional[dict]:
        """Redeem points for discount."""
        customer = self.get_customer(phone)
        if not customer:
            return None
        
        current_points = customer.get("Total Poin", 0)
        if current_points < points:
            return None
        
        discount = points * self.config.get("points_to_rupiah", 100)
        customer["Total Poin"] = current_points - points
        self._save_customers()
        
        return {
            "customer": customer,
            "points_used": points,
            "discount_rupiah": discount,
            "remaining_points": customer["Total Poin"]
        }

    def is_birthday(self, phone: str) -> bool:
        """Check if today is customer's birthday."""
        customer = self.get_customer(phone)
        if not customer:
            return False
        
        birth = customer.get("Tanggal Lahir", "")
        if not birth:
            return False
        
        try:
            birth_date = datetime.strptime(birth, "%Y-%m-%d")
            today = datetime.now()
            return (birth_date.month == today.month and 
                    birth_date.day == today.day)
        except ValueError:
            return False

    def birthday_bonus(self, phone: str) -> Optional[dict]:
        """Give birthday bonus points."""
        if not self.is_birthday(phone):
            return None
        
        customer = self.get_customer(phone)
        if not customer:
            return None
        
        bonus_points = 200  # Birthday bonus
        customer["Total Poin"] = customer.get("Total Poin", 0) + bonus_points
        customer["Catatan"] = f"Bonus ulang tahun {datetime.now().strftime('%d-%m-%Y')}"
        self._save_customers()
        
        return {
            "customer": customer,
            "bonus_points": bonus_points,
            "total_points": customer["Total Poin"]
        }

    def get_tier_benefits(self, tier_name: str) -> list:
        """Get benefits string for a membership tier."""
        for tier in MEMBERSHIP_TIERS:
            if tier["name"].lower() == tier_name.lower():
                return tier["benefits"]
        return MEMBERSHIP_TIERS[0]["benefits"]

    def get_all_tiers(self) -> list:
        """Get all membership tiers info."""
        return MEMBERSHIP_TIERS

    def add_sample_customers(self):
        """Add sample customers for demonstration."""
        samples = [
            {"Nama": "Budi Santoso", "Telepon": "08123456789", 
             "Total Poin": 750, "Tanggal Lahir": "1985-03-15"},
            {"Nama": "Siti Rahmawati", "Telepon": "08198765432",
             "Total Poin": 2200, "Tanggal Lahir": "1990-07-22"},
            {"Nama": "Ahmad Hidayat", "Telepon": "08561234567",
             "Total Poin": 350, "Tanggal Lahir": "1988-11-08"},
            {"Nama": "Dewi Lestari", "Telepon": "08781234567",
             "Total Poin": 1800, "Tanggal Lahir": "1995-01-30"},
            {"Nama": "Rudi Hermawan", "Telepon": "08991234567",
             "Total Poin": 5200, "Tanggal Lahir": "1982-09-12"},
        ]
        
        for s in samples:
            name = s["Nama"]
            phone = s["Telepon"]
            
            # Check if already exists
            if not self.get_customer(phone):
                customer = self.register_customer(name, phone, s["Tanggal Lahir"])
                customer["Total Poin"] = s["Total Poin"]
                self._save_customers()
        
        # Apply tiers based on points
        for c in self.customers:
            c["Tier"] = self._calculate_tier(c.get("Total Poin", 0))
        self._save_customers()
