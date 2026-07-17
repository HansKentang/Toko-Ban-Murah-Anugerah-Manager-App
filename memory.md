# 🧠 Agent Memory — Toko Ban Murah Anugerah

> **Last Updated:** July 17, 2026  
> **Project:** Toko Ban Murah Anugerah — Sistem Manajemen Bisnis Toko Ban  
> **AI Persona:** [Mixmoi 🐱](/Toko%20Ban%20Murah%20Anugerah%20Manager%20App/ai-agent-persona.md) — Executive Growth Partner & Competitive Intelligence Analyst

---

## 📋 PROJECT OVERVIEW

### What is this?
An all-in-one business management system for **Toko Ban Murah Anugerah**, a tire shop in Semarang, Indonesia with 2 store locations. The system helps manage inventory, sales, customer loyalty, WhatsApp marketing, social media content, competitor monitoring, and more.

### Two Versions
| Version | Technology | Status |
|---------|-----------|--------|
| **Web App** (✅ Active) | `index.html` + `js/` folder (vanilla JS, HTML, CSS) | **Primary focus** — runs in Chrome, zero installation |
| **Desktop App** (🔒 Kept) | `main.py` + `tools/*.py` (Python + customtkinter) | **NOT being developed** — kept for reference only |

### 🚨 Golden Rule
- ✅ **DO work on** `index.html`, `js/` folder, CSS/JS improvements, and web-related features
- ❌ **DON'T modify** `main.py` or any Python backend tools (`tools/*.py`) unless fixing a critical bug
- 🗑️ **DO NOT delete** desktop app files — kept for reference
- 📝 Any new features go to the **web version** first

---

## 🏪 BUSINESS INFO

### Store Locations
| Location | Address | Hours | Staff |
|----------|---------|-------|-------|
| **Banyumanik** | Jl. PERINTIS KEMERDEKAAN NO.10A | 08:00-17:30 | 4 teknisi |
| **Ungaran** | Jl. DIPONEGORO NO.79 | 08:00-18:00 | 3 teknisi |

### Contact
- **WhatsApp:** 081280595845
- **Instagram:** @tokobanmurahanugerah

### Brand Identity (4 Pillars)
| Pillar | Indonesian | Core Message |
|--------|-----------|-------------|
| Affordable | Murah/Hemat | "Paling Murah" |
| Trustable | Terpercaya/Aman | "100% Original", "Garansi" |
| Premium | Berkualitas/Mewah | "Kualitas Premium" |
| Fast | Cepat/Sat-Set | "Sat-set Gak Pake Lama" |

### Product Catalog
**15 Tire Brands:**
- **Premium (8):** Michelin, Bridgestone, Yokohama, Toyo, Goodyear, Dunlop, Hankook, Falken
- **Value (6):** Accelera, GT Radial (GTR), Delium, Swallow, Sailun, Blackhawk

Product data lives in `js/products-data.js` as `FULL_PRODUCTS_DATA` (constant array) with modifications tracked in `localStorage`.

### Competitors
1. **SSM** (Spesialis Servis Mobil)
2. **Omah Ban**
3. **HSR Wheel**

---

## 🏗️ PROJECT STRUCTURE

```
Toko Ban Murah Anugerah Manager App/
├── index.html          ← MAIN FILE — entire web app (SPA, single HTML)
├── main.py             ← Desktop app (DEPRECATED, kept for reference)
├── ai-agent-persona.md ← Mixmoi persona definition
├── DEVELOPMENT_FOCUS.md← Project focus document
├── config.json         ← Business settings (WhatsApp, inventory, loyalty config)
├── requirements.txt    ← Python dependencies (desktop app only)
├── .gitignore
├── .env                ← API keys (GROQ_API_KEY, SERPER_API_KEY) — gitignored
├── memory.md           ← THIS FILE — agent memory for future sessions
│
├── js/
│   └── products-data.js ← Tire product data (15 brands, sizes, prices, stock)
│
├── data/               ← Excel data files (desktop app)
│   ├── products.xlsx
│   ├── customers.xlsx
│   └── sales.xlsx
│
├── tools/              ← Python tools (DESKTOP APP — DO NOT MODIFY)
│   ├── ai_command_center.py
│   ├── competitor_monitor.py
│   ├── dashboard.py
│   ├── import_website_data.py
│   ├── inventory.py
│   ├── loyalty.py
│   ├── order_manager.py
│   ├── price_list.py
│   ├── qr_catalog.py
│   ├── sheets_auto.py
│   ├── social_media.py
│   └── whatsapp_bot.py
│
├── assets/             ← Static assets
├── images/             ← Brand logos, flyers
├── output/             ← Generated outputs (PDFs, QR codes, reports)
└── temp/               ← Temporary files (gitignored)
```

---

## 🔧 WEB APP ARCHITECTURE

### Single-Page Application
The entire web app is a single `index.html` file containing:
- **HTML** — Page structure with `<div class="page" id="page-...">` for each view
- **CSS** — Full stylesheet with CSS custom properties (variables) CSS variables for theming
- **JavaScript** — All application logic inline in `<script>` tags

