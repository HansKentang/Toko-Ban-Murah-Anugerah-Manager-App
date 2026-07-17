"""
Sales Dashboard - Toko Ban Murah Anugerah
==========================================
Visualize sales data, revenue, top products with charts.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    _has_matplotlib = True
except ImportError:
    _has_matplotlib = False

try:
    import pandas as pd
    _has_pandas = True
except ImportError:
    _has_pandas = False


class SalesDashboard:
    """Generate sales charts and reports."""

    def __init__(self, data_path: str = "../data/sales.xlsx", 
                 output_dir: str = "../output/reports"):
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sales_data = []
        self._load_sales()

    def _load_sales(self):
        """Load sales data from Excel."""
        if self.data_path.exists() and _has_pandas:
            try:
                df = pd.read_excel(self.data_path)
                self.sales_data = df.to_dict("records")
                return
            except Exception:
                pass
        self.sales_data = []

    def add_sale(self, sale: dict):
        """Record a new sale."""
        sale["Tanggal"] = sale.get("Tanggal", datetime.now().strftime("%Y-%m-%d"))
        sale["Total"] = float(sale.get("Total", 0))
        sale["Keuntungan"] = float(sale.get("Keuntungan", 0))
        self.sales_data.append(sale)
        self._save_sales()

    def _save_sales(self):
        """Save sales data to Excel."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if _has_pandas and self.sales_data:
            df = pd.DataFrame(self.sales_data)
            df.to_excel(self.data_path, index=False)

    def add_sample_sales(self):
        """Add sample sales data for demonstration."""
        import random
        products = [
            "Bridgestone 195/65R15", "Michelin 185/65R14", 
            "GT Radial 175/70R13", "Dunlop 215/55R17",
            "IRC 80/90-17", "Achilles 205/65R15"
        ]
        for days_ago in range(60):
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            num_sales = random.randint(1, 5)
            for _ in range(num_sales):
                product = random.choice(products)
                qty = random.randint(1, 4)
                price = random.randint(350000, 950000)
                profit = int(price * 0.25)
                self.add_sale({
                    "Tanggal": date,
                    "Produk": product,
                    "Jumlah": qty,
                    "Total": price * qty,
                    "Keuntungan": profit * qty,
                    "Pelanggan": f"Customer {random.randint(1, 30)}"
                })

    # ─── Charts ──────────────────────────────────────────────────────────
    def chart_daily_revenue(self, days: int = 30) -> Optional[str]:
        """Generate daily revenue chart for last N days."""
        if not _has_matplotlib or not self.sales_data:
            return None

        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        recent = [s for s in self.sales_data if s.get("Tanggal", "") >= cutoff]

        if not recent:
            return None

        # Aggregate by date
        daily = {}
        for s in recent:
            date = s.get("Tanggal", "")
            daily[date] = daily.get(date, 0) + s.get("Total", 0)

        dates = sorted(daily.keys())
        values = [daily[d] for d in dates]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.fill_between(range(len(dates)), values, alpha=0.3, color="#2E7D32")
        ax.plot(range(len(dates)), values, color="#2E7D32", linewidth=2,
                marker="o", markersize=4)
        
        ax.set_title(f"Pendapatan Harian - {days} Hari Terakhir", 
                     fontsize=14, fontweight="bold", color="#2E7D32")
        ax.set_xlabel("Tanggal", fontsize=10)
        ax.set_ylabel("Total Pendapatan (Rp)", fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x labels
        if len(dates) <= 10:
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels([d[-5:] for d in dates], rotation=45)
        else:
            step = max(1, len(dates) // 10)
            ax.set_xticks(range(0, len(dates), step))
            ax.set_xticklabels([dates[i][-5:] for i in range(0, len(dates), step)], 
                              rotation=45)

        # Format y axis
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f"Rp {x:,.0f}")
        )

        plt.tight_layout()
        filepath = self.output_dir / f"daily_revenue_{datetime.now().strftime('%Y%m%d')}.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(filepath)

    def chart_top_products(self, top_n: int = 10) -> Optional[str]:
        """Generate top selling products chart."""
        if not _has_matplotlib or not self.sales_data:
            return None

        product_sales = {}
        for s in self.sales_data:
            prod = s.get("Produk", "Unknown")
            product_sales[prod] = product_sales.get(prod, 0) + s.get("Jumlah", 0)

        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], 
                                 reverse=True)[:top_n]
        
        products = [p[0][:20] for p in sorted_products]
        quantities = [p[1] for p in sorted_products]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(range(len(products)), quantities, color="#2E7D32")
        
        # Color top bar differently
        if bars:
            bars[0].set_color("#FFD700")
            if len(bars) > 1:
                bars[1].set_color("#0066CC")

        ax.set_title(f"Top {top_n} Produk Terlaris", fontsize=14,
                     fontweight="bold", color="#003366")
        ax.set_xlabel("Jumlah Terjual", fontsize=10)
        ax.set_yticks(range(len(products)))
        ax.set_yticklabels(products, fontsize=9)
        ax.grid(True, alpha=0.3, axis="x")

        # Add value labels
        for i, v in enumerate(quantities):
            ax.text(v + 0.3, i, str(v), va="center", fontsize=9)

        plt.tight_layout()
        filepath = self.output_dir / f"top_products_{datetime.now().strftime('%Y%m%d')}.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(filepath)

    def chart_profit_margin(self) -> Optional[str]:
        """Generate profit margin trend chart."""
        if not _has_matplotlib or not self.sales_data:
            return None

        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        recent = [s for s in self.sales_data if s.get("Tanggal", "") >= cutoff]

        daily_profit = {}
        daily_revenue = {}
        for s in recent:
            date = s.get("Tanggal", "")
            daily_profit[date] = daily_profit.get(date, 0) + s.get("Keuntungan", 0)
            daily_revenue[date] = daily_revenue.get(date, 0) + s.get("Total", 0)

        dates = sorted(daily_profit.keys())
        margins = []
        for d in dates:
            rev = daily_revenue.get(d, 1)
            profit = daily_profit.get(d, 0)
            margins.append((profit / rev) * 100 if rev > 0 else 0)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(range(len(dates)), margins, color="#28A745", linewidth=2,
                marker="s", markersize=4)
        ax.axhline(y=25, color="red", linestyle="--", alpha=0.5, 
                   label="Target Margin 25%")
        
        ax.set_title("Margin Keuntungan - 30 Hari Terakhir", fontsize=14,
                     fontweight="bold", color="#003366")
        ax.set_xlabel("Tanggal", fontsize=10)
        ax.set_ylabel("Margin (%)", fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)

        if len(dates) <= 15:
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels([d[-5:] for d in dates], rotation=45)
        
        plt.tight_layout()
        filepath = self.output_dir / f"profit_margin_{datetime.now().strftime('%Y%m%d')}.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(filepath)

    # ─── Text Report ─────────────────────────────────────────────────────
    def generate_report(self) -> str:
        """Generate a text summary report."""
        if not self.sales_data:
            return "Belum ada data penjualan."

        total_revenue = sum(s.get("Total", 0) for s in self.sales_data)
        total_profit = sum(s.get("Keuntungan", 0) for s in self.sales_data)
        total_sales = len(self.sales_data)
        avg_transaction = total_revenue / total_sales if total_sales > 0 else 0

        # Best product
        product_sales = {}
        for s in self.sales_data:
            prod = s.get("Produk", "Unknown")
            product_sales[prod] = product_sales.get(prod, 0) + s.get("Jumlah", 0)
        best_product = max(product_sales, key=product_sales.get) if product_sales else "-"

        report = f"""
╔══════════════════════════════════════╗
║    LAPORAN PENJUALAN                ║
║    Toko Ban Murah Anugerah          ║
║    {datetime.now().strftime('%d-%m-%Y %H:%M')}          ║
╚══════════════════════════════════════╝

📊 RINGKASAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Transaksi    : {total_sales}
Total Pendapatan   : Rp {total_revenue:,.0f}
Total Keuntungan   : Rp {total_profit:,.0f}
Rata-rata Transaksi: Rp {avg_transaction:,.0f}

🏆 PRODUK TERLARIS: {best_product} ({product_sales.get(best_product, 0)} terjual)

📈 MARJIN KEUNTUNGAN: {(total_profit / total_revenue * 100):.1f}%
"""
        return report

    def get_stats(self) -> dict:
        """Get quick statistics."""
        if not self.sales_data:
            return {}
        
        return {
            "total_transactions": len(self.sales_data),
            "total_revenue": sum(s.get("Total", 0) for s in self.sales_data),
            "total_profit": sum(s.get("Keuntungan", 0) for s in self.sales_data),
            "avg_transaction": sum(s.get("Total", 0) for s in self.sales_data) / max(len(self.sales_data), 1),
        }
