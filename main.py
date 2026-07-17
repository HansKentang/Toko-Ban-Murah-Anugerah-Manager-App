"""
Toko Ban Murah Anugerah - Business Management System
====================================================
All-in-one desktop application for managing your tire shop.
Includes 10 powerful tools to boost sales and promotions.

Author: Freebuff AI
"""

import os
import sys
import json
import webbrowser
import subprocess
from pathlib import Path
from datetime import datetime
from threading import Thread
from typing import Optional

# Load environment variables from .env file (for API keys)
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
if env_path.exists():
  load_dotenv(dotenv_path=str(env_path))
  print(f"[*] Loaded environment from {env_path}")

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# ─── Try importing GUI framework ────────────────────────────────────────────
try:
  import customtkinter as ctk
  from tkinter import messagebox, filedialog, ttk
  _has_customtkinter = True
except ImportError:
  _has_customtkinter = False
  import tkinter as tk
  from tkinter import messagebox, filedialog, ttk
  # Fallback: use tkinter with ttk
  ctk = None

# ─── Import tools ───────────────────────────────────────────────────────────
from tools.whatsapp_bot import WhatsAppBot, TIRE_TEMPLATES
from tools.inventory import InventoryManager, TIRE_BRANDS, CATEGORIES, TIRE_SIZES_CAR
from tools.price_list import PriceListGenerator
from tools.dashboard import SalesDashboard
from tools.social_media import SocialMediaScheduler
from tools.competitor_monitor import CompetitorMonitor
from tools.order_manager import OrderManager
from tools.loyalty import LoyaltyProgram
from tools.sheets_auto import SheetsAutomation
from tools.qr_catalog import QRCatalog
from tools.ai_command_center import AICommandCenter, AGENT_DEFINITIONS, AGENTS_BY_ID


# ─── Constants ──────────────────────────────────────────────────────────────
BUSINESS_NAME = "Toko Ban Murah Anugerah"
APP_VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Colors
COLORS = {
  "primary": "#2E7D32",
  "primary_light": "#43A047",
  "secondary": "#A5D6A7",
  "success": "#2E7D32",
  "danger": "#E53935",
  "warning": "#FFB300",
  "dark": "#1B5E20",
  "white": "#FFFFFF",
  "light_bg": "#f1f8e9",
  "text": "#333333",
  "text_light": "#666666",
}