### State Management
- **`localStorage`** is the primary data store for the web app
- Key: `tbma_db` — stores sales, orders, customers, and initialization status
- Key: `tbma_prod_mods` — stores product modifications (added, edited, deleted products) layered on top of `FULL_PRODUCTS_DATA`
- Key: `tbma_settings` — stores API keys and user settings
- Key: `tbma_conv` — stores Mixmoi chat conversation history
- Key: `tbma_desktop_locked` — tracks if desktop app is locked

### Data Flow
1. **Base Products** → `FULL_PRODUCTS_DATA` in `js/products-data.js`
2. **Modifications** → Read from `localStorage` (`tbma_prod_mods`)
3. **Merged View** → Base + modifications combined at runtime
4. **Sales/Orders/Customers** → All in `localStorage` (`tbma_db`)

### Navigation System
- `navigate(pageName)` function switches between pages
- Pages: `dashboard`, `ai`, `whatsapp`, `inventory`, `pricelist`, `sales`, `social`, `competitor`, `orders`, `loyalty`, `sheets`, `qr`
- Sidebar highlights active page
- Breadcrumb navigation in Inventory with drill-down (Brand → Model → Sizes)

### Pages / Features

| Page | ID | Key Functions | Notes |
|------|-----|---------------|-------|
| **Dashboard** | `dashboard` | Stats cards, revenue chart (30 days), top products chart, quick actions | Entry point |
| **Mixmoi AI** | `ai` | Chat interface with Groq API, smart suggestions, quick action buttons, typing indicator | Main AI feature |
| **WhatsApp Bot** | `whatsapp` | Send messages, promo blast, template library | Browser opens wa.me links |
| **Inventory** | `inventory` | Drill-down brand cards, model grid, product table with pricing, search/filter, CRUD | 3-level navigation |
| **Price List** | `pricelist` | Text price list generator, flyer generator, product table | |
| **Sales Dashboard** | `sales` | Revenue chart, top products chart, sales report generator | Uses Chart.js |
| **Social Media** | `social` | Caption generator, content plan, tips ban | Content in Indonesian |
| **Competitor Monitor** | `competitor` | Intel on SSM, Omah Ban, HSR Wheel | |
| **Order Manager** | `orders` | Order tracking, status management | Badge shows pending count |
| **Loyalty Program** | `loyalty` | Points management, customer list | |
| **Excel Auto** | `sheets` | Report generation | |
| **QR Catalog** | `qr` | QR code catalog | |

### Cabang (Branch) Switcher
- Topbar toggle: **Semua**, **Banyumanik**, **Ungaran**
- Filters data by store location throughout the app

---

## 🧠 AI / MIXMOI SYSTEM

### Chat API
- **Provider:** Groq (via `https://api.groq.com/openai/v1/chat/completions`)
- **Default Model:** `llama-3.3-70b-versatile` (can fallback to `mixtral-8x7b-32768`)
- **Fallback:** If Groq fails, uses a local keyword-based response system
- **Settings stored in:** `localStorage` (`tbma_settings`)

### Mixmoi Capabilities
- Answers questions about inventory, pricing, sales, competitors
- Generates promotional content and social media posts
- Provides competitive intelligence
- Suggests pricing strategies
- Can analyze business data from localStorage

