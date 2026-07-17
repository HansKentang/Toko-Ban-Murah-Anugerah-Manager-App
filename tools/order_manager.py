"""
Order Management System - Toko Ban Murah Anugerah
==================================================
Track orders from inquiry to delivery, manage customer communications.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

try:
    import pandas as pd
    _has_pandas = True
except ImportError:
    _has_pandas = False


ORDER_STATUSES = [
    "Baru", "Dikonfirmasi", "Diproses", "Siap Ambil", 
    "Dikirim", "Selesai", "Dibatalkan"
]

PAYMENT_STATUSES = ["Belum Bayar", "DP 50%", "Lunas"]
DELIVERY_METHODS = ["Ambil di Toko", "Dikirim (GoSend)", "Dikirim (JNE)", "Dikirim (Grab)"]


class OrderManager:
    """Manage customer orders from start to finish."""

    def __init__(self, data_path: str = "../data/orders.xlsx"):
        self.data_path = Path(data_path)
        self.orders = []
        self._load_orders()

    def _load_orders(self):
        """Load orders from Excel file."""
        if self.data_path.exists() and _has_pandas:
            try:
                df = pd.read_excel(self.data_path)
                self.orders = df.to_dict("records")
                return
            except Exception:
                pass
        self.orders = []

    def _save_orders(self):
        """Save orders to Excel file."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if _has_pandas:
            df = pd.DataFrame(self.orders)
            df.to_excel(self.data_path, index=False)

    def add_order(self, order: dict) -> dict:
        """Create a new order."""
        order["ID"] = order.get("ID", f"ORD-{len(self.orders) + 1:04d}")
        order["Tanggal"] = order.get("Tanggal", datetime.now().strftime("%Y-%m-%d"))
        order["Status"] = order.get("Status", "Baru")
        order["Status Bayar"] = order.get("Status Bayar", "Belum Bayar")
        order["Total"] = float(order.get("Total", 0))
        order["Sisa"] = float(order.get("Total", 0))
        order["Catatan"] = order.get("Catatan", "")
        order["Histori"] = [
            f"{datetime.now().strftime('%d/%m %H:%M')} - Pesanan dibuat"
        ]
        self.orders.append(order)
        self._save_orders()
        return order

    def update_status(self, order_id: str, new_status: str) -> Optional[dict]:
        """Update order status."""
        if new_status not in ORDER_STATUSES:
            return None
        
        for order in self.orders:
            if order.get("ID") == order_id:
                old_status = order.get("Status", "")
                order["Status"] = new_status
                
                # Add to history
                history = order.get("Histori", [])
                if isinstance(history, str):
                    history = [history]
                history.append(
                    f"{datetime.now().strftime('%d/%m %H:%M')} - "
                    f"Status: {old_status} → {new_status}"
                )
                order["Histori"] = history
                
                self._save_orders()
                return order
        return None

    def update_payment(self, order_id: str, amount_paid: float) -> Optional[dict]:
        """Record a payment for an order."""
        for order in self.orders:
            if order.get("ID") == order_id:
                total = float(order.get("Total", 0))
                paid = float(order.get("Dibayar", 0))
                new_paid = paid + amount_paid
                
                order["Dibayar"] = new_paid
                order["Sisa"] = max(0, total - new_paid)
                
                if new_paid >= total:
                    order["Status Bayar"] = "Lunas"
                elif new_paid > 0:
                    order["Status Bayar"] = "DP 50%"
                
                history = order.get("Histori", [])
                if isinstance(history, str):
                    history = [history]
                history.append(
                    f"{datetime.now().strftime('%d/%m %H:%M')} - "
                    f"Pembayaran Rp {amount_paid:,.0f}"
                )
                order["Histori"] = history
                
                self._save_orders()
                return order
        return None

    def get_order(self, order_id: str) -> Optional[dict]:
        """Get a single order by ID."""
        for order in self.orders:
            if order.get("ID") == order_id:
                return order
        return None

    def get_orders_by_status(self, status: str) -> list:
        """Get all orders with a specific status."""
        return [o for o in self.orders if o.get("Status") == status]

    def get_today_orders(self) -> list:
        """Get today's orders."""
        today = datetime.now().strftime("%Y-%m-%d")
        return [o for o in self.orders if o.get("Tanggal") == today]

    def get_pending_orders(self) -> list:
        """Get all active (non-completed) orders."""
        return [o for o in self.orders 
                if o.get("Status") not in ["Selesai", "Dibatalkan"]]

    def get_customer_orders(self, customer_name: str) -> list:
        """Get all orders for a customer."""
        return [o for o in self.orders 
                if o.get("Pelanggan", "").lower() == customer_name.lower()]

    def get_summary(self) -> dict:
        """Get order summary statistics."""
        total = len(self.orders)
        pending = len(self.get_pending_orders())
        completed = len([o for o in self.orders if o.get("Status") == "Selesai"])
        cancelled = len([o for o in self.orders if o.get("Status") == "Dibatalkan"])
        
        total_revenue = sum(
            float(o.get("Total", 0)) for o in self.orders 
            if o.get("Status") == "Selesai"
        )
        
        unpaid = len([o for o in self.orders 
                     if o.get("Status Bayar") == "Belum Bayar"])
        
        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "cancelled": cancelled,
            "total_revenue": total_revenue,
            "unpaid": unpaid
        }

    def add_sample_orders(self):
        """Add sample orders for demonstration."""
        import random
        customers = [
            {"name": "Budi Santoso", "phone": "08123456789"},
            {"name": "Siti Rahmawati", "phone": "08198765432"},
            {"name": "Ahmad Hidayat", "phone": "08561234567"},
            {"name": "Dewi Lestari", "phone": "08781234567"},
            {"name": "Rudi Hermawan", "phone": "08991234567"},
        ]
        products = [
            "Bridgestone Turanza 195/65R15",
            "Michelin Energy XM2 185/65R14",
            "GT Radial Champiro 175/70R13",
            "Dunlop SP Sport 215/55R17",
            "IRC NR77 80/90-17",
        ]
        
        statuses = ["Baru", "Dikonfirmasi", "Diproses", "Siap Ambil", "Selesai"]
        
        for i in range(15):
            customer = random.choice(customers)
            product = random.choice(products)
            qty = random.randint(2, 4)
            price = random.randint(350000, 750000)
            days_ago = random.randint(0, 30)
            
            order = {
                "Tanggal": (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
                "Pelanggan": customer["name"],
                "Telepon": customer["phone"],
                "Produk": product,
                "Jumlah": qty,
                "Total": price * qty,
                "Dibayar": (price * qty) // 2 if random.random() > 0.5 else 0,
                "Sisa": 0,
                "Status": random.choice(statuses),
                "Status Bayar": random.choice(PAYMENT_STATUSES),
                "Metode Kirim": random.choice(DELIVERY_METHODS),
                "Catatan": "",
            }
            order["Sisa"] = order["Total"] - order["Dibayar"]
            self.add_order(order)
