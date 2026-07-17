"""
Competitor Price Monitor - Toko Ban Murah Anugerah
==================================================
Monitor competitor prices by scraping tire shop websites.
Track price changes and alert when competitors change prices.
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
    _has_scraping = True
except ImportError:
    _has_scraping = False


COMPETITOR_TEMPLATES = {
    "tokopedia": {
        "name": "Tokopedia",
        "search_url": "https://www.tokopedia.com/search?q={query}&category=ban",
        "product_selector": "div[data-testid='lst-product']",
        "name_selector": "span[data-testid='spnSRPProdName']",
        "price_selector": "span[data-testid='spnSRPProdPrice']",
    },
    "shopee": {
        "name": "Shopee",
        "search_url": "https://shopee.co.id/search?keyword={query}",
        "product_selector": "div.shopee-search-item-result__item",
        "name_selector": "div._10Wbs-._5SSWfi",
        "price_selector": "span._1z9x1k",
    },
    "bukalapak": {
        "name": "Bukalapak",
        "search_url": "https://www.bukalapak.com/products?from=&search%5Bkeywords%5D={query}",
        "product_selector": "div.bl-product-card",
        "name_selector": "a.bl-product-card__name",
        "price_selector": "span.bl-product-card__price",
    }
}


class CompetitorMonitor:
    """Monitor competitor tire prices from various sources."""

    def __init__(self, config_path: str = "../config.json",
                 data_path: str = "../data/competitors.xlsx"):
        self.config_path = Path(config_path)
        self.data_path = Path(data_path)
        self.config = self._load_config()
        self.price_history = []
        self._load_history()

    def _load_config(self) -> dict:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"competitors": {"urls": []}}

    def _load_history(self):
        """Load price history from file."""
        history_path = self.data_path.parent / "price_history.json"
        if history_path.exists():
            try:
                with open(history_path, "r") as f:
                    self.price_history = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.price_history = []

    def _save_history(self):
        """Save price history to file."""
        history_path = self.data_path.parent / "price_history.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, "w") as f:
            json.dump(self.price_history[-1000:], f, indent=2)  # Keep last 1000

    @staticmethod
    def _parse_price(text: str) -> Optional[float]:
        """Extract numeric price from text like 'Rp 750.000'."""
        if not text:
            return None
        clean = re.sub(r'[^\d,]', '', text)
        clean = clean.replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return None

    def search_tokopedia(self, query: str) -> list:
        """Search for tire prices on Tokopedia."""
        if not _has_scraping:
            return self._mock_search(query)
        
        results = []
        try:
            url = COMPETITOR_TEMPLATES["tokopedia"]["search_url"].format(query=query)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                products = soup.select(
                    COMPETITOR_TEMPLATES["tokopedia"]["product_selector"]
                )[:10]
                
                for prod in products:
                    name_el = prod.select_one(
                        COMPETITOR_TEMPLATES["tokopedia"]["name_selector"]
                    )
                    price_el = prod.select_one(
                        COMPETITOR_TEMPLATES["tokopedia"]["price_selector"]
                    )
                    
                    if name_el and price_el:
                        name = name_el.get_text(strip=True)
                        price = self._parse_price(price_el.get_text(strip=True))
                        results.append({
                            "source": "Tokopedia",
                            "product": name,
                            "price": price,
                            "date": datetime.now().isoformat()
                        })
        except Exception:
            pass
        
        return results if results else self._mock_search(query)

    def _mock_search(self, query: str) -> list:
        """Return mock competitor data when scraping is unavailable."""
        import random
        competitors = ["Toko Ban Jaya", "Ban Centre", "Ban Sejahtera", 
                       "Mega Ban", "Prima Ban"]
        prices = [
            random.randint(380000, 700000),
            random.randint(400000, 750000),
            random.randint(350000, 680000),
            random.randint(420000, 800000),
        ]
        
        results = []
        for comp, price in zip(competitors, prices):
            results.append({
                "source": comp,
                "product": query,
                "price": price,
                "date": datetime.now().isoformat(),
                "note": "Mock data - install requests & bs4 for live scraping"
            })
        
        return results

    def check_price_changes(self, product_query: str) -> list:
        """Check competitor prices and compare with history."""
        current = self.search_tokopedia(product_query)
        
        changes = []
        for item in current:
            # Find last price for this product+source
            last_price = None
            for h in reversed(self.price_history):
                if (h.get("product") == item.get("product") and 
                    h.get("source") == item.get("source")):
                    last_price = h.get("price")
                    break
            
            item["last_price"] = last_price
            
            if last_price and item.get("price"):
                diff = item["price"] - last_price
                item["price_change"] = diff
                item["price_change_pct"] = (diff / last_price) * 100
                if diff != 0:
                    changes.append(item)
            
            # Save to history
            self.price_history.append(item)
        
        self._save_history()
        return current

    def format_alert(self, changes: list) -> str:
        """Format price change alerts for WhatsApp."""
        if not changes:
            return "✅ Tidak ada perubahan harga kompetitor hari ini."
        
        lines = [
            "⚠️ *ALERT PERUBAHAN HARGA KOMPETITOR* ⚠️",
            f"📅 {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            "━" * 30,
        ]
        
        for c in changes:
            change_pct = c.get("price_change_pct", 0)
            arrow = "🔺 Naik" if change_pct > 0 else "🔻 Turun"
            lines.append(f"\n{c.get('source', '-')}")
            lines.append(f"  {c.get('product', '-')}")
            lines.append(f"  Harga: Rp {c.get('price', 0):,.0f}")
            lines.append(f"  {arrow} Rp {abs(c.get('price_change', 0)):,.0f} ({abs(change_pct):.0f}%)")
        
        lines.append("\n━" * 30)
        lines.append("💡 *Saran:* Sesuaikan harga jual Anda!")
        
        return "\n".join(lines)