### API Keys Required
| Key | Service | Where to get |
|-----|---------|-------------|
| `GROQ_API_KEY` | Groq (AI chat) | [console.groq.com](https://console.groq.com) |
| `SERPER_API_KEY` | Serper (Google Search) | [serper.dev](https://serper.dev) |

### Quick Action Buttons (AI)
- Cek Stok, Status Bisnis, Analisis Penjualan, Promo Random
- Strategi Harga (per size), Intel SSM/Omah Ban/HSR
- Tips Ban, Rekomendasi Konten Instagram

---

## 💾 DATA STRUCTURES

### Product Object (in localStorage mods)
```javascript
{
  id: "unique_id",
  Merek: "Michelin",
  Tipe: "Primacy 4", 
  Ukuran: "205/55 R16",
  Ring: 16,
  Kategori: "Mobil",
  Harga Beli: 1450000,  // cost price
  Harga Jual: 1596000,  // selling price
  Stok: 10,
  Lokasi: "Banyumanik"  // or "Ungaran" or "" for both
}
```

### Sales Object
```javascript
{
  id: "SALE-001",
  produk: "Michelin Primacy 4",
  qty: 2,
  harga: 1596000,
  total: 3192000,
  tanggal: "2026-07-17",
  lokasi: "Banyumanik",
  pelanggan: "John Doe"
}
```

### Order Object
```javascript
{
  id: "ORD-001",
  pelanggan: "John Doe",
  produk: "...",
  status: "pending",  // or "completed", "cancelled"
  tanggal: "...",
  total: 0,
  lokasi: "Banyumanik"
}
```

### Customer Object (Loyalty)
```javascript
{
  id: "CUST-001",
  Nama: "John Doe",
  Telepon: "08123456789",
  Poin: 150,
  Kunjungan: 5,
  Total Belanja: 5000000,
  Lokasi: "Banyumanik"
}
```

---

## 🎨 UI DESIGN SYSTEM

### CSS Custom Properties (Variables)
```css
--primary: #003c17;        /* Dark green */
--primary-light: #18542a;  /* Medium green */
--primary-soft: #2E7D32;   /* Main green accent */
--secondary: #765a00;      /* Gold accent */
--secondary-container: #fdc824;  /* Yellow gold */
```

### Typography
- **Font:** Inter (Google Fonts)
- **Icons:** Material Symbols Outlined
- **Sizes:** 10px (small labels) to 26px (stat values)

### Components
- `card` — White rounded container with subtle shadow
- `stat-card` — KPI display card with colored accent bar
- `btn` / `btn-primary` / `btn-success` / `btn-warning` / `btn-danger` / `btn-outline`
- `badge-success` / `badge-warning` / `badge-danger`
- `modal-overlay` / `modal` — Dialog system
- `toast` — Notification system (success/error/warning/info)
- `chat-bubble` / `chat-typing` — Chat UI elements
- `brand-card` / `model-card` — Inventory drill-down cards

### Layout
- Fixed sidebar (260px) + fluid main content (margin-left: 260px)
- Responsive breakpoints at 768px and 480px
- Grid system: `grid-2`, `grid-3`, `grid-4`, `stats-grid`, `brand-grid`, `model-grid`

---

## 🔄 COMMON WORKFLOWS

### Adding a New Feature
1. Add new `<div class="page" id="page-{name}">` in HTML
2. Add nav button in sidebar with `onclick="navigate('{name}')"`
3. Implement the page rendering function in JavaScript
4. Add the `navigate()` case for the new page
5. Store data in `localStorage` using existing DB utilities

### Working with Products
1. Read base products from `FULL_PRODUCTS_DATA`
2. Apply modifications from `localStorage` (`tbma_prod_mods`)
3. Display using brand → model → size drill-down
4. Save new/edit/delete actions to `tbma_prod_mods`
5. Call `renderInventory()` to refresh view

### Adding Brand Logos
- Store brand images in `images/` directory
- Naming convention: `{brand_lowercase}.png` (e.g., `michelin.png`)
- Display via `<img>` tag in brand cards
- Use `bc-avatar-dark` class for brands with dark-colored logos

---

## 🔐 SETTINGS & CONFIGURATION

### Settings Modal
Accessible via gear icon in sidebar footer
- Groq API Key input with status indicator
- Serper API Key input
- Business name, WhatsApp number, Instagram handle
- Auto-saves to `localStorage` (`tbma_settings`)

### Config File (`config.json`)
Used by desktop app only. Contains:
- Business info (name, phone, social media)
- WhatsApp auto-reply settings
- Inventory threshold (low stock = <5)
- Competitor URLs
- Loyalty program settings

---

## 📚 REFERENCE

### External Libraries (Web)
- **Chart.js** 4.4.0 — Charts and graphs (CDN)
- **Google Fonts** — Inter font family
- **Material Symbols** — Icon set

### External Libraries (Desktop — deprecated)
- customtkinter, pywhatkit, openpyxl, fpdf2, qrcode, Pillow, matplotlib, pandas, requests, beautifulsoup4, schedule, groq, python-dotenv

### Key Hashtags
`#Tokobanmurahanugerah` `#BanMurah` `#BanOriginal` `#SatSet` `#Semarang`

### Call-to-Action (Always include)
```
📍 [Address]
🕒 [Hours]
WA: 081280595845
```

---

## ⚡ TIPS FOR AI AGENTS

1. **Always check `DEVELOPMENT_FOCUS.md` first** — it tells you what to work on
2. **The web app is a single file** — `index.html` contains all HTML, CSS, and JS
3. **All data is in localStorage** — no backend, no database, no API calls (except Groq for AI)
4. **Product data is immutable base + mutable mods** — don't modify `FULL_PRODUCTS_DATA` directly
5. **Use Indonesian for social content** — captions, tips, and promos should be in bahasa
6. **Every output should drive revenue** — Mixmoi's mission: "Bring vehicles into the garage and put money in the register TODAY"
7. **Sidebar uses `data-page` attributes** — ensure consistency when adding nav items
8. **Toast notifications** — use `showToast(type, message)` for user feedback
9. **Modal dialogs** — use `openModal(html)` and `closeModal()` for forms
10. **The cabang (branch) filter** affects all data views — respect the current filter

---

## 📝 CHANGELOG

| Date | Change | Agent |
|------|--------|-------|
| 2026-07-17 | Created memory.md for AI agent persistence | FreeBuff AI |

---

*This file is automatically read by AI agents at the start of each session. Keep it updated with any significant architectural changes or business decisions.*