class TokoBanApp:
  """Main application class."""

  def __init__(self):
    self.root = ctk.CTk() if _has_customtkinter else tk.Tk()
    self.root.title(f"{BUSINESS_NAME} - Sistem Manajemen")
    self.root.geometry("1280x800")
    
    # Set theme
    if _has_customtkinter:
      ctk.set_appearance_mode("light")
      ctk.set_default_color_theme("green")
    
    # Initialize tools
    self.tools = self._init_tools()
    
    # Build UI
    self._build_ui()
    
    # Start with dashboard
    self._show_frame("dashboard")

  def _init_tools(self) -> dict:
    """Initialize all business tools."""
    tools = {
      "whatsapp": WhatsAppBot(str(CONFIG_PATH)),
      "inventory": InventoryManager(str(DATA_DIR / "products.xlsx")),
      "price_list": PriceListGenerator(BUSINESS_NAME, 
                       str(OUTPUT_DIR / "price_lists")),
      "dashboard": SalesDashboard(str(DATA_DIR / "sales.xlsx"),
                    str(OUTPUT_DIR / "reports")),
      "social": SocialMediaScheduler(BUSINESS_NAME, "", 
                      str(DATA_DIR / "social_posts.xlsx")),
      "competitor": CompetitorMonitor(str(CONFIG_PATH)),
      "orders": OrderManager(str(DATA_DIR / "orders.xlsx")),
      "loyalty": LoyaltyProgram(str(CONFIG_PATH), 
                   str(DATA_DIR / "customers.xlsx")),
      "sheets": SheetsAutomation(str(OUTPUT_DIR / "reports")),
      "qr_catalog": QRCatalog(BUSINESS_NAME, "",
                  str(OUTPUT_DIR / "qr_codes")),
    }
    # Get Groq API key from environment (if available)
    groq_api_key = os.environ.get("GROQ_API_KEY", "")
    
    # Initialize AI Command Center with reference to all tools
    tools["ai"] = AICommandCenter(tools, groq_api_key=groq_api_key)
    return tools

  # ─── UI Builder ──────────────────────────────────────────────────────
  def _build_ui(self):
    """Build the main user interface."""
    if not _has_customtkinter:
      self._build_ui_tkinter()
      return

    # Main container
    self.root.grid_columnconfigure(0, weight=0) # Sidebar
    self.root.grid_columnconfigure(1, weight=1) # Content
    self.root.grid_rowconfigure(0, weight=1)

    # ── Sidebar ──
    self.sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0,
                  fg_color=COLORS["primary"])
    self.sidebar.grid(row=0, column=0, sticky="nsew")
    self.sidebar.grid_rowconfigure(0, weight=0)
    self.sidebar.grid_rowconfigure(1, weight=0)
    self.sidebar.grid_rowconfigure(2, weight=1)
    self.sidebar.grid_rowconfigure(3, weight=0)

    # Logo area
    logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
    logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
    
    ctk.CTkLabel(logo_frame, text="", font=ctk.CTkFont(size=40)).pack()
    ctk.CTkLabel(logo_frame, text=BUSINESS_NAME, 
           font=ctk.CTkFont(size=16, weight="bold"),
           text_color="white").pack()
    ctk.CTkLabel(logo_frame, text="Sistem Manajemen", 
           font=ctk.CTkFont(size=11),
           text_color="#aabbcc").pack()

    # Separator
    separator = ctk.CTkFrame(self.sidebar, height=2, 
                 fg_color=COLORS["primary_light"])
    separator.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

    # Navigation buttons
    self.nav_buttons_frame = ctk.CTkScrollableFrame(
      self.sidebar, fg_color="transparent", scrollbar_button_color=COLORS["primary_light"])
    self.nav_buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    self.nav_buttons_frame.grid_columnconfigure(0, weight=1)

    self.nav_items = [
      ("", "Dashboard", "dashboard"),
      ("", "AI Command", "ai"),
      ("", "WhatsApp Bot", "whatsapp"),
      ("", "Inventory", "inventory"),
      ("", "Price List", "price_list"),
      ("", "Sales Dashboard", "sales_chart"),
      ("", "Social Media", "social"),
      ("", "Competitor Monitor", "competitor"),
      ("", "Order Manager", "orders"),
      ("", "Loyalty Program", "loyalty"),
      ("", "Excel Auto", "sheets"),
      ("", "QR Catalog", "qr_catalog"),
    ]

    self.nav_buttons = {}
    for icon, label, key in self.nav_items:
      btn = ctk.CTkButton(
        self.nav_buttons_frame,
        text=f" {icon} {label}",
        font=ctk.CTkFont(size=13),
        fg_color="transparent",
        text_color="white",
        hover_color=COLORS["primary_light"],
        anchor="w",
        height=40,
        command=lambda k=key: self._show_frame(k),
        corner_radius=8,
      )
      btn.pack(fill="x", pady=2)
      self.nav_buttons[key] = btn

    # Bottom section
    bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
    bottom_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
    
    # Settings button + version side by side
    settings_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    settings_row.pack(fill="x")
    
    self.groq_status_indicator = ctk.CTkLabel(
      settings_row, text="●", font=ctk.CTkFont(size=14),
      text_color="#888888"
    )
    self.groq_status_indicator.pack(side="left", padx=(5, 2))
    
    ctk.CTkLabel(settings_row, text=f"v{APP_VERSION}",
           font=ctk.CTkFont(size=10),
           text_color="#667788").pack(side="left")
    
    settings_btn = ctk.CTkButton(
      settings_row, text="", width=32, height=32,
      fg_color="transparent", text_color="#8899aa",
      hover_color=COLORS["primary_light"],
      font=ctk.CTkFont(size=14),
      command=self._open_api_settings,
      corner_radius=16,
      tooltip="API Settings"
    )
    settings_btn.pack(side="right")

    # ── Content Area ──
    self.content_frame = ctk.CTkFrame(self.root, fg_color=COLORS["light_bg"],
                     corner_radius=0)
    self.content_frame.grid(row=0, column=1, sticky="nsew")
    self.content_frame.grid_columnconfigure(0, weight=1)
    self.content_frame.grid_rowconfigure(0, weight=1)

    # Content container
    self.content_container = ctk.CTkFrame(self.content_frame, 
                        fg_color="transparent")
    self.content_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    self.content_container.grid_columnconfigure(0, weight=1)
    self.content_container.grid_rowconfigure(0, weight=1)

    # Store frames
    self.frames = {}

  def _build_ui_tkinter(self):
    """Fallback UI using tkinter if customtkinter not available."""
    self.root.configure(bg=COLORS["light_bg"])
    
    # Simple menu bar
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)
    
    tools_menu = tk.Menu(menubar, tearoff=0)
    for icon, label, key in [
      ("", "Dashboard", "dashboard"),
      ("", "WhatsApp Bot", "whatsapp"),
      ("", "Inventory", "inventory"),
      ("", "Price List", "price_list"),
      ("", "Sales Dashboard", "sales_chart"),
      ("", "Social Media", "social"),
      ("", "Competitor Monitor", "competitor"),
      ("", "Order Manager", "orders"),
      ("", "Loyalty Program", "loyalty"),
      ("", "Excel Auto", "sheets"),
      ("", "QR Catalog", "qr_catalog"),
    ]:
      tools_menu.add_command(label=label, command=lambda k=key: self._show_frame(k))
    
    menubar.add_cascade(label="Tools", menu=tools_menu)
    menubar.add_command(label="AI Command Center", command=lambda: self._show_frame("ai"))
    menubar.add_command(label="Exit", command=self.root.quit)

    # Main content
    self.content_frame = tk.Frame(self.root, bg=COLORS["light_bg"])
    self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    self.content_container = tk.Frame(self.content_frame, bg=COLORS["light_bg"])
    self.content_container.pack(fill="both", expand=True)

    self.frames = {}

  # ─── Navigation ──────────────────────────────────────────────────────
  def _show_frame(self, key: str):
    """Switch to a specific tool frame."""
    # Clear container
    for widget in self.content_container.winfo_children():
      widget.destroy()
    
    # Highlight active nav button
    if _has_customtkinter:
      for k, btn in self.nav_buttons.items():
        if k == key:
          btn.configure(fg_color=COLORS["primary_light"])
        else:
          btn.configure(fg_color="transparent")

    # Show selected frame
    frame_methods = {
      "dashboard": self._build_dashboard,
      "ai": self._build_ai,
      "whatsapp": self._build_whatsapp,
      "inventory": self._build_inventory,
      "price_list": self._build_price_list,
      "sales_chart": self._build_sales_chart,
      "social": self._build_social,
      "competitor": self._build_competitor,
      "orders": self._build_orders,
      "loyalty": self._build_loyalty,
      "sheets": self._build_sheets,
      "qr_catalog": self._build_qr_catalog,
    }
    
    method = frame_methods.get(key)
    if method:
      method()

  # ─── Dashboard ───────────────────────────────────────────────────────
  def _build_dashboard(self):
    """Build the main dashboard with quick stats."""
    frame = self._create_scrollable_frame()
    
    # Header
    header = ctk.CTkLabel(frame, text="Dashboard Utama",
               font=ctk.CTkFont(size=28, weight="bold"),
               text_color=COLORS["primary"]) if _has_customtkinter else \
         tk.Label(frame, text="Dashboard Utama", font=("Arial", 20, "bold"),
             bg=COLORS["light_bg"], fg=COLORS["primary"])
    header.pack(anchor="w", pady=(0, 20))

    # Stats cards
    stats_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
           tk.Frame(frame, bg=COLORS["light_bg"])
    stats_frame.pack(fill="x")

    # Get stats
    inv_summary = self.tools["inventory"].get_summary()
    dash_stats = self.tools["dashboard"].get_stats()
    
    stat_cards = [
      ("Total Produk", str(inv_summary.get("total_items", 0)), 
       "Semua produk di inventory", COLORS["primary"]),
      ("Pendapatan", f"Rp {dash_stats.get('total_revenue', 0):,.0f}",
       "Total penjualan", COLORS["success"]),
      ("Stok Menipis", str(inv_summary.get("low_stock_count", 0)),
       "Perlu restock segera", COLORS["warning"]),
      ("Pesanan Aktif", str(self.tools["orders"].get_summary().get("pending", 0)),
       "Pesanan belum selesai", COLORS["danger"]),
    ]

    if _has_customtkinter:
      for i, (icon_label, value, desc, color) in enumerate(stat_cards):
        card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12,
                  border_width=1, border_color="#e0e0e0")
        card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)
        
        # Color accent bar
        accent = ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0)
        accent.pack(fill="x")
        
        ctk.CTkLabel(card, text=icon_label, font=ctk.CTkFont(size=14),
              text_color=COLORS["text"]).pack(pady=(15, 5))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"),
              text_color=color).pack()
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11),
              text_color=COLORS["text_light"]).pack(pady=(5, 15))
    else:
      # tkinter fallback
      for i, (icon_label, value, desc, color) in enumerate(stat_cards):
        card = tk.LabelFrame(stats_frame, text=icon_label, 
                   font=("Arial", 10), bg="white", fg=color)
        card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)
        tk.Label(card, text=value, font=("Arial", 20, "bold"),
            bg="white", fg=color).pack(pady=10)
        tk.Label(card, text=desc, font=("Arial", 9),
            bg="white", fg="#666").pack(pady=5)

    # Quick actions
    actions_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
            tk.Frame(frame, bg=COLORS["light_bg"])
    actions_frame.pack(fill="x", pady=(30, 10))

    action_label = ctk.CTkLabel(actions_frame, text="Aksi Cepat",
                   font=ctk.CTkFont(size=18, weight="bold"),
                   text_color=COLORS["primary"]) if _has_customtkinter else \
            tk.Label(actions_frame, text="Aksi Cepat",
                font=("Arial", 14, "bold"), bg=COLORS["light_bg"],
                fg=COLORS["primary"])
    action_label.pack(anchor="w", pady=(0, 10))

    quick_actions = [
      ("Kirim Promo WhatsApp", self._action_whatsapp_promo,
       "Kirim pesan promo ke pelanggan"),
      ("Cek Stok Menipis", self._action_low_stock,
       "Lihat produk yang perlu di-restock"),
      ("Buat Daftar Harga", self._action_price_list,
       "Generate PDF daftar harga terbaru"),
      ("Generate Laporan", self._action_report,
       "Buat laporan penjualan Excel"),
    ]

    if _has_customtkinter:
      for i, (text, command, desc) in enumerate(quick_actions):
        btn = ctk.CTkButton(actions_frame, text=text,
                  font=ctk.CTkFont(size=13),
                  fg_color="white", text_color=COLORS["primary"],
                  hover_color="#e8f5e9", command=command,
                  height=70, corner_radius=12,
                  border_width=1, border_color="#d0d0d0")
        btn.pack(fill="x", pady=4)

    # Bottom info
    info_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
          tk.Frame(frame, bg=COLORS["light_bg"])
    info_frame.pack(fill="x", pady=(30, 0))
    
    info_text = "Tips: Gunakan menu sidebar untuk mengakses semua tools bisnis Anda."
    info_label = ctk.CTkLabel(info_frame, text=info_text,
                  font=ctk.CTkFont(size=12),
                  text_color=COLORS["text_light"],
                  wraplength=600) if _has_customtkinter else \
           tk.Label(info_frame, text=info_text, font=("Arial", 10),
               bg=COLORS["light_bg"], fg=COLORS["text_light"],
               wraplength=600)
    info_label.pack()

  def _action_whatsapp_promo(self):
    """Quick action: open WhatsApp promo."""
    self._show_frame("whatsapp")

  def _action_low_stock(self):
    """Quick action: show low stock products."""
    self._show_frame("inventory")

  def _action_price_list(self):
    """Quick action: generate price list."""
    self._show_frame("price_list")

  def _action_report(self):
    """Quick action: generate report."""
    self._show_frame("sheets")

  # ─── WhatsApp Bot ────────────────────────────────────────────────────
  def _build_whatsapp(self):
    """Build WhatsApp Bot interface."""
    frame = self._create_scrollable_frame()

    header = self._create_header(frame, "WhatsApp Auto-Reply & Bulk Messenger",
                   "Kirim pesan otomatis, blasting promo, dan template replies")
    
    # ── Send Message Section ──
    self._create_section_title(frame, "📤 Kirim Pesan")
    
    msg_frame = self._create_card(frame)
    
    # Phone
    phone_frame = ctk.CTkFrame(msg_frame, fg_color="transparent") if _has_customtkinter else \
           tk.Frame(msg_frame, bg="white")
    phone_frame.pack(fill="x", pady=5)
    
    if _has_customtkinter:
      ctk.CTkLabel(phone_frame, text="Nomor Telepon:", width=120,
            font=ctk.CTkFont(size=13)).pack(side="left")
      self.whatsapp_phone_entry = ctk.CTkEntry(phone_frame, placeholder_text="08123456789",
                           width=300)
      self.whatsapp_phone_entry.pack(side="left", padx=10)
    else:
      tk.Label(phone_frame, text="Nomor Telepon:", font=("Arial", 10),
          bg="white").pack(side="left")
      self.whatsapp_phone_entry = tk.Entry(phone_frame, width=30)
      self.whatsapp_phone_entry.pack(side="left", padx=10)

    # Template selector
    template_frame = ctk.CTkFrame(msg_frame, fg_color="transparent") if _has_customtkinter else \
            tk.Frame(msg_frame, bg="white")
    template_frame.pack(fill="x", pady=5)
    
    if _has_customtkinter:
      ctk.CTkLabel(template_frame, text="Template Pesan:", width=120,
            font=ctk.CTkFont(size=13)).pack(side="left")
      self.whatsapp_template_var = ctk.StringVar(value="promo")
      template_options = list(TIRE_TEMPLATES.keys())
      template_menu = ctk.CTkOptionMenu(template_frame, 
                       values=template_options,
                       variable=self.whatsapp_template_var,
                       width=300)
      template_menu.pack(side="left", padx=10)
    else:
      tk.Label(template_frame, text="Template Pesan:", font=("Arial", 10),
          bg="white").pack(side="left")
      self.whatsapp_template_var = tk.StringVar(value="promo")
      template_menu = ttk.Combobox(template_frame, 
                     values=list(TIRE_TEMPLATES.keys()),
                     textvariable=self.whatsapp_template_var,
                     width=28)
      template_menu.pack(side="left", padx=10)

    # Message preview
    preview_frame = ctk.CTkFrame(msg_frame, fg_color="transparent") if _has_customtkinter else \
            tk.Frame(msg_frame, bg="white")
    preview_frame.pack(fill="x", pady=5)
    
    if _has_customtkinter:
      ctk.CTkLabel(preview_frame, text="Pratinjau Pesan:", width=120,
            font=ctk.CTkFont(size=13)).pack(side="left")
      self.whatsapp_preview_text = ctk.CTkTextbox(preview_frame, height=120, width=500)
      self.whatsapp_preview_text.pack(side="left", padx=10)
    else:
      tk.Label(preview_frame, text="Pratinjau Pesan:", font=("Arial", 10),
          bg="white").pack(side="left")
      self.whatsapp_preview_text = tk.Text(preview_frame, height=6, width=50)
      self.whatsapp_preview_text.pack(side="left", padx=10)

    # Update preview when template changes
    def update_preview(*args):
      template_key = self.whatsapp_template_var.get()
      if _has_customtkinter:
        self.whatsapp_preview_text.delete("1.0", "end")
        self.whatsapp_preview_text.insert("1.0", TIRE_TEMPLATES.get(template_key, ""))
      else:
        self.whatsapp_preview_text.delete("1.0", "end")
        self.whatsapp_preview_text.insert("1.0", TIRE_TEMPLATES.get(template_key, ""))
    
    self.whatsapp_template_var.trace_add("write", update_preview)
    update_preview()

    # Send button
    btn_frame = ctk.CTkFrame(msg_frame, fg_color="transparent") if _has_customtkinter else \
          tk.Frame(msg_frame, bg="white")
    btn_frame.pack(fill="x", pady=10)
    
    def send_whatsapp():
      phone = self.whatsapp_phone_entry.get()
      if _has_customtkinter:
        message = self.whatsapp_preview_text.get("1.0", "end-1c")
      else:
        message = self.whatsapp_preview_text.get("1.0", "end-1c")
      
      if not phone:
        self._show_error("Masukkan nomor telepon!")
        return
      
      try:
        self.tools["whatsapp"].send_whatsapp(phone, message)
        self._show_success("Pesan dikirim! WhatsApp akan terbuka.")
      except Exception as e:
        self._show_error(f"Gagal: {e}")

    if _has_customtkinter:
      ctk.CTkButton(btn_frame, text="📤 Kirim Pesan", command=send_whatsapp,
             font=ctk.CTkFont(size=14, weight="bold"),
             fg_color=COLORS["success"], hover_color="#1B5E20",
             height=40, width=200).pack(side="left", padx=5)
    else:
      tk.Button(btn_frame, text="📤 Kirim Pesan", command=send_whatsapp,
           bg="#28A745", fg="white", font=("Arial", 10, "bold"),
           padx=20).pack(side="left", padx=5)

    # ── Bulk Send Section ──
    self._create_section_title(frame, "Promo Blast ke Semua Pelanggan")
    
    bulk_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkLabel(bulk_frame, text="Pilih template lalu kirim ke semua pelanggan terdaftar.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_light"]).pack(anchor="w")
      
      ctk.CTkButton(bulk_frame, text="Kirim Promo ke Pelanggan",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["primary"], hover_color=COLORS["primary_light"],
             command=self._bulk_whatsapp).pack(pady=10)
    else:
      tk.Label(bulk_frame, text="Pilih template lalu kirim ke semua pelanggan terdaftar.",
          font=("Arial", 10), bg="white", fg="#666").pack(anchor="w")
      tk.Button(bulk_frame, text="Kirim Promo ke Pelanggan",
           command=self._bulk_whatsapp, bg="#2E7D32", fg="white",
           font=("Arial", 10, "bold")).pack(pady=10)

    # ── Templates List ──
    self._create_section_title(frame, "📚 Library Template Pesan")
    
    templates_frame = self._create_card(frame)
    
    if _has_customtkinter:
      templates_text = ctk.CTkTextbox(templates_frame, height=200)
      templates_text.pack(fill="x", pady=5)
      templates_text.insert("1.0", "Template yang tersedia:\n\n")
      for key, template in TIRE_TEMPLATES.items():
        templates_text.insert("end", f"{key.upper()}\n")
        templates_text.insert("end", f"{template[:100]}...\n\n")
      templates_text.configure(state="disabled")
    else:
      templates_text = tk.Text(templates_frame, height=10)
      templates_text.pack(fill="x", pady=5)
      templates_text.insert("1.0", "Template yang tersedia:\n\n")
      for key, template in TIRE_TEMPLATES.items():
        templates_text.insert("end", f"{key.upper()}\n")
        templates_text.insert("end", f"{template[:100]}...\n\n")
      templates_text.configure(state="disabled")

  def _bulk_whatsapp(self):
    """Send bulk WhatsApp to all customers."""
    try:
      customers = self.tools["loyalty"].customers
      if not customers:
        # Add sample customers
        self.tools["loyalty"].add_sample_customers()
        customers = self.tools["loyalty"].customers
      
      if not customers:
        self._show_error("Belum ada pelanggan terdaftar!")
        return
      
      template_key = self.whatsapp_template_var.get()
      message = TIRE_TEMPLATES.get(template_key, TIRE_TEMPLATES["promo"])
      
      contacts = [{"name": c.get("Nama", ""), "phone": c.get("Telepon", "")} 
            for c in customers]
      
      Thread(target=lambda: self.tools["whatsapp"].bulk_send(contacts, message),
          daemon=True).start()
      
      self._show_success(f"Mengirim ke {len(contacts)} pelanggan... WhatsApp akan terbuka.")
    except Exception as e:
      self._show_error(f"Gagal: {e}")

  # ─── Inventory ──────────────────────────────────────────────────────
  def _build_inventory(self):
    """Build Inventory Management interface with brand drill-down navigation."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Inventory & Stok Ban",
              "Navigasi brand -> model -> ukuran. Kelola stok dan harga ban.")
    
    # Summary cards
    summary = self.tools["inventory"].get_summary()
    
    summary_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
            tk.Frame(frame, bg=COLORS["light_bg"])
    summary_frame.pack(fill="x", pady=(0, 20))
    
    stats = [
      ("Total Produk", str(summary.get("total_items", 0))),
      ("Total Stok", str(summary.get("total_stock", 0))),
      ("Total Nilai", f"Rp {summary.get('total_value', 0):,.0f}"),
      ("Stok Menipis", str(summary.get("low_stock_count", 0)), COLORS["warning"] if summary.get("low_stock_count", 0) > 0 else None),
    ]
    
    if _has_customtkinter:
      for i, stat in enumerate(stats):
        card = ctk.CTkFrame(summary_frame, fg_color="white", corner_radius=10)
        card.grid(row=0, column=i, padx=5, sticky="nsew")
        summary_frame.grid_columnconfigure(i, weight=1)
        
        ctk.CTkLabel(card, text=stat[0], font=ctk.CTkFont(size=12),
              text_color=COLORS["text_light"]).pack(pady=(10, 2))
        color = stat[2] if len(stat) > 2 else COLORS["primary"]
        ctk.CTkLabel(card, text=stat[1], font=ctk.CTkFont(size=22, weight="bold"),
              text_color=color).pack(pady=(0, 10))

    # Navigation bar with back button and breadcrumb
    self._inv_nav_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else tk.Frame(frame)
    self._inv_nav_frame.pack(fill="x", pady=(0, 8))
    
    self._inv_back_btn = ctk.CTkButton(
      self._inv_nav_frame, text="<- Kembali",
      font=ctk.CTkFont(size=12),
      fg_color="transparent", text_color=COLORS["primary"],
      hover_color="#e8f5e9", width=90, height=28,
      corner_radius=8, border_width=1, border_color=COLORS["primary"],
      command=self._inv_go_back
    ) if _has_customtkinter else tk.Button(self._inv_nav_frame, text="<- Kembali", command=self._inv_go_back)
    
    self._inv_breadcrumb = ctk.CTkLabel(
      self._inv_nav_frame, text="",
      font=ctk.CTkFont(size=12),
      text_color=COLORS["text_light"]
    ) if _has_customtkinter else tk.Label(self._inv_nav_frame, text="", fg=COLORS["text_light"])
    self._inv_breadcrumb.pack(side="left", padx=(10, 0))
    
    if _has_customtkinter:
      self._inv_back_btn.pack(side="left")
      self._inv_back_btn.pack_forget()
    
    # Quick action buttons
    action_bar = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
          tk.Frame(frame, bg=COLORS["light_bg"])
    action_bar.pack(fill="x", pady=(0, 10))
    
    if _has_customtkinter:
      ctk.CTkButton(action_bar, text="+ Tambah Produk", 
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["success"], width=130,
             command=self._add_sample_products).pack(side="left", padx=2)
      ctk.CTkButton(action_bar, text="! Stok Menipis", 
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["warning"], text_color="black", width=130,
             command=self._show_low_stock).pack(side="left", padx=2)
      ctk.CTkButton(action_bar, text="Export CSV", 
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["primary"], width=130,
             command=self._export_inventory).pack(side="left", padx=2)
    else:
      tk.Button(action_bar, text="+ Tambah Produk", bg="#28A745", fg="white",
           command=self._add_sample_products).pack(side="left", padx=2)
      tk.Button(action_bar, text="! Stok Menipis", bg="#FFC107", fg="black",
           command=self._show_low_stock).pack(side="left", padx=2)
      tk.Button(action_bar, text="Export CSV", bg="#2E7D32", fg="white",
           command=self._export_inventory).pack(side="left", padx=2)
    
    # Section title for drill-down
    self._create_section_title(frame, "Stok Ban - Navigasi Bertingkat")
    
    # Content area for drill-down navigation
    self._inv_content = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
             tk.Frame(frame, bg=COLORS["light_bg"])
    self._inv_content.pack(fill="both", expand=True)
    
    # Initialize drill-down state and show brands
    self._inv_level = 0 # 0=brands, 1=models, 2=products
    self._inv_brand = None
    self._inv_model = None
    
    self._render_inventory_brands()

  def _get_grouped_products(self):
    """Group products by brand, then by model/tipe."""
    products = self.tools["inventory"].products
    brands = {}
    for p in products:
      brand = p.get("Merek", "Unknown")
      if brand not in brands:
        brands[brand] = {}
      model = p.get("Tipe", "Unknown")
      if model not in brands[brand]:
        brands[brand][model] = []
      brands[brand][model].append(p)
    return brands

  BRAND_COLORS = {
    "Accelera": "#E53935", "Blackhawk": "#212121", "Bridgestone": "#1A237E",
    "Delium": "#00838F", "Dunlop": "#BF360C", "Falken": "#4A148C",
    "Goodyear": "#1B5E20", "GT Radial": "#E65100", "Hankook": "#01579B",
    "Michelin": "#33691E", "Sailun": "#004D40", "Swallow": "#F57F17",
    "Toyo": "#B71C1C", "Yokohama": "#3E2723",
  }
  BRAND_ICONS = {
    "Accelera": "A", "Blackhawk": "B", "Bridgestone": "BS", "Delium": "D",
    "Dunlop": "DL", "Falken": "F", "Goodyear": "GY", "GT Radial": "GT",
    "Hankook": "H",    "Michelin": "M", "Sailun": "S", "Swallow": "SW",
    "Toyo": "T", "Yokohama": "Y",
  }
  BRAND_TIERS = {
    "Michelin": "Premium", "Bridgestone": "Premium", "Yokohama": "Premium",
    "Goodyear": "Premium", "Dunlop": "Premium",
    "Hankook": "Premium", "Falken": "Premium", "Toyo": "Premium",
    "GT Radial": "Value", "Accelera": "Value", "Delium": "Value",
    "Swallow": "Value", "Sailun": "Value", "Blackhawk": "Value",
  }

  def _render_inventory_brands(self):
    """Level 1: Show brand cards grid (like website admin panel)."""
    self._inv_level = 0
    self._inv_brand = None
    self._inv_model = None
    if _has_customtkinter:
      self._inv_back_btn.pack_forget()
      self._inv_breadcrumb.configure(text="Semua Merek")
    
    # Clear content
    for w in self._inv_content.winfo_children():
      w.destroy()
    
    grouped = self._get_grouped_products()
    if not grouped:
      empty = ctk.CTkLabel(self._inv_content, 
        text="Belum ada produk. Klik 'Tambah Produk' untuk mulai.",
        font=ctk.CTkFont(size=14), text_color=COLORS["text_light"]) if _has_customtkinter else \
          tk.Label(self._inv_content, text="Belum ada produk.", bg=COLORS["light_bg"])
      empty.pack(pady=40)
      return
    
    # Grid container
    grid = ctk.CTkFrame(self._inv_content, fg_color="transparent") if _has_customtkinter else \
        tk.Frame(self._inv_content, bg=COLORS["light_bg"])
    grid.pack(fill="x")
    
    sorted_brands = sorted(grouped.keys())
    cols = 4
    
    for idx, brand_name in enumerate(sorted_brands):
      if not _has_customtkinter:
        continue
      row = idx // cols
      col = idx % cols
      
      models = grouped[brand_name]
      total_products = sum(len(prods) for prods in models.values())
      model_count = len(models)
      total_stock = sum(p.get("Stok", 0) for prods in models.values() for p in prods)
      
      brand_color = self.BRAND_COLORS.get(brand_name, COLORS["primary"])
      brand_initials = self.BRAND_ICONS.get(brand_name, brand_name[:2])
      tier = self.BRAND_TIERS.get(brand_name, "")
      
      # Brand card
      card = ctk.CTkFrame(grid, fg_color="white", corner_radius=12,
                border_width=1, border_color="#e0e0e0")
      card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
      grid.grid_columnconfigure(col, weight=1)
      
      # Color accent bar
      accent = ctk.CTkFrame(card, height=4, fg_color=brand_color, corner_radius=0)
      accent.pack(fill="x")
      
      # Brand avatar circle
      avatar = ctk.CTkFrame(card, fg_color=brand_color, corner_radius=20, width=40, height=40)
      avatar.pack(pady=(14, 6))
      avatar.pack_propagate(False)
      ctk.CTkLabel(avatar, text=brand_initials,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white").pack(expand=True)
      
      # Brand name
      ctk.CTkLabel(card, text=brand_name,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text"]).pack(pady=(6, 2))
      
      # Tier badge
      if tier:
        tier_color = COLORS["success"] if tier == "Premium" else COLORS["warning"]
        ctk.CTkLabel(card, text=tier,
              font=ctk.CTkFont(size=9, weight="bold"),
              text_color=tier_color,
              fg_color=tier_color + "18",
              corner_radius=4).pack(pady=2)
      
      # Stats
      ctk.CTkLabel(card,
        text=f"{model_count} seri | {total_products} produk",
        font=ctk.CTkFont(size=11),
        text_color=COLORS["text_light"]).pack(pady=(4, 2))
      
      # Stock info
      stock_color = COLORS["success"] if total_stock > 50 else COLORS["warning"] if total_stock > 10 else COLORS["danger"]
      ctk.CTkLabel(card,
        text=f"Stok: {total_stock} unit",
        font=ctk.CTkFont(size=10, weight="bold"),
        text_color=stock_color).pack(pady=(2, 10))
      
      # Click to drill down
      card.bind("<Button-1>", lambda e, b=brand_name: self._render_inventory_models(b))
      card.configure(cursor="hand2")
      
      # Make all child labels clickable too
      for child in card.winfo_children():
        child.bind("<Button-1>", lambda e, b=brand_name: self._render_inventory_models(b))
        child.configure(cursor="hand2")

  def _render_inventory_models(self, brand_name):
    """Level 2: Show model/series cards for selected brand."""
    self._inv_level = 1
    self._inv_brand = brand_name
    self._inv_model = None
    if _has_customtkinter:
      self._inv_back_btn.pack(side="left")
      self._inv_breadcrumb.configure(text=f"{brand_name} -> Pilih Seri")
    
    # Clear content
    for w in self._inv_content.winfo_children():
      w.destroy()
    
    grouped = self._get_grouped_products()
    models = grouped.get(brand_name, {})
    if not models:
      ctk.CTkLabel(self._inv_content,
        text=f"Tidak ada produk untuk {brand_name}.",
        font=ctk.CTkFont(size=14), text_color=COLORS["text_light"]).pack(pady=40)
      return
    
    sorted_models = sorted(models.items(), key=lambda x: -sum(p.get("Stok", 0) for p in x[1]))
    
    if _has_customtkinter:
      brand_color = self.BRAND_COLORS.get(brand_name, COLORS["primary"])
      total_products = sum(len(prods) for _, prods in sorted_models)
      total_stock = sum(p.get("Stok", 0) for _, prods in sorted_models for p in prods)
      
      # Brand header card
      header = ctk.CTkFrame(self._inv_content, fg_color="white", corner_radius=12,
                 border_width=1, border_color="#e0e0e0")
      header.pack(fill="x", pady=(0, 12))
      
      avatar = ctk.CTkFrame(header, fg_color=brand_color, corner_radius=16, width=32, height=32)
      avatar.pack(side="left", padx=12, pady=10)
      avatar.pack_propagate(False)
      ctk.CTkLabel(avatar, text=self.BRAND_ICONS.get(brand_name, brand_name[:2]),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white").pack(expand=True)
      
      info_frame = ctk.CTkFrame(header, fg_color="transparent")
      info_frame.pack(side="left", fill="x", expand=True, pady=10)
      ctk.CTkLabel(info_frame, text=brand_name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]).pack(anchor="w")
      ctk.CTkLabel(info_frame,
        text=f"{len(sorted_models)} seri | {total_products} produk | {total_stock} unit stok",
        font=ctk.CTkFont(size=11),
        text_color=COLORS["text_light"]).pack(anchor="w")
      
      # Search/filter input
      filter_frame = ctk.CTkFrame(self._inv_content, fg_color="transparent")
      filter_frame.pack(fill="x", pady=(0, 8))
      
      search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Cari seri...", height=32)
      search_entry.pack(side="left", fill="x", expand=True)
      
      # Model cards grid
      grid = ctk.CTkFrame(self._inv_content, fg_color="transparent")
      grid.pack(fill="x")
      
      cols = 3
      for idx, (model_name, prods) in enumerate(sorted_models):
        row = idx // cols
        col = idx % cols
        
        stock = sum(p.get("Stok", 0) for p in prods)
        min_price = min(p.get("Harga Jual", 0) for p in prods)
        max_price = max(p.get("Harga Jual", 0) for p in prods)
        
        # Stock color indicator
        stock_color = COLORS["success"] if stock > 10 else COLORS["warning"] if stock > 3 else COLORS["danger"]
        
        card = ctk.CTkFrame(grid, fg_color="white", corner_radius=12,
                  border_width=1, border_color="#e0e0e0")
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        grid.grid_columnconfigure(col, weight=1)
        
        # Stock dot indicator
        dot = ctk.CTkFrame(card, fg_color=stock_color, corner_radius=4, width=8, height=8)
        dot.pack(anchor="ne", padx=8, pady=(8, 0))
        
        # Model name
        ctk.CTkLabel(card, text=model_name[:28],
              font=ctk.CTkFont(size=13, weight="bold"),
              text_color=COLORS["text"]).pack(pady=(10, 2), padx=8)
        
        # Size count
        ctk.CTkLabel(card,
          text=f"{len(prods)} ukuran",
          font=ctk.CTkFont(size=11),
          text_color=brand_color).pack()
        
        # Price range
        if min_price > 0:
          price_text = f"Rp {min_price:,}" if min_price == max_price else f"Rp {min_price:,} - Rp {max_price:,}"
          ctk.CTkLabel(card,
            text=price_text,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_light"]).pack(pady=2)
        
        # Stock badge
        ctk.CTkLabel(card,
          text=f"Stok: {stock}",
          font=ctk.CTkFont(size=10, weight="bold"),
          text_color=stock_color).pack(pady=(2, 10))
        
        card.bind("<Button-1>", lambda e, b=brand_name, m=model_name: self._render_inventory_products(b, m))
        card.configure(cursor="hand2")
        for child in card.winfo_children():
          child.bind("<Button-1>", lambda e, b=brand_name, m=model_name: self._render_inventory_products(b, m))
          child.configure(cursor="hand2")
      
      # Filter functionality
      def filter_models():
        query = search_entry.get().lower()
        for child in grid.winfo_children():
          if isinstance(child, ctk.CTkFrame):
            # Check if any label contains the query
            visible = False
            for label in child.winfo_children():
              if isinstance(label, ctk.CTkLabel):
                if query in label.cget("text").lower():
                  visible = True
                  break
            child.pack_forget() if not visible else None
            if visible:
              child.grid()
            else:
              child.grid_remove()
      
      search_entry.bind("<KeyRelease>", lambda e: filter_models())

  def _render_inventory_products(self, brand_name, model_name):
    """Level 3: Show product/size list with prices, stock and margins."""
    self._inv_level = 2
    self._inv_brand = brand_name
    self._inv_model = model_name
    if _has_customtkinter:
      self._inv_back_btn.pack(side="left")
      self._inv_breadcrumb.configure(text=f"{brand_name} -> {model_name[:22]} -> Ukuran")
    
    # Clear content
    for w in self._inv_content.winfo_children():
      w.destroy()
    
    grouped = self._get_grouped_products()
    products = grouped.get(brand_name, {}).get(model_name, [])
    if not products:
      ctk.CTkLabel(self._inv_content,
        text=f"Tidak ada produk untuk {brand_name} {model_name}.",
        font=ctk.CTkFont(size=14), text_color=COLORS["text_light"]).pack(pady=40)
      return
    
    # Sort by ring then size
    products.sort(key=lambda p: (int(p.get("Ring", 0) or 0), p.get("Ukuran", "")))
    
    if _has_customtkinter:
      brand_color = self.BRAND_COLORS.get(brand_name, COLORS["primary"])
      
      # Header
      header = ctk.CTkFrame(self._inv_content, fg_color="white", corner_radius=12,
                 border_width=1, border_color="#e0e0e0")
      header.pack(fill="x", pady=(0, 10))
      
      ctk.CTkLabel(header, text=f"{model_name} - {len(products)} ukuran",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]).pack(pady=(12, 2), padx=14)
      ctk.CTkLabel(header,
        text=brand_name,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=brand_color).pack(pady=(0, 12))
      
      # Column headers (pack order matches data row order below)
      col_header = ctk.CTkFrame(self._inv_content, fg_color="#f0f0f0", corner_radius=6, height=28)
      col_header.pack(fill="x", pady=(0, 2))
      
      labels_frame = ctk.CTkFrame(col_header, fg_color="transparent")
      labels_frame.pack(fill="x", padx=10, pady=4)
      
      ctk.CTkLabel(labels_frame, text="Ukuran", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="left", padx=(4, 30))
      ctk.CTkLabel(labels_frame, text="Ring", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="left", padx=10)
      ctk.CTkLabel(labels_frame, text="Kategori", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="left", padx=10)
      # Right-aligned columns: packed right-to-left, so reverse visual order
      ctk.CTkLabel(labels_frame, text="Modal", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="right", padx=4)
      ctk.CTkLabel(labels_frame, text="Margin", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="right", padx=4)
      ctk.CTkLabel(labels_frame, text="Harga Jual", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="right", padx=4)
      ctk.CTkLabel(labels_frame, text="Stok", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_light"]).pack(side="right", padx=4)
      
      # Product rows
      for prod in products:
        size = prod.get("Ukuran", "-")
        ring = prod.get("Ring", "-")
        price = prod.get("Harga Jual", 0)
        stock = prod.get("Stok", 0)
        category = prod.get("Kategori", "")
        cost = prod.get("Harga Beli", 0)
        profit = price - cost
        profit_pct = (profit / cost * 100) if cost > 0 else 0
        
        row = ctk.CTkFrame(self._inv_content, fg_color="white", corner_radius=6,
                 border_width=1, border_color="#f0f0f0")
        row.pack(fill="x", pady=1)
        
        # Hover effect
        def on_enter(e, r=row):
          r.configure(fg_color="#f8fff8")
        def on_leave(e, r=row):
          r.configure(fg_color="white")
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=6)
        
        # Size (largest element)
        size_badge = ctk.CTkFrame(inner, fg_color=brand_color + "15", corner_radius=4)
        size_badge.pack(side="left")
        ctk.CTkLabel(size_badge,
          text=f"R{ring} {size}",
          font=ctk.CTkFont(size=12, weight="bold"),
          text_color=brand_color).pack(padx=6, pady=2)
        
        # Category tag
        if category:
          cat_color = COLORS["primary"] if "Mobil" in category else COLORS["warning"]
          cat_label = ctk.CTkLabel(inner,
            text=category[:8],
            font=ctk.CTkFont(size=9),
            text_color=cat_color,
            fg_color=cat_color + "12",
            corner_radius=4,
            padx=4, pady=1)
          cat_label.pack(side="left", padx=8)
        
        # Cost
        ctk.CTkLabel(inner,
          text=f"Rp {cost:,}",
          font=ctk.CTkFont(size=11),
          text_color=COLORS["text_light"]).pack(side="right", padx=4)
        
        # Margin
        margin_color = COLORS["success"] if profit_pct > 25 else COLORS["warning"] if profit_pct > 15 else COLORS["danger"]
        ctk.CTkLabel(inner,
          text=f"{profit_pct:.0f}%",
          font=ctk.CTkFont(size=11, weight="bold"),
          text_color=margin_color).pack(side="right", padx=4)
        
        # Price
        ctk.CTkLabel(inner,
          text=f"Rp {price:,}",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color=COLORS["text"]).pack(side="right", padx=4)
        
        # Stock
        stock_color = COLORS["success"] if stock > 10 else COLORS["warning"] if stock > 3 else COLORS["danger"]
        stock_badge = ctk.CTkFrame(inner, fg_color=stock_color + "18", corner_radius=4)
        stock_badge.pack(side="right", padx=4)
        ctk.CTkLabel(stock_badge,
          text=str(stock),
          font=ctk.CTkFont(size=11, weight="bold"),
          text_color=stock_color).pack(padx=6, pady=1)
      
      # Summary footer
      total_stock = sum(p.get("Stok", 0) for p in products)
      total_value = sum(p.get("Harga Jual", 0) * p.get("Stok", 0) for p in products)
      total_cost = sum(p.get("Harga Beli", 0) * p.get("Stok", 0) for p in products)
      total_profit = total_value - total_cost
      
      summary_row = ctk.CTkFrame(self._inv_content, fg_color=COLORS["primary"] + "08",
                    corner_radius=8, border_width=1, border_color=COLORS["primary"] + "20")
      summary_row.pack(fill="x", pady=(8, 0))
      
      ctk.CTkLabel(summary_row,
        text=f"Total: {len(products)} ukuran | {total_stock} unit | "
           f"Nilai: Rp {total_value:,} | "
           f"Modal: Rp {total_cost:,} | "
           f"Potensi Untung: Rp {total_profit:,}",
        font=ctk.CTkFont(size=11),
        text_color=COLORS["text_light"]).pack(pady=8, padx=10)

  def _inv_go_back(self):
    """Navigate back one drill-down level."""
    if self._inv_level == 1:
      self._render_inventory_brands()
    elif self._inv_level == 2:
      self._render_inventory_models(self._inv_brand)

  def _add_sample_products(self):
    """Add sample products to inventory."""
    count = self.tools["inventory"].add_sample_data()
    self._show_success(f"{count} produk contoh berhasil ditambahkan!")
    self._show_frame("inventory") # Refresh

  def _show_low_stock(self):
    """Show low stock products in a popup."""
    low_stock = self.tools["inventory"].get_low_stock_products()
    if not low_stock:
      self._show_success("Semua stok aman!")
      return
    
    msg = "PRODUK STOK MENIPIS:\n\n"
    for p in low_stock:
      msg += f"• {p.get('Merek', '-')} {p.get('Ukuran', '-')}: Stok {p.get('Stok', 0)}\n"
    
    if _has_customtkinter:
      dialog = ctk.CTkInputDialog(text=msg, title="Stok Menipis")
      dialog.destroy()
    else:
      messagebox.showwarning("Stok Menipis", msg)

  def _export_inventory(self):
    """Export inventory to CSV."""
    filepath = filedialog.asksaveasfilename(
      defaultextension=".csv",
      filetypes=[("CSV files", "*.csv")]
    )
    if filepath:
      self.tools["inventory"].export_csv(filepath)
      self._show_success(f"Data di-export ke {filepath}")

  # ─── Price List ─────────────────────────────────────────────────────
  def _build_price_list(self):
    """Build Price List Generator interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Price List Generator",
              "Buat daftar harga PDF, promo flyer, dan teks untuk WhatsApp")

    # Products selection
    products = self.tools["inventory"].products
    if not products:
      self.tools["inventory"].add_sample_data()
      products = self.tools["inventory"].products

    # PDF Generator
    self._create_section_title(frame, "Generate Daftar Harga PDF")
    
    pdf_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkLabel(pdf_frame, 
            text="Buat daftar harga profesional format PDF untuk dicetak atau dishare.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_light"]).pack(anchor="w", pady=5)
      
      button_frame = ctk.CTkFrame(pdf_frame, fg_color="transparent")
      button_frame.pack(fill="x", pady=10)
      
      ctk.CTkButton(button_frame, text="Generate PDF Price List",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["primary"],
             command=lambda: self._generate_pdf(products)).pack(side="left", padx=5)
    else:
      tk.Label(pdf_frame, text="Buat daftar harga profesional format PDF.",
          font=("Arial", 10), bg="white", fg="#666").pack(anchor="w", pady=5)
      tk.Button(pdf_frame, text="Generate PDF Price List",
           command=lambda: self._generate_pdf(products),
           bg="#2E7D32", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    # Flyer Generator
    self._create_section_title(frame, "Generate Promo Flyer")
    
    flyer_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkLabel(flyer_frame, text="Buat gambar flyer promo untuk Instagram/WhatsApp.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_light"]).pack(anchor="w", pady=5)
      
      ctk.CTkButton(flyer_frame, text="Generate Promo Flyer",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["secondary"], text_color="black",
             command=self._generate_flyer).pack(pady=10)
    else:
      tk.Label(flyer_frame, text="Buat gambar flyer promo untuk Instagram/WhatsApp.",
          font=("Arial", 10), bg="white", fg="#666").pack(anchor="w", pady=5)
      tk.Button(flyer_frame, text="Generate Promo Flyer",
           command=self._generate_flyer,
           bg="#FFD700", fg="black", font=("Arial", 10, "bold")).pack(pady=10)

    # Text Price List
    self._create_section_title(frame, "Teks Daftar Harga (untuk WhatsApp)")
    
    text_frame = self._create_card(frame)
    
    if _has_customtkinter:
      text_preview = ctk.CTkTextbox(text_frame, height=200)
      text_preview.pack(fill="x", pady=5)
      price_text = self.tools["price_list"].generate_text(products[:10])
      text_preview.insert("1.0", price_text)
      text_preview.configure(state="disabled")
      
      ctk.CTkButton(text_frame, text="Copy ke Clipboard",
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["primary"],
             command=lambda: self._copy_text(price_text)).pack(pady=5)
    else:
      text_preview = tk.Text(text_frame, height=10)
      text_preview.pack(fill="x", pady=5)
      price_text = self.tools["price_list"].generate_text(products[:10])
      text_preview.insert("1.0", price_text)
      text_preview.configure(state="disabled")
      tk.Button(text_frame, text="Copy ke Clipboard",
           command=lambda: self._copy_text(price_text)).pack(pady=5)

  def _generate_pdf(self, products):
    """Generate PDF price list."""
    filepath = self.tools["price_list"].generate_pdf(products)
    if filepath:
      self._show_success(f"PDF tersimpan di:\n{filepath}")
      if messagebox.askyesno("Buka File", "Buka file PDF?"):
        os.startfile(filepath)
    else:
      self._show_error("Gagal generate PDF. Pastikan fpdf2 terinstall.")

  def _generate_flyer(self):
    """Generate promo flyer."""
    filepath = self.tools["price_list"].generate_flyer(
      "Diskon 20%\nSemua Ban Mobil!", 
      "Mulai Rp 350rb"
    )
    if filepath:
      self._show_success(f"Flyer tersimpan di:\n{filepath}")
      if messagebox.askyesno("Buka File", "Buka gambar flyer?"):
        os.startfile(filepath)
    else:
      self._show_error("Gagal generate flyer. Pastikan Pillow terinstall.")

  def _copy_text(self, text):
    """Copy text to clipboard."""
    self.root.clipboard_clear()
    self.root.clipboard_append(text)
    self._show_success("Teks di-copy ke clipboard!")

  # ─── Sales Chart ─────────────────────────────────────────────────────
  def _build_sales_chart(self):
    """Build Sales Dashboard interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Sales Dashboard & Analisis",
              "Visualisasikan penjualan, lihat produk terlaris, dan analisis keuntungan")

    # Check if we have data
    if not self.tools["dashboard"].sales_data:
      self.tools["dashboard"].add_sample_sales()
    
    stats = self.tools["dashboard"].get_stats()
    
    # Stats cards
    stats_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
           tk.Frame(frame, bg=COLORS["light_bg"])
    stats_frame.pack(fill="x", pady=(0, 20))
    
    stat_items = [
      ("Pendapatan", f"Rp {stats.get('total_revenue', 0):,.0f}", COLORS["success"]),
      ("Transaksi", str(stats.get('total_transactions', 0)), COLORS["primary"]),
      ("Rata-rata", f"Rp {stats.get('avg_transaction', 0):,.0f}", COLORS["warning"]),
    ]
    
    if _has_customtkinter:
      for i, (label, value, color) in enumerate(stat_items):
        card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
        card.grid(row=0, column=i, padx=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)
        
        ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
              text_color=COLORS["text_light"]).pack(pady=(10, 2))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"),
              text_color=color).pack(pady=(0, 10))

    # Generate charts buttons
    self._create_section_title(frame, "Generate Charts")
    
    charts_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkButton(charts_frame, text="Pendapatan Harian",
             font=ctk.CTkFont(size=13),
             fg_color=COLORS["primary"],
             command=self._chart_daily_revenue).pack(side="left", padx=5, pady=10)
      ctk.CTkButton(charts_frame, text="Produk Terlaris",
             font=ctk.CTkFont(size=13),
             fg_color=COLORS["success"],
             command=self._chart_top_products).pack(side="left", padx=5, pady=10)
      ctk.CTkButton(charts_frame, text="Margin Keuntungan",
             font=ctk.CTkFont(size=13),
             fg_color=COLORS["warning"], text_color="black",
             command=self._chart_profit_margin).pack(side="left", padx=5, pady=10)
    else:
      tk.Button(charts_frame, text="Pendapatan Harian",
           command=self._chart_daily_revenue,
           bg="#2E7D32", fg="white").pack(side="left", padx=5, pady=10)
      tk.Button(charts_frame, text="Produk Terlaris",
           command=self._chart_top_products,
           bg="#28A745", fg="white").pack(side="left", padx=5, pady=10)
      tk.Button(charts_frame, text="Margin Keuntungan",
           command=self._chart_profit_margin,
           bg="#FFC107", fg="black").pack(side="left", padx=5, pady=10)

    # Text report
    self._create_section_title(frame, "Laporan Teks")
    
    report_frame = self._create_card(frame)
    
    report_text = self.tools["dashboard"].generate_report()
    if _has_customtkinter:
      text_widget = ctk.CTkTextbox(report_frame, height=250)
      text_widget.pack(fill="x", pady=5)
      text_widget.insert("1.0", report_text)
      text_widget.configure(state="disabled")
    else:
      text_widget = tk.Text(report_frame, height=12)
      text_widget.pack(fill="x", pady=5)
      text_widget.insert("1.0", report_text)
      text_widget.configure(state="disabled")

  def _chart_daily_revenue(self):
    """Generate daily revenue chart."""
    filepath = self.tools["dashboard"].chart_daily_revenue()
    if filepath:
      self._show_success(f"Chart tersimpan di:\n{filepath}")
      if messagebox.askyesno("Buka File", "Buka gambar chart?"):
        os.startfile(filepath)
    else:
      self._show_error("Gagal generate chart. Pastikan matplotlib terinstall.")

  def _chart_top_products(self):
    """Generate top products chart."""
    filepath = self.tools["dashboard"].chart_top_products()
    if filepath:
      self._show_success(f"Chart tersimpan di:\n{filepath}")
      if messagebox.askyesno("Buka File", "Buka gambar chart?"):
        os.startfile(filepath)
    else:
      self._show_error("Gagal generate chart.")

  def _chart_profit_margin(self):
    """Generate profit margin chart."""
    filepath = self.tools["dashboard"].chart_profit_margin()
    if filepath:
      self._show_success(f"Chart tersimpan di:\n{filepath}")
    else:
      self._show_error("Gagal generate chart.")

  # ─── Social Media ────────────────────────────────────────────────────
  def _build_social(self):
    """Build Social Media Scheduler interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Social Media Content Scheduler",
              "Buat caption, jadwalkan postingan, dan kelola konten promosi")

    # Caption Generator
    self._create_section_title(frame, "✍️ Generator Caption")
    
    cap_frame = self._create_card(frame)
    
    if _has_customtkinter:
      templates = self.tools["social"].get_all_templates()
      template_names = list(templates.keys())
      
      ctk.CTkLabel(cap_frame, text="Pilih template caption:",
            font=ctk.CTkFont(size=13)).pack(anchor="w")
      
      cap_var = ctk.StringVar(value="promo_harga")
      cap_menu = ctk.CTkOptionMenu(cap_frame, values=template_names,
                    variable=cap_var, width=300)
      cap_menu.pack(anchor="w", pady=5)
      
      # Preview
      ctk.CTkLabel(cap_frame, text="Pratinjau Caption:",
            font=ctk.CTkFont(size=13)).pack(anchor="w")
      
      cap_preview = ctk.CTkTextbox(cap_frame, height=150)
      cap_preview.pack(fill="x", pady=5)
      
      def update_caption():
        caption = self.tools["social"].generate_caption(
          cap_var.get(),
          product="Ban Michelin",
          price=750000,
          size="185/65R14",
          tipe="Energy XM2+",
          car_type="Sedan"
        )
        cap_preview.delete("1.0", "end")
        cap_preview.insert("1.0", caption)
      
      ctk.CTkButton(cap_frame, text="✍️ Generate Caption",
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["primary"],
             command=update_caption).pack(pady=5)
      
      ctk.CTkButton(cap_frame, text="Copy Caption",
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["success"],
             command=lambda: self._copy_text(
               cap_preview.get("1.0", "end-1c"))).pack(pady=2)
    else:
      tk.Label(cap_frame, text="Pilih template caption:",
          font=("Arial", 10), bg="white").pack(anchor="w")
      tk.Label(cap_frame, text="(Gunakan customtkinter untuk UI lengkap)",
          font=("Arial", 9), bg="white", fg="#999").pack()

    # Content Plan
    self._create_section_title(frame, "Rencana Konten Mingguan")
    
    plan_frame = self._create_card(frame)
    
    if _has_customtkinter:
      plan = self.tools["social"].generate_content_plan(7)
      
      for day_plan in plan:
        day_frame = ctk.CTkFrame(plan_frame, fg_color="#f8f9fa", corner_radius=8)
        day_frame.pack(fill="x", pady=3)
        
        ctk.CTkLabel(day_frame, 
              text=f"{day_plan['day']} ({day_plan['date']})",
              font=ctk.CTkFont(size=12, weight="bold"),
              text_color=COLORS["primary"]).pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(day_frame,
              text=f"Template: {day_plan['template']}",
              font=ctk.CTkFont(size=11),
              text_color=COLORS["text_light"]).pack(anchor="w", padx=10, pady=(0, 5))
    else:
      tk.Label(plan_frame, text="(Install customtkinter untuk melihat rencana konten)",
          font=("Arial", 10), bg="#f8f9fa").pack(pady=20)

  # ─── Competitor Monitor ──────────────────────────────────────────────
  def _build_competitor(self):
    """Build Competitor Monitor interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Competitor Price Monitor",
              "Pantau harga kompetitor dan dapatkan alert perubahan harga")

    # Search
    self._create_section_title(frame, "🔎 Cek Harga Kompetitor")
    
    search_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkLabel(search_frame, text="Cari produk ban:",
            font=ctk.CTkFont(size=13)).pack(anchor="w")
      
      query_entry = ctk.CTkEntry(search_frame, placeholder_text="Contoh: Bridgestone 195/65R15",
                   width=400)
      query_entry.pack(anchor="w", pady=5)
      
      def search_competitors():
        query = query_entry.get()
        if not query:
          self._show_error("Masukkan nama produk!")
          return
        
        results = self.tools["competitor"].check_price_changes(query)
        
        # Show results
        result_text = ctk.CTkTextbox(search_frame, height=200)
        result_text.pack(fill="x", pady=10)
        
        result_text.insert("1.0", f"Hasil pencarian: {query}\n\n")
        for r in results:
          change = ""
          if r.get("price_change"):
            arrow = "🔺" if r.get("price_change", 0) > 0 else "🔻"
            change = f" {arrow} {abs(r.get('price_change', 0)):,.0f}"
          
          result_text.insert("end", 
            f"{r.get('source', '-')}\n"
            f"  Produk: {r.get('product', '-')}\n"
            f"  Harga: Rp {r.get('price', 0):,.0f}{change}\n\n"
          )
        result_text.configure(state="disabled")
      
      ctk.CTkButton(search_frame, text="Cari & Monitor",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["primary"],
             command=search_competitors).pack(pady=10)
    else:
      tk.Label(search_frame, text="Cari produk ban untuk memantau harga kompetitor.",
          font=("Arial", 10), bg="white", fg="#666").pack(pady=10)

    # Mock data info
    info_frame = self._create_card(frame)
    if _has_customtkinter:
      ctk.CTkLabel(info_frame, text="Untuk scraping live, install: pip install requests beautifulsoup4",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_light"]).pack(pady=10)
    else:
      tk.Label(info_frame, text="Install requests & beautifulsoup4 untuk scraping langsung.",
          font=("Arial", 10), bg="white", fg="#666").pack(pady=10)

  # ─── Orders ──────────────────────────────────────────────────────────
  def _build_orders(self):
    """Build Order Management interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Order Management System",
              "Kelola pesanan pelanggan dari awal sampai selesai")

    # Summary
    summary = self.tools["orders"].get_summary()
    
    summary_frame = ctk.CTkFrame(frame, fg_color="transparent") if _has_customtkinter else \
            tk.Frame(frame, bg=COLORS["light_bg"])
    summary_frame.pack(fill="x", pady=(0, 20))
    
    stats = [
      ("Total Pesanan", str(summary.get("total", 0))),
      ("Pending", str(summary.get("pending", 0))),
      ("Selesai", str(summary.get("completed", 0))),
      ("Belum Bayar", str(summary.get("unpaid", 0))),
    ]
    
    if _has_customtkinter:
      for i, (label, value) in enumerate(stats):
        card = ctk.CTkFrame(summary_frame, fg_color="white", corner_radius=10)
        card.grid(row=0, column=i, padx=5, sticky="nsew")
        summary_frame.grid_columnconfigure(i, weight=1)
        
        ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
              text_color=COLORS["text_light"]).pack(pady=(10, 2))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"),
              text_color=COLORS["primary"]).pack(pady=(0, 10))

    # Actions
    self._create_section_title(frame, "Aksi")
    
    actions_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkButton(actions_frame, text="Lihat Pesanan Pending",
             font=ctk.CTkFont(size=13),
             fg_color=COLORS["warning"], text_color="black",
             command=self._show_pending_orders).pack(side="left", padx=5, pady=10)
      ctk.CTkButton(actions_frame, text="➕ Tambah Sample Pesanan",
             font=ctk.CTkFont(size=13),
             fg_color=COLORS["success"],
             command=self._add_sample_orders).pack(side="left", padx=5, pady=10)
    else:
      tk.Button(actions_frame, text="Lihat Pesanan Pending",
           command=self._show_pending_orders,
           bg="#FFC107", fg="black").pack(side="left", padx=5)
      tk.Button(actions_frame, text="➕ Tambah Sample Pesanan",
           command=self._add_sample_orders,
           bg="#28A745", fg="white").pack(side="left", padx=5)

    # Order list
    self._create_section_title(frame, "Daftar Pesanan")
    
    if self.tools["orders"].orders:
      list_frame = self._create_card(frame)
      if _has_customtkinter:
        text = ctk.CTkTextbox(list_frame, height=250)
        text.pack(fill="x", pady=5)
        for o in self.tools["orders"].orders[:10]:
          text.insert("end", 
            f"{o.get('ID', '-')} | {o.get('Pelanggan', '-')}\n"
            f"  {o.get('Produk', '-')} x{o.get('Jumlah', 0)}\n"
            f"  Rp {o.get('Total', 0):,.0f} | Status: {o.get('Status', '-')}\n\n"
          )
        text.configure(state="disabled")
    else:
      empty_frame = self._create_card(frame)
      if _has_customtkinter:
        ctk.CTkLabel(empty_frame, text="Belum ada pesanan. Klik 'Tambah Sample Pesanan'.",
              font=ctk.CTkFont(size=14), text_color=COLORS["text_light"]).pack(pady=20)

  def _show_pending_orders(self):
    """Show pending orders in a popup."""
    pending = self.tools["orders"].get_pending_orders()
    if not pending:
      self._show_success("Tidak ada pesanan pending!")
      return
    
    msg = "PESANAN PENDING:\n\n"
    for p in pending:
      msg += f"• {p.get('ID', '-')}: {p.get('Pelanggan', '-')} - {p.get('Status', '-')}\n"
    
    if _has_customtkinter:
      dialog = ctk.CTkInputDialog(text=msg, title="Pesanan Pending")
      dialog.destroy()
    else:
      messagebox.showinfo("Pesanan Pending", msg)

  def _add_sample_orders(self):
    """Add sample orders."""
    self.tools["orders"].add_sample_orders()
    self._show_success("15 sample pesanan ditambahkan!")
    self._show_frame("orders")

  # ─── Loyalty ─────────────────────────────────────────────────────────
  def _build_loyalty(self):
    """Build Loyalty Program interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Customer Loyalty Program",
              "Program poin, tier membership, dan reward pelanggan")

    # Initialize sample data
    if not self.tools["loyalty"].customers:
      self.tools["loyalty"].add_sample_customers()

    # Tiers
    self._create_section_title(frame, "Level Membership")
    
    tiers_frame = self._create_card(frame)
    
    if _has_customtkinter:
      tiers_grid = ctk.CTkFrame(tiers_frame, fg_color="transparent")
      tiers_grid.pack(fill="x")
      
      for i, tier in enumerate(self.tools["loyalty"].get_all_tiers()):
        tier_card = ctk.CTkFrame(tiers_grid, fg_color="white", corner_radius=10,
                    border_width=1, border_color="#e0e0e0")
        tier_card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        tiers_grid.grid_columnconfigure(i, weight=1)
        
        ctk.CTkLabel(tier_card, text=f"👑 {tier['name']}",
              font=ctk.CTkFont(size=14, weight="bold"),
              text_color=tier['color']).pack(pady=(10, 2))
        ctk.CTkLabel(tier_card, text=f"Min {tier['min_points']} poin",
              font=ctk.CTkFont(size=11),
              text_color=COLORS["text_light"]).pack()
        for benefit in tier['benefits'][:2]:
          ctk.CTkLabel(tier_card, text=f"✓ {benefit}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_light"]).pack(pady=1)
        ctk.CTkLabel(tier_card, text="", height=10).pack()
    else:
      tk.Label(tiers_frame, text="Level: Reguler, Silver, Gold, Platinum",
          font=("Arial", 10), bg="white").pack(pady=10)

    # Customer list
    self._create_section_title(frame, "Daftar Pelanggan")
    
    cust_frame = self._create_card(frame)
    
    if _has_customtkinter:
      text = ctk.CTkTextbox(cust_frame, height=200)
      text.pack(fill="x", pady=5)
      
      text.insert("1.0", f"{'Nama':<20} {'Poin':<8} {'Tier':<12} {'Total':<15}\n")
      text.insert("1.0", "━" * 60 + "\n")
      
      for c in self.tools["loyalty"].customers:
        text.insert("end",
          f"{c.get('Nama', '-'):<20} {c.get('Total Poin', 0):<8} "
          f"{c.get('Tier', 'Reguler'):<12} "
          f"Rp {c.get('Total Belanja', 0):<,.0f}\n"
        )
      text.configure(state="disabled")
    else:
      tk.Label(cust_frame, text="Data pelanggan tersimpan di Excel.",
          font=("Arial", 10), bg="white", fg="#666").pack(pady=10)

  # ─── Sheets ─────────────────────────────────────────────────────────
  def _build_sheets(self):
    """Build Excel Automation interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "Excel & Google Sheets Automation",
              "Generate laporan otomatis, merge data, export ke Excel")

    # Reports
    self._create_section_title(frame, "Generate Laporan")
    
    reports_frame = self._create_card(frame)
    
    if _has_customtkinter:
      ctk.CTkLabel(reports_frame, text="Buat laporan Excel profesional dengan chart otomatis.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_light"]).pack(anchor="w", pady=5)
      
      # Generate sales report
      def make_sales_report():
        sales_data = self.tools["dashboard"].sales_data
        if not sales_data:
          self.tools["dashboard"].add_sample_sales()
          sales_data = self.tools["dashboard"].sales_data
        
        filepath = self.tools["sheets"].create_sales_report(sales_data)
        if filepath:
          self._show_success(f"Laporan tersimpan di:\n{filepath}")
          if messagebox.askyesno("Buka File", "Buka file Excel?"):
            os.startfile(filepath)
        else:
          self._show_error("Gagal generate. Install: pip install openpyxl pandas")
      
      ctk.CTkButton(reports_frame, text="Generate Laporan Penjualan Excel",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["primary"],
             command=make_sales_report).pack(pady=10)
      
      # Generate catalog
      def make_catalog():
        products = self.tools["inventory"].products
        if not products:
          self.tools["inventory"].add_sample_data()
          products = self.tools["inventory"].products
        
        filepath = self.tools["sheets"].create_catalog_excel(products)
        if filepath:
          self._show_success(f"Katalog tersimpan di:\n{filepath}")
      
      ctk.CTkButton(reports_frame, text="📗 Generate Katalog Ban Excel",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["success"],
             command=make_catalog).pack(pady=10)
    else:
      tk.Label(reports_frame, text="Install openpyxl & pandas untuk fitur Excel.",
          font=("Arial", 10), bg="white", fg="#666").pack(pady=20)

    # Daily summary
    self._create_section_title(frame, "Ringkasan Harian")
    
    daily_frame = self._create_card(frame)
    
    if _has_customtkinter:
      inv_summary = self.tools["inventory"].get_summary()
      orders_summary = self.tools["orders"].get_summary()
      
      daily_text = self.tools["sheets"].daily_summary_text(
        self.tools["dashboard"].sales_data,
        inv_summary,
        orders_summary
      )
      
      text_widget = ctk.CTkTextbox(daily_frame, height=250)
      text_widget.pack(fill="x", pady=5)
      text_widget.insert("1.0", daily_text)
      text_widget.configure(state="disabled")
      
      ctk.CTkButton(daily_frame, text="Copy Laporan",
             font=ctk.CTkFont(size=12),
             fg_color=COLORS["primary"],
             command=lambda: self._copy_text(daily_text)).pack(pady=5)

  # ─── QR Catalog ──────────────────────────────────────────────────────
  def _build_qr_catalog(self):
    """Build QR Code Catalog interface."""
    frame = self._create_scrollable_frame()

    self._create_header(frame, "QR Code Catalog",
              "Buat katalog ban digital yang bisa di-scan pelanggan dari HP mereka!")

    # Info
    info_frame = self._create_card(frame)
    if _has_customtkinter:
      ctk.CTkLabel(info_frame, text="Cara kerjanya:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["primary"]).pack(anchor="w")
      
      steps = [
        "1. Generate katalog HTML dengan semua produk & harga",
        "2. Generate QR code yang mengarah ke katalog",
        "3. Cetak QR code dan tempel di toko",
        "4. Pelanggan scan QR → langsung lihat katalog di HP!",
        "5. Bisa juga buat sticker QR untuk produk individual",
      ]
      for step in steps:
        ctk.CTkLabel(info_frame, text=step,
              font=ctk.CTkFont(size=12),
              text_color=COLORS["text"]).pack(anchor="w", pady=2)
    else:
      tk.Label(info_frame, text="Buat katalog digital yang bisa di-scan pelanggan.",
          font=("Arial", 10), bg="white").pack(pady=10)

    # Actions
    self._create_section_title(frame, "Generate")
    
    actions_frame = self._create_card(frame)
    
    if _has_customtkinter:
      def gen_catalog():
        products = self.tools["inventory"].products
        if not products:
          self.tools["inventory"].add_sample_data()
          products = self.tools["inventory"].products
        
        filepath = self.tools["qr_catalog"].save_catalog(products)
        if filepath:
          self._show_success(f"Katalog HTML tersimpan!\n{filepath}")
          if messagebox.askyesno("Buka", "Buka file HTML?"):
            webbrowser.open(f"file://{filepath}")
      
      def gen_qr():
        products = self.tools["inventory"].products
        if not products:
          self.tools["inventory"].add_sample_data()
          products = self.tools["inventory"].products
        
        # First save catalog
        html_path = self.tools["qr_catalog"].save_catalog(products)
        if html_path:
          qr_path = self.tools["qr_catalog"].generate_qr(
            f"file://{html_path}",
            label=BUSINESS_NAME
          )
          if qr_path:
            self._show_success(f"QR Code tersimpan!\n{qr_path}")
            if messagebox.askyesno("Buka", "Buka QR code?"):
              os.startfile(qr_path)
      
      ctk.CTkButton(actions_frame, text="Generate Katalog HTML",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["primary"],
             command=gen_catalog).pack(side="left", padx=5, pady=10)
      
      ctk.CTkButton(actions_frame, text="Generate QR Code Katalog",
             font=ctk.CTkFont(size=13, weight="bold"),
             fg_color=COLORS["success"],
             command=gen_qr).pack(side="left", padx=5, pady=10)

  # ═══════════════════════════════════════════════════════════════════
  # AI COMMAND CENTER — Multi-Agent Visualization
  # ═══════════════════════════════════════════════════════════════════

  def _build_ai(self):
    """Build AI Command Center with visual multi-agent system."""
    try:
      self._build_ai_impl()
    except Exception as e:
      frame = self._create_scrollable_frame()
      label = ctk.CTkLabel(frame, 
        text=f"AI Command Center\n\nGagal memuat UI.\nError: {e}",
        font=ctk.CTkFont(size=14),
        text_color=COLORS["text"],
        justify="left")
      label.pack(pady=40, padx=20)
      import traceback
      traceback.print_exc()

  def _build_ai_impl(self):
    """Build AI Command Center with visual multi-agent system."""
    if not _has_customtkinter:
      frame = self._create_scrollable_frame()
      tk.Label(frame, text="AI Command Center — Multi-Agent System",
          font=("Arial", 20, "bold"),
          bg=COLORS["light_bg"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 20))
      tk.Label(frame, text="Ketik perintah di bawah, AI akan menjalankannya!",
          font=("Arial", 10),
          bg=COLORS["light_bg"], fg=COLORS["text_light"]).pack(anchor="w")
      tk.Label(frame, text="\nContoh:\n• 'cek stok'\n• 'buat daftar harga'\n• 'kirim promo ke 08123456789'\n• 'bantuan'\n\n(Install customtkinter untuk UI multi-agent visual)",
          font=("Arial", 10), bg=COLORS["light_bg"], fg="#666",
          justify="left").pack(anchor="w", pady=10)
      return

    # Main vertical layout: [Agent Cards] [Chat] [Input]
    frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
    frame.pack(fill="both", expand=True)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1) # Chat area expands
    frame.grid_rowconfigure(2, weight=0) # Input fixed

    # ── 1. AGENT CARDS PANEL ──────────────────────────────────────────
    self.agent_cards_frame = ctk.CTkFrame(frame, fg_color="transparent", height=100)
    self.agent_cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    self.agent_cards_frame.grid_columnconfigure(0, weight=1)
    self.agent_cards_frame.grid_propagate(False)

    self._build_agent_cards_panel()

    # ── 2. CHAT CONTAINER ─────────────────────────────────────────────
    chat_frame = ctk.CTkFrame(frame, fg_color="white", corner_radius=12,
                 border_width=1, border_color="#e0e0e0")
    chat_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
    chat_frame.grid_columnconfigure(0, weight=1)
    chat_frame.grid_rowconfigure(1, weight=1)

    # Header with avatar
    header_frame = ctk.CTkFrame(chat_frame, fg_color=COLORS["primary"], corner_radius=0)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=22)
          ).grid(row=0, column=0, padx=(18, 5), pady=10)

    self.ai_header_title = ctk.CTkLabel(
      header_frame, text="AI Command Center",
      font=ctk.CTkFont(size=16, weight="bold"),
      text_color="white"
    )
    self.ai_header_title.grid(row=0, column=1, padx=2, pady=5, sticky="w")
    
    self.groq_status_label = ctk.CTkLabel(
      header_frame, text=self._get_groq_status_text(),
      font=ctk.CTkFont(size=9),
      text_color=self._get_groq_status_color()
    )
    self.groq_status_label.grid(row=0, column=1, padx=2, pady=(22, 2), sticky="w")

    # Header buttons
    settings_ai_btn = ctk.CTkButton(header_frame, text="", width=36, height=36,
                    fg_color=COLORS["primary_light"],
                    hover_color="#66BB6A",
                    font=ctk.CTkFont(size=16),
                    command=self._open_api_settings)
    settings_ai_btn.grid(row=0, column=2, padx=(0, 4))
    
    clear_btn = ctk.CTkButton(header_frame, text="🗑", width=36, height=36,
                 fg_color=COLORS["primary_light"],
                 hover_color="#66BB6A",
                 font=ctk.CTkFont(size=16),
                 command=self._clear_chat)
    clear_btn.grid(row=0, column=3, padx=(0, 10))

    # Chat messages area
    chat_bg = ctk.CTkFrame(chat_frame, fg_color="#e8f0e8", corner_radius=0)
    chat_bg.grid(row=1, column=0, sticky="nsew")
    chat_bg.grid_columnconfigure(0, weight=1)
    chat_bg.grid_rowconfigure(0, weight=1)

    self.chat_messages = ctk.CTkScrollableFrame(
      chat_bg, fg_color="#e8f0e8",
      scrollbar_button_color=COLORS["primary_light"],
      scrollbar_button_hover_color=COLORS["primary"]
    )
    self.chat_messages.grid(row=0, column=0, sticky="nsew")
    self.chat_messages.grid_columnconfigure(0, weight=1)

    # Welcome message from Supervisor agent
    self._add_chat_message(
      "ai",
      "Halo! Saya **Mixmoi** 🐱. Saya akan pilih agent terbaik untuk tugas Anda!\n\n"
      "Coba ketik perintah berikut:\n\n"
      " \"cek stok\" → **Inventory Agent**\n"
      " \"promo random 3\" → **Marketing Agent**\n"
      "💬 \"balas harga ban?\" → **💬 Chat Agent**\n"
      " \"status\" → **Sales Agent**\n"
      " \"daftar pelanggan\" → **Loyalty Agent**\n"
      " \"pesanan pending\" → **Orders Agent**\n"
      " \"cek kompetitor\" → **Monitor Agent**",
      timestamp="Sekarang",
      agent_id="supervisor"
    )

    # ── 3. INPUT AREA ─────────────────────────────────────────────────
    input_frame = ctk.CTkFrame(frame, fg_color="transparent")
    input_frame.grid(row=2, column=0, sticky="ew")
    input_frame.grid_columnconfigure(0, weight=1)

    # Active agent chip (shows which agent is active)
    self.active_agent_chip_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
    self.active_agent_chip_frame.pack(fill="x", pady=(0, 6))
    
    self.active_agent_chip = ctk.CTkLabel(
      self.active_agent_chip_frame,
      text="Mixmoi 🐱 siap membantu...",
      font=ctk.CTkFont(size=11),
      text_color=COLORS["text_light"],
      fg_color="#f0f0f0",
      corner_radius=12,
      padx=12,
      pady=4
    )
    self.active_agent_chip.pack(side="left")

    # Input row
    input_row = ctk.CTkFrame(input_frame, fg_color="transparent")
    input_row.pack(fill="x")
    input_row.grid_columnconfigure(0, weight=1)

    input_bg = ctk.CTkFrame(input_row, fg_color="white", corner_radius=25,
                border_width=1, border_color="#d0d0d0")
    input_bg.grid(row=0, column=0, sticky="ew", padx=(0, 10))
    input_bg.grid_columnconfigure(0, weight=1)

    self.ai_input = ctk.CTkEntry(input_bg, placeholder_text="Ketik perintah untuk agent...",
                   font=ctk.CTkFont(size=13),
                   height=40, fg_color="transparent",
                   border_width=0)
    self.ai_input.grid(row=0, column=0, sticky="ew", padx=(15, 5), pady=2)

    def send_ai_command():
      command = self.ai_input.get().strip()
      if not command:
        return
      self.ai_input.delete(0, "end")
      self._execute_and_display(command)

    def send_on_enter(event):
      send_ai_command()
      return "break"

    self.ai_input.bind("<Return>", send_on_enter)
    self.ai_input.focus_set()

    send_btn = ctk.CTkButton(input_row, text="➤",
                 font=ctk.CTkFont(size=18),
                 fg_color=COLORS["primary"],
                 hover_color=COLORS["primary_light"],
                 command=send_ai_command,
                 width=45, height=45,
                 corner_radius=25)
    send_btn.grid(row=0, column=1)

    # ── Quick action chips ──
    quick_frame = ctk.CTkFrame(frame, fg_color="transparent")
    quick_frame.grid(row=3, column=0, sticky="ew", pady=(0, 0))

    quick_actions = [
      ("Cek Stok", "cek stok"),
      ("Random 3", "promo random 3"),
      ("Promo Gold", "promo gold"),
      ("Status", "status"),
      ("Tips Ban", "tips ban"),
      ("💬 Balas Halo", "balas halo ada promo?"),
      ("Pelanggan", "daftar pelanggan"),
    ]

    for label, cmd in quick_actions:
      btn = ctk.CTkButton(quick_frame, text=label,
                font=ctk.CTkFont(size=10),
                fg_color="#e8f0e8",
                text_color=COLORS["dark"],
                hover_color="#c8e6c9",
                command=lambda c=cmd: self._ai_quick_command(c),
                height=28,
                corner_radius=14,
                border_width=0)
      btn.pack(side="left", padx=2)

  # ─── AGENT CARDS PANEL ──────────────────────────────────────────────
  def _build_agent_cards_panel(self):
    """Build the visual agent cards panel at the top of AI view."""
    # Clear existing
    for w in self.agent_cards_frame.winfo_children():
      w.destroy()

    # Scrollable frame for cards
    cards_scroll = ctk.CTkScrollableFrame(
      self.agent_cards_frame,
      fg_color="transparent",
      orientation="horizontal",
      height=95,
      scrollbar_button_color=COLORS["primary_light"],
      scrollbar_button_hover_color=COLORS["primary"]
    )
    cards_scroll.pack(fill="x", expand=True)

    self.agent_card_widgets = {}

    for agent in AGENT_DEFINITIONS:
      # Agent card frame
      card = ctk.CTkFrame(
        cards_scroll,
        fg_color="white",
        corner_radius=12,
        border_width=2,
        border_color="#e0e0e0",
        width=100,
        height=82
      )
      card.pack(side="left", padx=4)
      card.pack_propagate(False)

      # Icon
      icon_label = ctk.CTkLabel(
        card,
        text=agent["icon"],
        font=ctk.CTkFont(size=24)
      )
      icon_label.pack(pady=(6, 0))

      # Name
      name_label = ctk.CTkLabel(
        card,
        text=agent["name"],
        font=ctk.CTkFont(size=9, weight="bold"),
        text_color=COLORS["text"]
      )
      name_label.pack(pady=(1, 0))

      # Status dot
      status_frame = ctk.CTkFrame(card, fg_color="transparent")
      status_frame.pack(pady=(2, 4))
      
      status_dot = ctk.CTkLabel(
        status_frame,
        text="○",
        font=ctk.CTkFont(size=8),
        text_color="#cccccc"
      )
      status_dot.pack(side="left")
      
      status_text = ctk.CTkLabel(
        status_frame,
        text="idle",
        font=ctk.CTkFont(size=7),
        text_color="#cccccc"
      )
      status_text.pack(side="left", padx=(2, 0))

      self.agent_card_widgets[agent["id"]] = {
        "frame": card,
        "icon": icon_label,
        "name": name_label,
        "dot": status_dot,
        "status": status_text
      }

  def _add_chat_message(self, sender: str, message: str, timestamp: str = "",
              agent_id: str = ""):
    """Add a styled chat bubble to the messages area with agent visualization."""
    is_user = sender == "user"
    now = datetime.now().strftime("%H:%M")
    ts = timestamp if timestamp else now

    # Determine agent info
    if not agent_id and not is_user:
      agent_id = "supervisor"
    agent_info = AGENTS_BY_ID.get(agent_id, AGENTS_BY_ID["supervisor"]) if agent_id else None
    agent_color = agent_info["color"] if agent_info else COLORS["primary"]
    agent_icon = agent_info["icon"] if agent_info else ""
    agent_name = agent_info["name"] if agent_info else "AI"

    # Container
    bubble_container = ctk.CTkFrame(self.chat_messages, fg_color="transparent")
    bubble_container.pack(fill="x", pady=(4, 0), padx=10)
    bubble_container.grid_columnconfigure(0, weight=1)

    # ── Agent header (only for AI messages) ──
    if not is_user and agent_info:
      label_frame = ctk.CTkFrame(bubble_container, fg_color="transparent")
      label_frame.pack(anchor="w", pady=(6, 0))
      
      # Agent icon + name in agent's color
      agent_label = ctk.CTkLabel(
        label_frame,
        text=f"{agent_info['icon']} {agent_info['name']}",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=agent_color
      )
      agent_label.pack(side="left")
      
      # Small capability badge
      cap_label = ctk.CTkLabel(
        label_frame,
        text=f" {agent_info['desc'][:30]}..." if len(agent_info['desc']) > 30 else f" {agent_info['desc']}",
        font=ctk.CTkFont(size=8),
        text_color="#999"
      )
      cap_label.pack(side="left", padx=(4, 0))

    # ── Bubble frame ──
    if is_user:
      bubble_frame = ctk.CTkFrame(
        bubble_container,
        fg_color="#dcf8c6",
        corner_radius=18,
      )
      bubble_frame.pack(anchor="e", pady=2, padx=(40, 0))
    else:
      # AI bubble: left-aligned with subtle agent color border
      bubble_frame = ctk.CTkFrame(
        bubble_container,
        fg_color="white",
        corner_radius=18,
        border_width=1,
        border_color=agent_color
      )
      bubble_frame.pack(anchor="w", pady=2, padx=(0, 40))

    # ── Message content ──
    msg_label = ctk.CTkLabel(
      bubble_frame,
      text=message,
      font=ctk.CTkFont(size=12),
      text_color=COLORS["text"],
      wraplength=450,
      justify="left"
    )
    msg_label.pack(padx=14, pady=(10, 4))

    # ── Timestamp ──
    if is_user:
      status_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
      status_frame.pack(anchor="e", padx=(10, 12), pady=(0, 6))
      ctk.CTkLabel(status_frame, text=f"✓ {ts}",
            font=ctk.CTkFont(size=9),
            text_color="#888").pack(side="right")

    if not is_user:
      ts_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
      ts_frame.pack(anchor="e", padx=10, pady=(0, 6))
      ctk.CTkLabel(ts_frame, text=f" {ts}",
            font=ctk.CTkFont(size=9),
            text_color="#bbb").pack(side="left")

    # Auto-scroll
    try:
      self.chat_messages._parent_canvas.yview_moveto(1.0)
    except Exception:
      pass

  def _show_typing_indicator(self, agent_id: str = ""):
    """Show typing indicator while AI processes, with agent branding."""
    agent_info = AGENTS_BY_ID.get(agent_id, AGENTS_BY_ID["supervisor"]) if agent_id else AGENTS_BY_ID["supervisor"]
    
    typing_frame = ctk.CTkFrame(self.chat_messages, fg_color="transparent")
    typing_frame.pack(fill="x", pady=(4, 0), padx=10)

    # Agent header
    label_frame = ctk.CTkFrame(typing_frame, fg_color="transparent")
    label_frame.pack(anchor="w", pady=(6, 0))
    
    ctk.CTkLabel(
      label_frame,
      text=f"{agent_info['icon']} {agent_info['name']}",
      font=ctk.CTkFont(size=11, weight="bold"),
      text_color=agent_info["color"]
    ).pack(side="left")

    bubble = ctk.CTkFrame(
      typing_frame,
      fg_color="white",
      corner_radius=18,
      border_width=1,
      border_color=agent_info["color"]
    )
    bubble.pack(anchor="w", pady=2, padx=(0, 40))

    # Animated dots
    dots_label = ctk.CTkLabel(
      bubble,
      text=f"{agent_info['icon']} {agent_info['name']} sedang memproses...",
      font=ctk.CTkFont(size=11),
      text_color="#888"
    )
    dots_label.pack(padx=16, pady=10)

    # Auto-scroll
    try:
      self.chat_messages._parent_canvas.yview_moveto(1.0)
    except Exception:
      pass
    
    typing_frame.agent_id = agent_id
    return typing_frame

  def _clear_chat(self):
    """Clear all chat messages and reset agent states."""
    for widget in self.chat_messages.winfo_children():
      widget.destroy()
    self._deactivate_all_agents()
    self._add_chat_message(
      "ai",
      "🧹 Chat dibersihkan! Semua agent siap membantu lagi.",
      timestamp="Sekarang",
      agent_id="supervisor"
    )
    # Update agent chip
    self._update_active_agent_chip("supervisor", is_thinking=False)

  def _execute_and_display(self, command: str):
    """Execute AI command and show result with visual delegation chain animation."""
    # Add user message bubble
    try:
      self._add_chat_message("user", command)
    except Exception:
      pass

    # Predict which agent handles this for pre-visualization
    import tools.ai_command_center as acc
    predicted_agent = acc.determine_agent(command)
    
    # ── ANIMATE SUPERVISOR THINKING ──
    self._activate_agent_card("supervisor")
    self._update_active_agent_chip("supervisor", is_thinking=True)
    
    # Show Supervisor typing indicator first
    typing_indicator = None
    try:
      typing_indicator = self._show_typing_indicator("supervisor")
      self.root.update_idletasks()
    except Exception:
      pass

    # Process command - get delegation chain
    agent_id = predicted_agent
    sub_agents = []
    delegation_chain = []
    try:
      result = self.tools["ai"].process_command(command)
      response = result["result"]
      agent_id = result.get("agent_id", predicted_agent)
      sub_agents = result.get("sub_agents", [])
      delegation_chain = result.get("delegation_chain", [])
    except Exception as e:
      response = f"Terjadi kesalahan: {str(e)}"

    # Remove typing indicator
    if typing_indicator:
      try:
        typing_indicator.destroy()
      except Exception:
        pass

    # ── ANIMATE DELEGATION CHAIN ──
    # If multiple agents were involved, show them one by one
    if len(sub_agents) > 1:
      # Animate each agent in the chain with a delay
      def animate_chain():
        for i, sub_id in enumerate(sub_agents):
          self._activate_agent_card(sub_id)
          self._update_active_agent_chip(sub_id, is_thinking=True)
          try:
            self.root.update_idletasks()
          except Exception:
            pass
        
        # Final: show last agent as done + Supervisor back
        if sub_agents:
          self._activate_agent_card(sub_agents[-1])
          self._update_active_agent_chip(sub_agents[-1], is_thinking=False)
      
      # Run animation after a tiny delay
      self.root.after(50, animate_chain)
    else:
      # Single agent - just activate it
      self._activate_agent_card(agent_id)
      self._update_active_agent_chip(agent_id, is_thinking=False)

    # Update header title to show agents involved
    if len(sub_agents) > 1:
      agent_icons = [AGENTS_BY_ID.get(a, {}).get("icon", "?") for a in sub_agents]
      chain_text = " → ".join(agent_icons)
      try:
        self.ai_header_title.configure(
          text=f"{chain_text}",
          text_color="white"
        )
      except Exception:
        pass
    else:
      agent_info = AGENTS_BY_ID.get(agent_id, AGENTS_BY_ID["supervisor"])
      try:
        self.ai_header_title.configure(
          text=f"{agent_info['icon']} {agent_info['name']}",
          text_color="white"
        )
      except Exception:
        pass

    # Add AI response bubble with agent info
    try:
      # If multiple agents, show delegation in the bubble header
      if len(sub_agents) > 1:
        # Add Supervisor's delegation message
        self._add_chat_message("ai", response, agent_id="supervisor")
      else:
        self._add_chat_message("ai", response, agent_id=agent_id)
    except Exception:
      pass

  def _ai_quick_command(self, command: str):
    """Execute a quick AI command."""
    self.ai_input.delete(0, "end")
    self._execute_and_display(command)

  # ─── AGENT VISUALIZATION HELPERS ────────────────────────────────────
  def _activate_agent_card(self, agent_id: str):
    """Highlight an agent card to show it's active."""
    # Deactivate all first
    self._deactivate_all_agents()
    
    widget_group = self.agent_card_widgets.get(agent_id)
    if not widget_group:
      return
    
    agent_info = AGENTS_BY_ID.get(agent_id, AGENTS_BY_ID["supervisor"])
    
    # Animate the card
    widget_group["frame"].configure(
      border_color=agent_info["color"],
      fg_color=agent_info["bg_color"]
    )
    widget_group["dot"].configure(
      text="●",
      text_color=agent_info["color"]
    )
    widget_group["status"].configure(
      text="active",
      text_color=agent_info["color"]
    )
    widget_group["icon"].configure(text=agent_info["icon"])

  def _deactivate_all_agents(self):
    """Reset all agent cards to idle state."""
    for aid, widget_group in self.agent_card_widgets.items():
      agent_info = AGENTS_BY_ID.get(aid, {})
      try:
        widget_group["frame"].configure(
          border_color="#e0e0e0",
          fg_color="white"
        )
        widget_group["dot"].configure(
          text="○",
          text_color="#cccccc"
        )
        widget_group["status"].configure(
          text="idle",
          text_color="#cccccc"
        )
      except Exception:
        pass

  def _update_active_agent_chip(self, agent_id: str, is_thinking: bool = False):
    """Update the active agent chip below the input area."""
    agent_info = AGENTS_BY_ID.get(agent_id, AGENTS_BY_ID["supervisor"])
    try:
      if is_thinking:
        self.active_agent_chip.configure(
          text=f"⏳ {agent_info['icon']} {agent_info['name']} sedang bekerja...",
          text_color=agent_info["color"],
          fg_color=agent_info["bg_color"]
        )
      else:
        self.active_agent_chip.configure(
          text=f"{agent_info['icon']} {agent_info['name']} selesai",
          text_color=agent_info["color"],
          fg_color=agent_info["bg_color"]
        )
        # Auto-reset after 3 seconds
        self.root.after(3000, lambda: self.active_agent_chip.configure(
          text="Mixmoi 🐱 siap membantu...",
          text_color=COLORS["text_light"],
          fg_color="#f0f0f0"
        ))
    except Exception:
      pass

  # ─── Helper Methods ──────────────────────────────────────────────────
  def _create_scrollable_frame(self) -> object:
    """Create a scrollable frame for content."""
    if _has_customtkinter:
      frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
      frame.pack(fill="both", expand=True)
      return frame
    else:
      canvas = tk.Canvas(self.content_container, bg=COLORS["light_bg"])
      scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=canvas.yview)
      scrollable_frame = tk.Frame(canvas, bg=COLORS["light_bg"])
      
      scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
      )
      
      canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
      canvas.configure(yscrollcommand=scrollbar.set)
      
      canvas.pack(side="left", fill="both", expand=True)
      scrollbar.pack(side="right", fill="y")
      
      return scrollable_frame

  def _create_header(self, parent, title: str, subtitle: str = ""):
    """Create a header section."""
    if _has_customtkinter:
      header = ctk.CTkFrame(parent, fg_color="transparent")
      header.pack(fill="x", pady=(0, 20))
      
      ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["primary"]).pack(anchor="w")
      if subtitle:
        ctk.CTkLabel(header, text=subtitle, font=ctk.CTkFont(size=12),
              text_color=COLORS["text_light"]).pack(anchor="w")
    else:
      tk.Label(parent, text=title, font=("Arial", 16, "bold"),
          bg=COLORS["light_bg"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 5))
      if subtitle:
        tk.Label(parent, text=subtitle, font=("Arial", 9),
            bg=COLORS["light_bg"], fg=COLORS["text_light"]).pack(anchor="w", pady=(0, 15))

  def _create_section_title(self, parent, title: str):
    """Create a section title."""
    if _has_customtkinter:
      ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["primary"]).pack(anchor="w", pady=(15, 10))
    else:
      tk.Label(parent, text=title, font=("Arial", 12, "bold"),
          bg=COLORS["light_bg"], fg=COLORS["primary"]).pack(anchor="w", pady=(10, 5))

  def _create_card(self, parent) -> object:
    """Create a card frame."""
    if _has_customtkinter:
      card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                border_width=1, border_color="#e0e0e0")
      card.pack(fill="x", pady=5, padx=2)
      card.pack_configure(pady=5)
      return card
    else:
      card = tk.LabelFrame(parent, text="", bg="white", padx=10, pady=10)
      card.pack(fill="x", pady=5, padx=2)
      return card

  def _show_success(self, message: str):
    """Show success message."""
    if _has_customtkinter:
      messagebox.showinfo("Sukses", message)
    else:
      messagebox.showinfo("Sukses", message)

  def _show_error(self, message: str):
    """Show error message."""
    if _has_customtkinter:
      messagebox.showerror("Error", message)
    else:
      messagebox.showerror("Error", message)

    # ─── Groq Status Helpers ──────────────────────────────────────────
  def _get_groq_status_text(self) -> str:
    """Get status text for Groq connection."""
    groq_api_key = os.environ.get("GROQ_API_KEY", "")
    if self.tools["ai"].groq_configured:
      return "Connected • Groq AI"
    elif groq_api_key:
      return "Key set • Not connected"
    else:
      return "No API Key • Click to set"

  def _get_groq_status_color(self) -> str:
    """Get color for Groq status label."""
    if self.tools["ai"].groq_configured:
      return "#aaddaa"
    elif os.environ.get("GROQ_API_KEY", ""):
      return "#ffdd44"
    else:
      return "#ff8888"

  def _update_groq_status(self):
    """Update all Groq status indicators in the UI."""
    # Update sidebar indicator dot
    if hasattr(self, 'groq_status_indicator'):
      if self.tools["ai"].groq_configured:
        self.groq_status_indicator.configure(text_color="#44dd44", text="●")
      elif os.environ.get("GROQ_API_KEY", ""):
        self.groq_status_indicator.configure(text_color="#ffdd44", text="●")
      else:
        self.groq_status_indicator.configure(text_color="#888888", text="●")

    # Update AI header label if visible
    if hasattr(self, 'groq_status_label'):
      try:
        self.groq_status_label.configure(
          text=self._get_groq_status_text(),
          text_color=self._get_groq_status_color()
        )
      except Exception:
        pass

  # ─── API Settings Dialog ────────────────────────────────────────────
  def _open_api_settings(self):
    """Open a beautiful settings popup to enter your Groq API key."""
    if not _has_customtkinter:
      self._show_error("Settings dialog requires customtkinter.")
      return

    # Create popup window
    popup = ctk.CTkToplevel(self.root)
    popup.title("API Settings - Groq AI")
    popup.geometry("500x420")
    popup.resizable(False, False)
    popup.transient(self.root)
    popup.grab_set()

    # Center on parent
    popup.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2
    y = self.root.winfo_y() + (self.root.winfo_height() - 420) // 2
    popup.geometry(f"+{x}+{y}")

    # ── Main frame with padding ──
    main = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
    main.pack(fill="both", expand=True, padx=0, pady=0)

    # ── Header ──
    header = ctk.CTkFrame(main, fg_color=COLORS["primary"], corner_radius=0, height=80)
    header.pack(fill="x")
    header.pack_propagate(False)

    ctk.CTkLabel(header, text="Groq AI Settings",
          font=ctk.CTkFont(size=20, weight="bold"),
          text_color="white").pack(pady=(15, 2))
    ctk.CTkLabel(header, text="Connect your app to Groq AI",
          font=ctk.CTkFont(size=11),
          text_color="#aaddaa").pack()

    # ── Body with scroll ──
    body = ctk.CTkScrollableFrame(main, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=25, pady=(15, 10))

    # ── Connection Status Card ──
    status_card = ctk.CTkFrame(body, fg_color="#f0f8f0", corner_radius=10,
                  border_width=1, border_color="#d0e0d0")
    status_card.pack(fill="x", pady=(0, 15))

    status_inner = ctk.CTkFrame(status_card, fg_color="transparent")
    status_inner.pack(fill="x", padx=15, pady=12)

    ctk.CTkLabel(status_inner, text="📡 Connection Status",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color=COLORS["primary"]).pack(anchor="w")

    # Check current status
    has_key = bool(os.environ.get("GROQ_API_KEY", ""))
    is_connected = self.tools["ai"].groq_configured

    if is_connected:
      status_icon = "Connected"
      status_text = "Connected! Groq AI is active."
      status_color = COLORS["success"]
    elif has_key:
      status_icon = "Key found"
      status_text = "API key found but Groq not initialized."
      status_color = COLORS["warning"]
    else:
      status_icon = "No API Key"
      status_text = "No API key set. Groq AI is disabled."
      status_color = "#d32f2f"

    status_label = ctk.CTkLabel(status_inner, text=f"{status_icon} {status_text}",
                  font=ctk.CTkFont(size=12),
                  text_color=status_color)
    status_label.pack(anchor="w", pady=(5, 0))

    # ── Groq API Key Input ──
    ctk.CTkLabel(body, text="🔐 Your Groq API Key (wajib untuk AI)",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color=COLORS["text"]).pack(anchor="w")

    ctk.CTkLabel(body, text="Get your free key at console.groq.com → API Keys",
          font=ctk.CTkFont(size=11),
          text_color=COLORS["text_light"]).pack(anchor="w", pady=(2, 8))

    current_key = os.environ.get("GROQ_API_KEY", "")
    api_entry = ctk.CTkEntry(
      body,
      placeholder_text="Paste your gsk_... API key here",
      font=ctk.CTkFont(size=13, family="Consolas"),
      height=42,
      corner_radius=8,
      border_width=2,
      border_color="#d0d0d0"
    )
    api_entry.pack(fill="x")
    if current_key and len(current_key) > 10:
      api_entry.insert(0, current_key)

    # ── Serper API Key Input ──
    ctk.CTkLabel(body, text="🔍 Your Serper API Key (untuk riset perusahaan)",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color=COLORS["text"]).pack(anchor="w", pady=(15, 0))

    ctk.CTkLabel(body, text="Get your free key at serper.dev → API Keys",
          font=ctk.CTkFont(size=11),
          text_color=COLORS["text_light"]).pack(anchor="w", pady=(2, 8))

    current_serper = os.environ.get("SERPER_API_KEY", "")
    serper_entry = ctk.CTkEntry(
      body,
      placeholder_text="Paste your Serper API key here",
      font=ctk.CTkFont(size=13, family="Consolas"),
      height=42,
      corner_radius=8,
      border_width=2,
      border_color="#d0d0d0"
    )
    serper_entry.pack(fill="x")
    if current_serper and len(current_serper) > 10:
      serper_entry.insert(0, current_serper)

    # ── Quick Links ──
    link_frame = ctk.CTkFrame(body, fg_color="transparent")
    link_frame.pack(fill="x", pady=(12, 5))

    def open_groq_console():
      webbrowser.open("https://console.groq.com/keys")

    ctk.CTkButton(link_frame, text="🌐 Get Groq API Key",
           font=ctk.CTkFont(size=11),
           fg_color="#f0f0f0", text_color=COLORS["primary"],
           hover_color="#e0e0e0",
           command=open_groq_console,
           height=30, corner_radius=8).pack(side="left", padx=(0, 5))

    def open_serper_console():
      webbrowser.open("https://serper.dev")

    ctk.CTkButton(link_frame, text="🔍 Get Serper API Key",
           font=ctk.CTkFont(size=11),
           fg_color="#f0f0f0", text_color=COLORS["primary"],
           hover_color="#e0e0e0",
           command=open_serper_console,
           height=30, corner_radius=8).pack(side="left")

    # ── Action Buttons ──
    btn_frame = ctk.CTkFrame(body, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(15, 0))

    # Save status label
    save_status = ctk.CTkLabel(btn_frame, text="",
                  font=ctk.CTkFont(size=12),
                  text_color=COLORS["success"])
    save_status.pack(pady=(0, 8))

    def save_api_key():
      """Save API keys to .env and reload Groq client."""
      groq_key = api_entry.get().strip()
      serper_key = serper_entry.get().strip()

      if not groq_key:
        save_status.configure(text="Please enter a Groq API key!", text_color=COLORS["danger"])
        return

      try:
        env_path = BASE_DIR / ".env"
        env_lines = []
        groq_found = False
        serper_found = False
        if env_path.exists():
          with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
              if line.startswith("GROQ_API_KEY="):
                env_lines.append(f"GROQ_API_KEY={groq_key}\n")
                groq_found = True
              elif line.startswith("SERPER_API_KEY="):
                if serper_key:
                  env_lines.append(f"SERPER_API_KEY={serper_key}\n")
                  serper_found = True
                else:
                  env_lines.append(line)
              else:
                env_lines.append(line)
        if not groq_found:
          env_lines.append(f"\nGROQ_API_KEY={groq_key}\n")
        if serper_key and not serper_found:
          env_lines.append(f"SERPER_API_KEY={serper_key}\n")
        with open(env_path, "w", encoding="utf-8") as f:
          f.writelines(env_lines)

        os.environ["GROQ_API_KEY"] = groq_key
        if serper_key:
          os.environ["SERPER_API_KEY"] = serper_key
        load_dotenv(dotenv_path=str(env_path), override=True)

        success = self.tools["ai"].set_groq_api_key(groq_key)
        self._update_groq_status()

        if success:
          save_status.configure(text="Keys saved & Groq AI is ACTIVE!",
                     text_color=COLORS["success"])
          status_label.configure(
            text="Connected! Groq AI is active.",
            text_color=COLORS["success"]
          )
        else:
          save_status.configure(text="Groq key saved but init failed. Check your key.",
                     text_color=COLORS["warning"])
          status_label.configure(
            text="Key saved but connection failed.",
            text_color=COLORS["warning"]
          )

        popup.after(3000, lambda: popup.destroy())

      except Exception as e:
        save_status.configure(text=f"Error saving: {str(e)}",
                   text_color=COLORS["danger"])

    def test_connection():
      """Test the Groq API connection."""
      key = api_entry.get().strip()
      if not key:
        save_status.configure(text="Enter a key first!", text_color=COLORS["danger"])
        return

      try:
        from groq import Groq
        c = Groq(api_key=key)
        c.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=[{"role": "user", "content": "say ok"}],
          max_tokens=5
        )
        save_status.configure(text="Connection successful! Key is valid. Now click Save.",
                   text_color=COLORS["success"])
      except Exception as e:
        save_status.configure(text=f"Connection failed: {str(e)[:60]}...",
                   text_color=COLORS["danger"])

    button_row = ctk.CTkFrame(btn_frame, fg_color="transparent")
    button_row.pack(fill="x")

    ctk.CTkButton(button_row, text="🧪 Test Connection",
           font=ctk.CTkFont(size=12),
           fg_color="#f0f0f0", text_color=COLORS["text"],
           hover_color="#e0e0e0",
           command=test_connection,
           height=38, corner_radius=8).pack(side="left", padx=(0, 8))

    ctk.CTkButton(button_row, text="💾 Save & Activate",
           font=ctk.CTkFont(size=13, weight="bold"),
           fg_color=COLORS["primary"], text_color="white",
           hover_color=COLORS["primary_light"],
           command=save_api_key,
           height=38, corner_radius=8).pack(side="right")

    # ── Footer info ──
    ctk.CTkLabel(body, text="Your API key is stored locally in the .env file. Never shared.",
          font=ctk.CTkFont(size=10),
          text_color=COLORS["text_light"]).pack(pady=(15, 5))

  # ─── Run ─────────────────────────────────────────────────────────────
  def run(self):
    """Start the application."""
    # Update Groq UI status on startup
    self.root.after(100, self._update_groq_status)
    self.root.mainloop()


# ─── Entry Point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
  import sys
  import io
  # Fix Windows console encoding for emoji support
  if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
  
  print(f"[*] Starting {BUSINESS_NAME} Management System v{APP_VERSION}")
  print(f"[*] Project directory: {BASE_DIR}")
  print()
  
  if not _has_customtkinter:
    print("customtkinter tidak terinstall.")
    print("  Menggunakan tampilan dasar tkinter.")
    print("  Install dengan: pip install customtkinter")
    print()
  
  app = TokoBanApp()
  app.run()
