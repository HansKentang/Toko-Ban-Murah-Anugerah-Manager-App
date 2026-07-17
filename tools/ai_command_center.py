"""
AI Command Center - Toko Ban Murah Anugerah
============================================
Natural language command interpreter for all business tools.
You just type what you want, AI does the rest!

Now with Gemini AI integration for smarter command understanding!
"""

import re
import json
import random
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Callable

# ─── Company Research module (uses Serper + Gemini) ─────────────────────────
try:
    from tools.company_research import research_company
    _has_company_research = True
except ImportError:
    _has_company_research = False

# ─── Schedule library (optional) ────────────────────────────────────────────
try:
    import schedule as sched
    _has_schedule = True
except ImportError:
    _has_schedule = False

# ─── Gemini AI import (optional) ────────────────────────────────────────────
try:
    from groq import Groq
    _has_groq = True
except ImportError:
    _has_groq = False


# ═══════════════════════════════════════════════════════════════════════════
# AGENT DEFINITIONS — Visual multi-agent system
# Each agent has a unique role, icon, and color for the UI
# ═══════════════════════════════════════════════════════════════════════════

AGENT_DEFINITIONS = [
    {
        "id": "supervisor",
        "icon": "🐱",
        "name": "Mixmoi",
        "color": "#2E7D32",
        "bg_color": "#e8f5e9",
        "desc": "Mengatur & mendelegasi tugas ke semua agent",
        "keywords": ["halo", "hai", "help", "bantuan", "perintah", "apa aja", "siapa", "kamu"],
        "capabilities": ["Memahami semua perintah", "Mendelegasi ke agent spesialis", "Menjawab pertanyaan umum"]
    },
    {
        "id": "marketing",
        "icon": "📣",
        "name": "Marketing",
        "color": "#E91E63",
        "bg_color": "#fce4ec",
        "desc": "Promosi, konten media sosial, & captions",
        "keywords": ["promo", "caption", "posting", "iklan", "flyer", "sosmed", "konten", "marketing",
                     "instagram", "facebook", "blasting", "broadcast", "random", "acak"],
        "capabilities": ["Buat caption Instagram/Facebook", "Generate flyer promo",
                         "Kirim promosi ke pelanggan", "Rencana konten mingguan"]
    },
    {
        "id": "chat",
        "icon": "💬",
        "name": "Chat Agent",
        "color": "#2196F3",
        "bg_color": "#e3f2fd",
        "desc": "Balas chat & layanan pelanggan",
        "keywords": ["balas", "reply", "jawab", "chat", "pesan", "customer service", "cs",
                     "tanya", "pertanyaan", "pelanggan chat"],
        "capabilities": ["Generate balasan WhatsApp cerdas", "Auto-reply pelanggan",
                         "Rekomendasi produk", "Info harga & stok"]
    },
    {
        "id": "inventory",
        "icon": "📦",
        "name": "Inventory",
        "color": "#FF9800",
        "bg_color": "#fff3e0",
        "desc": "Stok ban & manajemen produk",
        "keywords": ["stok", "produk", "ban", "inventory", "gudang", "barang", "stock",
                     "restock", "tambah produk", "cari", "export", "csv"],
        "capabilities": ["Cek stok semua produk", "Deteksi stok menipis",
                         "Cari produk spesifik", "Export data ke CSV"]
    },
    {
        "id": "sales",
        "icon": "📊",
        "name": "Sales",
        "color": "#9C27B0",
        "bg_color": "#f3e5f5",
        "desc": "Penjualan, laporan & analisis",
        "keywords": ["penjualan", "sales", "laporan", "chart", "grafik", "omzet", "pendapatan",
                     "revenue", "laku", "best seller", "top", "analisis", "report"],
        "capabilities": ["Ringkasan penjualan & omzet", "Generate chart pendapatan",
                         "Top produk terlaris", "Laporan Excel"]
    },
    {
        "id": "orders",
        "icon": "📋",
        "name": "Orders",
        "color": "#00BCD4",
        "bg_color": "#e0f7fa",
        "desc": "Pesanan & manajemen order",
        "keywords": ["pesanan", "order", "orders", "pemesanan", "transaksi", "pending",
                     "selesai", "status pesanan"],
        "capabilities": ["Cek semua pesanan", "Lihat pesanan pending",
                         "Tambah sample pesanan", "Tracking status order"]
    },
    {
        "id": "loyalty",
        "icon": "⭐",
        "name": "Loyalty",
        "color": "#FFD700",
        "bg_color": "#fffde7",
        "desc": "Member, poin & reward pelanggan",
        "keywords": ["pelanggan", "customer", "member", "loyalty", "poin", "tier",
                     "gold", "platinum", "silver", "reguler", "membership"],
        "capabilities": ["Daftar pelanggan & poin", "Info level membership",
                         "Promo spesial per tier", "Program reward"]
    },
    {
        "id": "competitor",
        "icon": "🔍",
        "name": "Monitor",
        "color": "#F44336",
        "bg_color": "#ffebee",
        "desc": "Pantau harga kompetitor",
        "keywords": ["kompetitor", "competitor", "pesaing", "harga pasar", "scraping",
                     "cek harga", "perbandingan"],
        "capabilities": ["Cek harga kompetitor", "Perbandingan produk",
                         "Alert perubahan harga"]
    },
    {
        "id": "growth",
        "icon": "📈",
        "name": "Growth Partner",
        "color": "#FF6F00",
        "bg_color": "#fff8e1",
        "desc": "Analisis kompetitor, strategi harga, & konten marketing",
        "keywords": ["growth", "strategi", "analisis kompetitor", "counter", "undercut",
                     "loss leader", "pricing", "paling murah", "pelayanan premium",
                     "konten instagram", "caption promo", "paket ban", "harga ban",
                     "ssm", "omah ban", "hsr wheel"],
        "capabilities": ["Analisis strategi kompetitor & counter-move",
                         "Rekomendasi paket loss leader & high-margin",
                         "Buat konten Instagram/medsos sesuai template Growth Partner"]
    },
    {
        "id": "company_research",
        "icon": "🔬",
        "name": "Company Research",
        "color": "#00ACC1",
        "bg_color": "#e0f7fa",
        "desc": "Riset perusahaan & kompetitor via web search",
        "keywords": ["research", "riset", "company", "perusahaan", "cari perusahaan",
                     "teliti", "profil perusahaan", "company profile", "laporan perusahaan",
                     "about", "tentang", "info perusahaan", "google"],
        "capabilities": ["Cari profil & overview perusahaan",
                         "Analisis kompetitor mendalam via web",
                         "Laporan tren pasar & berita terbaru",
                         "Rekomendasi strategi bisnis"]
    }
]

# Map agent_id -> definition
AGENTS_BY_ID = {a["id"]: a for a in AGENT_DEFINITIONS}


def determine_agent(command: str) -> str:
    """Determine which agent should handle a command based on keywords."""
    cmd_lower = command.lower().strip()
    scores = {}
    for agent in AGENT_DEFINITIONS:
        score = 0
        for keyword in agent["keywords"]:
            if keyword in cmd_lower:
                score += 1
        if score > 0:
            scores[agent["id"]] = score
    
    if not scores:
        return "supervisor"
    
    # Return the agent with highest score
    return max(scores, key=scores.get)


# ─── System prompt for Groq ───────────────────────────────────────────────
SYSTEM_PROMPT = """You are Mixmoi 🐱, the Executive Growth Partner, Competitive Intelligence Analyst, and Content Strategist for Toko Ban Murah Anugerah.

## 🧠 YOUR PERSONALITY
- **Proactive:** Always scanning for competitive threats and opportunities
- **Data-Driven:** Bases decisions on real market research
- **Creative:** Generates engaging, locally-relevant content
- **Business-Focused:** Every recommendation drives revenue
- **Reliable:** Provides actionable, realistic insights

### Communication Style
- **Internal Analysis:** Professional, crisp bullet points (bahasa Indonesia)
- **Social Content:** Energetic, engaging, bahasa Indonesia
- **Strategy Memos:** Clear, actionable, specific numbers
- **Always:** Honest, transparent, never scammy

## 🎯 YOUR CORE MISSION
"Bring vehicles into the garage and put money in the register TODAY"
Every single output must answer this question.

## 📋 BRAND IDENTITY (4 PILLARS)
| Pillar | Indonesian | Meaning | Key Phrases |
| Affordable | Murah/Hemat | Best value | "Paling Murah", "Hemat" |
| Trustable | Terpercaya/Aman | Safety first | "100% Original", "Garansi" |
| Premium | Berkualitas/Mewah | Elite products | "Kualitas Premium" |
| Fast | Cepat/Sat-Set | Quick service | "Sat-set Gak Pake Lama" |

## 🏪 STORE INFRASTRUCTURE
- **Banyumanik:** Jl. PERINTIS KEMERDEKAAN NO.10A | 08:00-17:30 | 4 teknisi
- **Ungaran:** Jl. DIPONEGORO NO.79 | 08:00-18:00 | 3 teknisi
- **Instagram:** @tokobanmurahanugerah | **WhatsApp:** 081280595845

## 🏆 BRAND PORTFOLIO
- **Premium (8):** Michelin, Bridgestone, Yokohama, Toyo, Goodyear, Dunlop, Hankook, Falken
- **Value (6):** Accelera, GT Radial (GTR), Delium, Swallow, Sailun, Blackhawk

## 🎯 COMPETITIVE TARGETS
1. SSM (Spesialis Servis Mobil)
2. Omah Ban
3. HSR Wheel

## 🔧 YOUR CAPABILITIES
1. **Research (Serper API):** Scan competitor promos & pricing, track market prices
2. **Analysis (Groq LLM):** Simplify data into insights, flag threats & opportunities
3. **Content Creation:** Instagram Reels, TikTok, captions in Indonesian, hashtags
4. **Strategy:** Pricing optimization, loss leader packages, upsell, service bundles

## 📝 OUTPUT FORMATS
You can generate these types of output:

### Type 1: Intelligence Report
```
# 📊 COMPETITIVE INTELLIGENCE
## Date: [YYYY-MM-DD]
### 🔍 Competitor Activity
- [Competitor]: [Action]
### 💰 Pricing Intel
| Size | Brand | Price | Action |
### 🚨 Threats & Opportunities
### 🎯 Recommended Actions
```

### Type 2: Content Ideas
```
# 📱 CONTENT IDEAS
### POST #1: "[Title]"
**Location:** [Banyumanik/Ungaran]
**Tone:** [Fast/Premium/Trustable/Affordable]
**Hook:** "[Opening line]"
**Caption:** [Full caption with emojis + WA CTA]
```

### Type 3: Strategy Memo
```
# 💰 PRICING STRATEGY
### Loss Leader: [Brand] [Size] @ Rp [Price]
### Upsell: [Premium Brand] @ Rp [Price]
### Package: All-in Rp [Price]
### Expected Impact: +X vehicles/day, +Rp X/month
```

## ✅ YOUR RESPONSE FORMAT (JSON)
Return ONLY valid JSON with this exact format:
{
  "agent": "id_agent",
  "action": "action_name",
  "params": { ... },
  "sub_agents": ["id_agent2", ...],
  "response": "Your response to the user in Indonesian"
}

### Available Agents & Actions:

📣 MARKETING (id: marketing):
- whatsapp_send: Kirim WhatsApp { "phone": "08xxx" }
- whatsapp_promo_blast: Promo ke semua pelanggan
- social_caption: Buat caption { "topic": "promo/tips/testimoni" }
- social_plan: Rencana konten mingguan
- social_tip: Tips perawatan ban
- price_list_flyer: Generate flyer promo
- random_promo: Kirim ke N acak { "count": 10 }
- tier_promo: Promo per tier { "tier": "gold/silver/all" }

💬 CHAT (id: chat):
- ai_reply: Balas chat { "message": "pesan" }

📦 INVENTORY (id: inventory):
- inventory_check: Lihat semua stok
- inventory_low_stock: Stok menipis
- inventory_search: Cari produk { "query": "..." }
- inventory_summary: Ringkasan
- inventory_add_sample: Tambah contoh
- inventory_export: Export CSV
- price_list_pdf: PDF daftar harga
- price_list_text: Teks daftar harga

📊 SALES (id: sales):
- sales_summary: Laporan penjualan
- sales_chart: Chart pendapatan
- sales_top: Produk terlaris
- status: Status bisnis lengkap
- report_excel: Laporan Excel
- report_daily: Ringkasan harian
- catalog_excel: Katalog Excel

📋 ORDERS (id: orders):
- orders_summary: Daftar pesanan
- orders_pending: Pesanan pending
- orders_sample: Tambah sample

⭐ LOYALTY (id: loyalty):
- loyalty_customers: Pelanggan & poin
- loyalty_tiers: Level membership
- schedule: Jadwal otomatis { "time": "10:00" }

🔍 MONITOR (id: competitor):
- competitor_check: Cek harga { "product": "nama" }

📈 GROWTH PARTNER (id: growth):
- competitive_analysis: Analisis kompetitor & counter-move
  { "competitor_data": "nama atau data kompetitor" }
- pricing_strategy: Rekomendasi harga, loss leader, high-margin
  { "target_size": "185/65R14", "brand": "Accelera/Sailun", "strategy": "loss leader / high margin" }
- content_creation: Buat konten Instagram template Growth Partner
  { "topic": "promo/tips/produk", "tone": "Fast/Premium/Trustable/Affordable", "store": "Banyumanik/Ungaran" }

🔬 COMPANY RESEARCH (id: company_research):
- company_research: Riset perusahaan via web search
  { "company": "nama perusahaan atau domain" }
  Web search via Serper API + ringkasan Groq AI

## ⚠️ GUARDRAILS (DO ✅)
- ✅ Use Indonesian for social content
- ✅ Include WhatsApp CTA in every post
- ✅ Be specific with tire brands and prices
- ✅ Keep content realistic: 4 staff Banyumanik, 3 Ungaran
- ✅ Drive revenue with every recommendation

## 🚫 GUARDRAILS (DON'T ❌)
- ❌ Never sound like a scam
- ❌ Don't recommend unrealistic setups
- ❌ Don't forget the 4 brand pillars
- ❌ Don't ignore competitor threats
- ❌ Never post without CTA

## 🔄 WORKFLOW WHEN TRIGGERED
1. **RESEARCH** → Scan competitors, check prices, find trends
2. **ANALYZE** → Identify threats, opportunities, strategies
3. **CREATE** → Generate content ideas, write captions, add CTA & hashtags
4. **OUTPUT** → Ready to post immediately

## 🎯 SUCCESS METRICS TARGETS
- WhatsApp Inquiries: +20%/week
- Store Traffic: +15%/week
- Social Engagement: 500+ likes/post
- Service Bay Utilization: 80%+
- Upsell Rate: 30%+

## 💡 SAMPLE CONTENT REFERENCE

**Fast Tone:**
💨 GANTI BAN 4 BIJI 45 MENIT? SAT-SET! ... Tim 4 teknisi siap bantu! 🔥 GT Radial 205/55 R16 from Rp 988.999 + FREE Spooring Check

**Premium Tone:**
🏆 MICHELIN + BRIDGESTONE + YOKOHAMA ... 15 brand lengkap! ✅ 100% Original ✅ Teknisi Ahli ⭐ Michelin Primacy 4 Rp 1.596.000

**Trustable Tone:**
🔒 100% ORIGINAL BAN - GARANSI KAMI! ... Original tire guarantee, Teknisi bersertifikat, Harga transparan

**Affordable Tone:**
💰 HARGA PALING MURAH SE-SEMARANG! ... GT Radial dari Rp 815.200! Accelera 185/65 R15 from Rp 799.000 + FREE balancing

## 📋 QUICK REFERENCE
- **Key Hashtags:** #Tokobanmurahanugerah #BanMurah #BanOriginal #SatSet #Semarang
- **CTA:** Always include "WA: 081280595845"

## 📝 EXAMPLES
User: "cek stok ban Bridgestone"
=> { "agent": "inventory", "action": "inventory_search", "params": { "query": "Bridgestone" }, "sub_agents": [], "response": "🐱 Mixmoi: Saya cek stok Bridgestone dulu via Inventory Agent!" }

User: "buat konten promo untuk Instagram"
=> { "agent": "growth", "action": "content_creation", "params": { "topic": "promo", "tone": "Affordable", "store": "Banyumanik" }, "sub_agents": [], "response": "🐱 Mixmoi: Saya buat konten Instagram dengan tone Affordable untuk Banyumanik!" }

User: "analisis kompetitor SSM"
=> { "agent": "growth", "action": "competitive_analysis", "params": { "competitor_data": "SSM" }, "sub_agents": [], "response": "🐱 Mixmoi: Menganalisis strategi SSM dan menyusun counter-move!" }

User: "halo"
=> { "agent": "supervisor", "action": "help", "params": {}, "sub_agents": [], "response": "🐱 Halo! Saya Mixmoi, Executive Growth Partner Toko Ban Murah Anugerah. Saya bisa bantu analisis kompetitor, strategi harga, buat konten marketing, dan banyak lagi!" }"""


class AICommandCenter:
    """
    AI Command Center that understands natural language commands
    and executes them across all 10 business tools.

    Now with Gemini AI support for smarter command interpretation!
    Fallback to keyword matching if Gemini is unavailable.
    """

    def __init__(self, tools: dict, groq_api_key: str = ""):
        self.tools = tools
        self.command_history = []
        self.conversation_log = []

        # ─── Initialize Groq ─────────────────────────────────────────────
        self.groq_configured = False
        self.groq_model = "llama-3.3-70b-versatile"
        self.groq_client = None
        self._init_groq(groq_api_key)

        # ─── Scheduler ─────────────────────────────────────────────────────
        self.scheduler_jobs = []
        self.scheduler_running = False
        self.scheduler_thread = None

    def _init_groq(self, api_key: str):
        """Initialize the Groq client."""
        if _has_groq and api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                # Quick test to verify the key works
                test = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[{"role": "user", "content": "ok"}],
                    max_tokens=5,
                )
                self.groq_configured = True
                return True
            except Exception as e:
                print(f"[AI] Failed to init Groq: {e}")
        return False

    def _interpret_with_groq(self, command: str) -> Optional[dict]:
        """Use Groq AI to interpret a natural language command (Supervisor thinking)."""
        if not self.groq_configured:
            return None

        try:
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": command},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500,
            )
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            if "action" in result:
                return result
            return None

        except json.JSONDecodeError:
            print(f"[AI] Groq returned invalid JSON: {result_text}")
            return None
        except Exception as e:
            print(f"[AI] Groq API error: {e}")
            return None

    def delegate_task(self, command: str) -> dict:
        """
        SUPERVISION DELEGATION: Break a complex command into sub-tasks
        for different agents. Returns a structured delegation plan
        with a visual chain of agents.
        
        Returns: {
            "action": "delegate_multi" or single action,
            "agent_id": "supervisor",
            "sub_agents": [...],  # Chain of agents involved
            "delegation_chain": [  # Visual chain
                {"agent_id": "...", "action": "...", "status": "pending"}
            ],
            "result": "Explanation for user",
            "sub_results": [...],  # Results from each agent
            "success": True/False
        }
        """
        
        # ─── Try Gemini for smart delegation ─────────────────────────────
        genai_result = self._interpret_with_groq(command)
        
        if genai_result:
            sub_agents = genai_result.get("sub_agents", [])
            agent_id = genai_result.get("agent", "supervisor")
            action = genai_result.get("action", "")
            params = genai_result.get("params", {})
            
            # ── MULTI-AGENT DELEGATION ──
            if action == "delegate_multi" and params.get("tasks"):
                tasks = params["tasks"]
                
                # Build delegation chain
                chain = []
                for task in tasks:
                    chain.append({
                        "agent_id": task.get("agent", "supervisor"),
                        "action": task.get("action", ""),
                        "params": task.get("params", {}),
                        "status": "pending"
                    })
                
                # Execute each task in sequence
                sub_results = []
                all_success = True
                for i, step in enumerate(chain):
                    step["status"] = "working"
                    agent_id_step = step["agent_id"]
                    action_step = step["action"]
                    params_step = step["params"]
                    
                    # Execute via the action map
                    agent_action = self._execute_by_action(action_step, params_step)
                    
                    if agent_action and agent_action.get("success"):
                        step["status"] = "done"
                        sub_results.append({
                            "agent_id": agent_id_step,
                            "result": agent_action.get("result", ""),
                            "success": True
                        })
                    else:
                        step["status"] = "failed"
                        all_success = False
                        sub_results.append({
                            "agent_id": agent_id_step,
                            "result": agent_action.get("result", "Error") if agent_action else "Failed",
                            "success": False
                        })
                
                # Build visual chain text
                chain_visual = " → ".join([
                    f"{AGENTS_BY_ID.get(s['agent_id'], AGENTS_BY_ID['supervisor'])['icon']} {AGENTS_BY_ID.get(s['agent_id'], AGENTS_BY_ID['supervisor'])['name']}"
                    for s in chain
                ])
                
                # Combine results
                combined = "\n\n---\n\n".join([
                    f"**{AGENTS_BY_ID.get(r['agent_id'], AGENTS_BY_ID['supervisor'])['icon']} {AGENTS_BY_ID.get(r['agent_id'], AGENTS_BY_ID['supervisor'])['name']}:**\n{r['result']}"
                    for r in sub_results
                ])
                
                supervisor_msg = genai_result.get("response", f"🐱 Mixmoi: Mendelegasikan ke {len(chain)} agent!")
                
                return {
                    "action": "delegate_multi",
                    "agent_id": "supervisor",
                    "sub_agents": [s["agent_id"] for s in chain],
                    "delegation_chain": chain,
                    "success": all_success,
                    "result": f"{supervisor_msg}\n\n📋 **Delegasi Chain:**\n{chain_visual}\n\n{combined}",
                    "data": {
                        "chain": chain,
                        "sub_results": sub_results,
                        "chain_visual": chain_visual
                    }
                }
            
            # ── SINGLE AGENT DELEGATION ──
            else:
                # Route to the specific agent
                result = self._execute_by_action(action, params)
                if result:
                    agent_def = AGENTS_BY_ID.get(agent_id, AGENTS_BY_ID["supervisor"])
                    supervisor_msg = genai_result.get("response", f"🐱 Mixmoi: Saya delegasikan ke {agent_def['icon']} {agent_def['name']}!")
                    
                    if result.get("success"):
                        result["result"] = f"{supervisor_msg}\n\n{result['result']}"
                    result["agent_id"] = agent_id
                    result["sub_agents"] = [agent_id]
                    result["delegation_chain"] = [{
                        "agent_id": agent_id,
                        "action": action,
                        "status": "done"
                    }]
                    return result
        
        # ─── Fallback: keyword matching (NO RECURSION - uses _skip_genai=True) ──
        fallback_agent = determine_agent(command)
        result = self.process_command(command, _skip_genai=True)
        result["agent_id"] = fallback_agent
        result["sub_agents"] = [fallback_agent]
        result["delegation_chain"] = [{
            "agent_id": fallback_agent,
            "action": result.get("action", ""),
            "status": "done"
        }]
        return result

    def process_command(self, command: str, _skip_genai: bool = False) -> dict:
        """
        SUPERVISOR PROCESSING: Process a command with multi-agent delegation.
        
        Strategy:
        1. Try Gemini AI (Supervisor thinking) for smart delegation
           - Can delegate to SINGLE agent or MULTIPLE agents
        2. Fall back to keyword matching (always works)
        
        Returns: { "action": "...", "result": "...", "success": bool, 
                   "data": {...}, "agent_id": "...", "sub_agents": [],
                   "delegation_chain": [] }
        """
        command_lower = command.lower().strip()

        # Log the command
        self.command_history.append({
            "command": command,
            "timestamp": datetime.now().isoformat()
        })

        # ─── Determine which agent handles this ───────────────────────────
        predicted_agent = determine_agent(command)

        # ─── TRY GEMINI SUPERVISOR DELEGATION FIRST (skip if called from fallback) ──
        if self.groq_configured and not _skip_genai:
            delegation = self.delegate_task(command)
            if delegation and delegation.get("success", False):
                self._log_conversation(command, delegation)
                return delegation
            # If delegation failed, fall through to keyword matching

        # ─── FALLBACK: keyword matching ───────────────────────────────────
        result = None

        # WhatsApp commands
        result = result or self._cmd_whatsapp_send(command_lower, command)
        result = result or self._cmd_whatsapp_promo(command_lower)
        result = result or self._cmd_whatsapp_bulk(command_lower)

        # Inventory commands
        result = result or self._cmd_inventory_check(command_lower)
        result = result or self._cmd_inventory_low_stock(command_lower)
        result = result or self._cmd_inventory_summary(command_lower)
        result = result or self._cmd_inventory_search(command_lower)
        result = result or self._cmd_inventory_add_sample(command_lower)
        result = result or self._cmd_inventory_export(command_lower)

        # Price List commands
        result = result or self._cmd_price_list_pdf(command_lower)
        result = result or self._cmd_price_list_flyer(command_lower)
        result = result or self._cmd_price_list_text(command_lower)

        # Sales / Dashboard commands
        result = result or self._cmd_sales_summary(command_lower)
        result = result or self._cmd_sales_chart(command_lower)
        result = result or self._cmd_sales_top(command_lower)

        # Social Media commands
        result = result or self._cmd_social_caption(command_lower)
        result = result or self._cmd_social_plan(command_lower)
        result = result or self._cmd_social_tip(command_lower)

        # Competitor commands
        result = result or self._cmd_competitor_check(command_lower)

        # Order commands
        result = result or self._cmd_orders_summary(command_lower)
        result = result or self._cmd_orders_pending(command_lower)
        result = result or self._cmd_orders_sample(command_lower)

        # Loyalty commands
        result = result or self._cmd_loyalty_customers(command_lower)
        result = result or self._cmd_loyalty_tiers(command_lower)

        # Sheet / Report commands
        result = result or self._cmd_report_excel(command_lower)
        result = result or self._cmd_report_daily(command_lower)
        result = result or self._cmd_catalog_excel(command_lower)

        # QR commands
        result = result or self._cmd_qr_catalog(command_lower)
        result = result or self._cmd_qr_generate(command_lower)

        # 📈 GROWTH PARTNER commands
        result = result or self._cmd_growth_competitive_intel(command_lower)
        result = result or self._cmd_growth_pricing_strategy(command_lower)
        result = result or self._cmd_growth_content_creation(command_lower)

        # 🔬 COMPANY RESEARCH commands
        result = result or self._cmd_company_research(command_lower)

        # 🆕 NEW AUTOMATION commands
        result = result or self._cmd_random_promo(command_lower)
        result = result or self._cmd_tier_promo(command_lower)
        result = result or self._cmd_ai_auto_reply(command_lower)
        result = result or self._cmd_schedule_auto(command_lower)
        result = result or self._cmd_schedule_status(command_lower)

        # Help / General commands
        result = result or self._cmd_help(command_lower)
        result = result or self._cmd_status(command_lower)

        # If nothing matched
        if not result:
            result = {
                "action": "unknown",
                "success": False,
                "result": "Maaf, saya tidak mengerti perintah itu. Ketik 'bantuan' untuk melihat apa yang bisa saya lakukan!",
                "data": {},
                "agent_id": predicted_agent,
                "sub_agents": [],
                "delegation_chain": []
            }

        # Add agent metadata to result
        if "agent_id" not in result:
            result["agent_id"] = predicted_agent
        if "sub_agents" not in result:
            result["sub_agents"] = [result.get("agent_id", predicted_agent)]
        if "delegation_chain" not in result:
            result["delegation_chain"] = [{
                "agent_id": result.get("agent_id", predicted_agent),
                "action": result.get("action", ""),
                "status": "done"
            }]

        self._log_conversation(command, result)
        return result

    def _execute_by_action(self, action: str, params: dict) -> Optional[dict]:
        """Execute a command by its action name (from Gemini interpretation)."""
        action_map = {
            "inventory_check": lambda: self._cmd_inventory_check("cek stok"),
            "inventory_low_stock": lambda: self._cmd_inventory_low_stock("stok menipis"),
            "inventory_search": lambda: self._cmd_inventory_search(f"cari {params.get('query', '')}"),
            "inventory_add_sample": lambda: self._cmd_inventory_add_sample("tambah sample"),
            "inventory_summary": lambda: self._cmd_inventory_summary("summary"),
            "inventory_export": lambda: self._cmd_inventory_export("export inventory"),
            "whatsapp_send": lambda: self._cmd_whatsapp_send(f"kirim promo ke {params.get('phone', '')}", f"kirim promo ke {params.get('phone', '')}"),
            "whatsapp_promo_blast": lambda: self._cmd_whatsapp_promo("promo blast"),
            "price_list_pdf": lambda: self._cmd_price_list_pdf("buat daftar harga"),
            "price_list_flyer": lambda: self._cmd_price_list_flyer("buat flyer"),
            "price_list_text": lambda: self._cmd_price_list_text("teks harga"),
            "sales_summary": lambda: self._cmd_sales_summary("laporan penjualan"),
            "sales_chart": lambda: self._cmd_sales_chart("chart penjualan"),
            "sales_top": lambda: self._cmd_sales_top("produk terlaris"),
            "social_caption": lambda: self._cmd_social_caption(f"buat caption {params.get('topic', 'promo')}"),
            "social_plan": lambda: self._cmd_social_plan("rencana konten"),
            "social_tip": lambda: self._cmd_social_tip("tips ban"),
            "competitor_check": lambda: self._cmd_competitor_check(f"cek kompetitor {params.get('product', 'ban')}"),
            "orders_summary": lambda: self._cmd_orders_summary("cek pesanan"),
            "orders_pending": lambda: self._cmd_orders_pending("pesanan pending"),
            "orders_sample": lambda: self._cmd_orders_sample("sample pesanan"),
            "loyalty_customers": lambda: self._cmd_loyalty_customers("daftar pelanggan"),
            "loyalty_tiers": lambda: self._cmd_loyalty_tiers("level membership"),
            "report_excel": lambda: self._cmd_report_excel("buat laporan excel"),
            "report_daily": lambda: self._cmd_report_daily("ringkasan harian"),
            "catalog_excel": lambda: self._cmd_catalog_excel("katalog excel"),
            "qr_catalog": lambda: self._cmd_qr_catalog("buat katalog html"),
            "qr_generate": lambda: self._cmd_qr_generate("buat qr"),
            "status": lambda: self._cmd_status("status"),
            "help": lambda: self._cmd_help("bantuan"),
            "random_promo": lambda: self._cmd_random_promo(f"kirim ke {params.get('count', 10)} random"),
            "tier_promo": lambda: self._cmd_tier_promo(f"kirim ke {params.get('tier', 'all')}"),
            "ai_reply": lambda: self._cmd_ai_auto_reply(f"balas {params.get('message', 'halo')}"),
            "schedule": lambda: self._cmd_schedule_auto(f"jadwal promo setiap {params.get('time', '10:00')}"),
            "schedule_status": lambda: self._cmd_schedule_status("cek jadwal"),
            # ── Growth Partner actions ──
            "competitive_analysis": lambda: self._cmd_growth_competitive_intel(f"analisis kompetitor {params.get('competitor_data', 'SSM')}"),
            "pricing_strategy": lambda: self._cmd_growth_pricing_strategy(f"strategi harga {params.get('target_size', '185/65R14')} {params.get('brand', 'value')}"),
            "content_creation": lambda: self._cmd_growth_content_creation(f"buat konten {params.get('topic', 'promo')} {params.get('tone', 'Trustable')} {params.get('store', 'Banyumanik')}"),
            # ── Company Research actions ──
            "company_research": lambda: self._cmd_company_research(f"research {params.get('company', '')}"),
        }

        handler = action_map.get(action)
        if handler:
            try:
                return handler()
            except Exception as e:
                return {
                    "action": action,
                    "success": False,
                    "result": f"Terjadi kesalahan saat menjalankan perintah: {e}",
                    "data": {}
                }
        return None

    def _log_conversation(self, command: str, result: dict):
        """Log conversation to history."""
        self.conversation_log.append({
            "user": command,
            "ai": result.get("result", ""),
            "action": result.get("action", ""),
            "success": result.get("success", False),
            "timestamp": datetime.now().isoformat()
        })

    def set_groq_api_key(self, api_key: str) -> bool:
        """Update the Groq API key at runtime."""
        return self._init_groq(api_key)

    def set_groq_model(self, model: str):
        """Change the Groq model name."""
        self.groq_model = model

    # ═══════════════════════════════════════════════════════════════════
    # COMMAND PATTERNS (Fallback keyword matching)
    # ═══════════════════════════════════════════════════════════════════

    # ─── HELP ──────────────────────────────────────────────────────────
    def _cmd_help(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["bantuan", "help", " bisa", "perintah", "command", "apa aja", "tolong"]):
            help_text = """\
🤖 *AI COMMAND CENTER - Tersedia Perintah:*

📱 *WHATSAPP:*
• "kirim promo ke [nomor]" - Kirim promo WhatsApp
• "promo blast" - Kirim ke semua pelanggan
• "kirim pesan ke [nomor] isi [pesan]" - Kirim pesan custom

📦 *INVENTORY:*
• "cek stok" - Lihat semua stok ban
• "stok menipis" - Lihat produk yang hampir habis
• "cari [produk]" - Cari produk tertentu
• "tambah sample produk" - Tambah data contoh
• "export inventory" - Export ke CSV

💰 *PRICE LIST:*
• "buat daftar harga" - Generate PDF price list
• "buat flyer promo" - Generate gambar flyer
• "teks daftar harga" - Teks untuk WhatsApp

📈 *SALES:*
• "laporan penjualan" - Ringkasan penjualan
• "chart penjualan" - Generate chart pendapatan
• "produk terlaris" - Lihat top produk

📣 *SOSIAL MEDIA:*
• "buat caption [promo/tips/testimoni]" - Generate caption
• "tips ban" - Tips perawatan ban random

🔍 *COMPETITOR:*
• "cek kompetitor [produk]" - Cek harga kompetitor

📋 *ORDERS:*
• "cek pesanan" - Lihat semua pesanan
• "pesanan pending" - Lihat pesanan belum selesai

⭐ *LOYALTY:*
• "daftar pelanggan" - Lihat pelanggan & poin
• "level membership" - Info tier member

📑 *LAPORAN:*
• "buat laporan excel" - Generate laporan Excel
• "ringkasan harian" - Ringkasan bisnis hari ini

📱 *QR:*
• "buat katalog QR" - Generate QR code catalog
• "buat katalog html" - Generate katalog online

📈 *GROWTH PARTNER:*
• "analisis kompetitor [SSM/Omah Ban/HSR]" - Intel kompetitor & counter-move
• "strategi harga loss leader" - Rekomendasi paket ban & pricing
• "buat konten [promo/tips/produk]" - Buat konten Instagram + caption
• "buat konten [topik] di Ungaran" - Konten spesifik lokasi

🔬 *COMPANY RESEARCH (via Serper + Gemini):*
• "research [nama perusahaan]" - Riset profil & overview perusahaan
• "cari perusahaan [nama]" - Cari informasi lengkap perusahaan
• "profil [nama perusahaan]" - Dapatkan laporan perusahaan
• "info [nama perusahaan]" - Info & berita terbaru perusahaan

🤖 *AUTOMASI BARU (pake Gemini AI):*
• "promo random 5 orang" - Kirim promo ke N pelanggan acak
• "promo gold/platinum" - Kirim promo berdasarkan tier member
• "balas [pesan]" - Dapat balasan cerdas untuk chat pelanggan
• "jadwal promo jam 10:00" - Jadwalkan promo otomatis tiap hari
• "jadwal promo tiap 3 jam" - Promo otomatis setiap 3 jam
"""
            return {
                "action": "help",
                "success": True,
                "result": help_text.strip(),
                "data": {"commands": help_text}
            }
        return None

    # ─── STATUS ────────────────────────────────────────────────────────
    def _cmd_status(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["status", "dashboard", "ringkasan", "summary"]):
            inv = self.tools["inventory"].get_summary()
            dash = self.tools["dashboard"].get_stats()
            orders = self.tools["orders"].get_summary()

            status = f"""\
📊 *STATUS BISNIS - {datetime.now().strftime('%d/%m/%Y')}*
━━━━━━━━━━━━━━━━━━━━━

📦 *INVENTORY:*
  • Total Produk: {inv.get('total_items', 0)}
  • Total Stok: {inv.get('total_stock', 0)}
  • Stok Menipis: {inv.get('low_stock_count', 0)} ⚠️
  • Stok Habis: {inv.get('out_of_stock_count', 0)}

💰 *PENJUALAN:*
  • Total Pendapatan: Rp {dash.get('total_revenue', 0):,}
  • Total Transaksi: {dash.get('total_transactions', 0)}
  • Rata-rata: Rp {dash.get('avg_transaction', 0):,}

📋 *PESANAN:*
  • Total: {orders.get('total', 0)}
  • Pending: {orders.get('pending', 0)}
  • Selesai: {orders.get('completed', 0)}
"""
            return {
                "action": "status",
                "success": True,
                "result": status.strip(),
                "data": {"inventory": inv, "sales": dash, "orders": orders}
            }
        return None

    # ─── WHATSAPP ──────────────────────────────────────────────────────
    def _cmd_whatsapp_send(self, cmd: str, original: str) -> Optional[dict]:
        # Pattern: kirim promo ke 08123456789
        match = re.search(r'kirim\s+(promo|pesan|halo|harga|stok|lokasi)\s+ke\s+(\d+)', cmd)
        if match:
            template_key = match.group(1)
            phone = match.group(2)

            # Map to valid template keys
            template_map = {
                "promo": "promo", "pesan": "promo",
                "halo": "halo", "harga": "harga",
                "stok": "stok", "lokasi": "lokasi"
            }
            key = template_map.get(template_key, "promo")

            from tools.whatsapp_bot import TIRE_TEMPLATES
            message = TIRE_TEMPLATES.get(key, TIRE_TEMPLATES["promo"])

            try:
                self.tools["whatsapp"].send_whatsapp(phone, message)
                return {
                    "action": "whatsapp_send",
                    "success": True,
                    "result": f"✅ Pesan '{template_key}' dikirim ke {phone}! WhatsApp akan terbuka.",
                    "data": {"phone": phone, "template": key}
                }
            except Exception as e:
                return {
                    "action": "whatsapp_send",
                    "success": False,
                    "result": f"❌ Gagal kirim: {e}",
                    "data": {}
                }

        # Pattern: kirim pesan ke 08xxx isi [pesan custom]
        match2 = re.search(r'kirim\s+pesan\s+ke\s+(\d+)\s+isi\s+(.+)', cmd)
        if match2:
            phone = match2.group(1)
            custom_message = match2.group(2)
            try:
                self.tools["whatsapp"].send_whatsapp(phone, custom_message)
                return {
                    "action": "whatsapp_send_custom",
                    "success": True,
                    "result": f"✅ Pesan custom dikirim ke {phone}!",
                    "data": {"phone": phone, "message": custom_message}
                }
            except Exception as e:
                return {"action": "whatsapp_send", "success": False, "result": f"❌ Gagal: {e}", "data": {}}

        return None

    def _cmd_whatsapp_promo(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["promo blast", "blast promo", "promo semua", "kirim semua"]):
            customers = self.tools["loyalty"].customers
            if not customers:
                self.tools["loyalty"].add_sample_customers()
                customers = self.tools["loyalty"].customers

            if not customers:
                return {"action": "whatsapp_promo", "success": False,
                        "result": "❌ Belum ada pelanggan terdaftar.", "data": {}}

            contacts = [{"name": c.get("Nama", ""), "phone": c.get("Telepon", "")}
                       for c in customers]

            import threading
            from tools.whatsapp_bot import TIRE_TEMPLATES
            thread = threading.Thread(
                target=lambda: self.tools["whatsapp"].bulk_send(contacts, TIRE_TEMPLATES["promo"]),
                daemon=True
            )
            thread.start()

            return {
                "action": "whatsapp_promo_blast",
                "success": True,
                "result": f"📨 Promo sedang dikirim ke {len(contacts)} pelanggan! WhatsApp akan terbuka satu per satu.",
                "data": {"total": len(contacts)}
            }
        return None

    def _cmd_whatsapp_bulk(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["bulk", "broadcast"]):
            return self._cmd_whatsapp_promo(cmd)
        return None

    # ─── INVENTORY ────────────────────────────────────────────────────
    def _cmd_inventory_check(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["cek stok", "lihat stok", "tampilkan stok", "daftar produk", "semua produk"]):
            products = self.tools["inventory"].products
            if not products:
                self.tools["inventory"].add_sample_data()
                products = self.tools["inventory"].products

            lines = ["📦 *DAFTAR STOK BAN:*\n"]
            for i, p in enumerate(products[:15], 1):
                stock_icon = "✅" if p.get("Stok", 0) > 5 else "⚠️" if p.get("Stok", 0) > 0 else "❌"
                lines.append(
                    f"{i}. {stock_icon} {p.get('Merek', '-')} {p.get('Ukuran', '-')}\n"
                    f"   Ring {p.get('Ring', '-')} | Rp {p.get('Harga Jual', 0):,} | Stok: {p.get('Stok', 0)}"
                )

            if len(products) > 15:
                lines.append(f"\n...dan {len(products) - 15} produk lainnya")

            return {
                "action": "inventory_check",
                "success": True,
                "result": "\n".join(lines),
                "data": {"products": products[:15], "total": len(products)}
            }
        return None

    def _cmd_inventory_low_stock(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["stok menipis", "stok habis", "low stock", "restock"]):
            low = self.tools["inventory"].get_low_stock_products()
            out = self.tools["inventory"].get_out_of_stock()

            if not low and not out:
                return {"action": "inventory_low_stock", "success": True,
                        "result": "✅ Semua stok aman! Tidak ada produk yang menipis.", "data": {}}

            lines = ["⚠️ *PRODUK PERLU RESTOCK:*\n"]
            for p in low:
                emoji = "🔴" if p.get("Stok", 0) == 0 else "🟡"
                lines.append(f"{emoji} {p.get('Merek', '-')} {p.get('Ukuran', '-')}: Stok {p.get('Stok', 0)}")

            return {
                "action": "inventory_low_stock",
                "success": True,
                "result": "\n".join(lines),
                "data": {"low_stock": low, "out_of_stock": out}
            }
        return None

    def _cmd_inventory_summary(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["summary inventory", "ringkasan stok", "total stok"]):
            summary = self.tools["inventory"].get_summary()
            return {
                "action": "inventory_summary",
                "success": True,
                "result": (
                    f"📊 *RINGKASAN INVENTORY:*\n"
                    f"• Total Produk: {summary.get('total_items', 0)}\n"
                    f"• Total Stok: {summary.get('total_stock', 0)}\n"
                    f"• Total Nilai: Rp {summary.get('total_value', 0):,}\n"
                    f"• Merek: {summary.get('unique_brands', 0)}\n"
                    f"• Stok Menipis: {summary.get('low_stock_count', 0)}\n"
                    f"• Stok Habis: {summary.get('out_of_stock_count', 0)}"
                ),
                "data": summary
            }
        return None

    def _cmd_inventory_search(self, cmd: str) -> Optional[dict]:
        match = re.search(r'cari\s+(.+)', cmd)
        if match:
            query = match.group(1).strip()
            results = self.tools["inventory"].search_products(query)

            if not results:
                return {"action": "inventory_search", "success": True,
                        "result": f"🔍 Tidak ada produk ditemukan untuk '{query}'.", "data": {}}

            lines = [f"🔍 *Hasil pencarian: '{query}'* ({len(results)} ditemukan)\n"]
            for p in results:
                lines.append(f"• {p.get('Merek', '-')} {p.get('Ukuran', '-')} - Rp {p.get('Harga Jual', 0):,} (Stok: {p.get('Stok', 0)})")

            return {
                "action": "inventory_search",
                "success": True,
                "result": "\n".join(lines),
                "data": {"query": query, "results": results}
            }
        return None

    def _cmd_inventory_add_sample(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["tambah sample", "sample produk", "contoh produk"]):
            count = self.tools["inventory"].add_sample_data()
            return {
                "action": "inventory_add_sample",
                "success": True,
                "result": f"✅ {count} produk contoh berhasil ditambahkan ke inventory!",
                "data": {"count": count}
            }
        return None

    def _cmd_inventory_export(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["export inventory", "export csv", "download data"]):
            filepath = str(Path.cwd() / "output" / f"inventory_{datetime.now().strftime('%Y%m%d')}.csv")
            self.tools["inventory"].export_csv(filepath)
            return {
                "action": "inventory_export",
                "success": True,
                "result": f"✅ Data inventory di-export ke:\n{filepath}",
                "data": {"filepath": filepath}
            }
        return None

    # ─── PRICE LIST ───────────────────────────────────────────────────
    def _cmd_price_list_pdf(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["buat daftar harga", "generate pdf", "daftar harga pdf", "price list"]):
            products = self.tools["inventory"].products
            if not products:
                self.tools["inventory"].add_sample_data()
                products = self.tools["inventory"].products

            filepath = self.tools["price_list"].generate_pdf(products)
            if filepath:
                return {
                    "action": "price_list_pdf",
                    "success": True,
                    "result": f"✅ PDF daftar harga tersimpan di:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "price_list_pdf", "success": False,
                        "result": "❌ Gagal generate PDF. Pastikan fpdf2 terinstall.", "data": {}}
        return None

    def _cmd_price_list_flyer(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["buat flyer", "generate flyer", "flyer promo", "buat gambar promo"]):
            filepath = self.tools["price_list"].generate_flyer(
                "PROMO SPESIAL!\nDiskon 20% Semua Ban",
                "Mulai Rp 350rb"
            )
            if filepath:
                return {
                    "action": "price_list_flyer",
                    "success": True,
                    "result": f"✅ Flyer promo tersimpan di:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "price_list_flyer", "success": False,
                        "result": "❌ Gagal generate flyer. Pastikan Pillow terinstall.", "data": {}}
        return None

    def _cmd_price_list_text(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["teks harga", "teks daftar harga", "list harga teks", "copy harga"]):
            products = self.tools["inventory"].products
            if not products:
                self.tools["inventory"].add_sample_data()
                products = self.tools["inventory"].products

            text = self.tools["price_list"].generate_text(products[:10])
            return {
                "action": "price_list_text",
                "success": True,
                "result": f"📝 *Teks Daftar Harga (copy ke WhatsApp):*\n\n{text}",
                "data": {"text": text}
            }
        return None

    # ─── SALES ─────────────────────────────────────────────────────────
    def _cmd_sales_summary(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["laporan penjualan", "penjualan", "sales report", "omzet"]):
            if not self.tools["dashboard"].sales_data:
                self.tools["dashboard"].add_sample_sales()

            report = self.tools["dashboard"].generate_report()
            return {
                "action": "sales_summary",
                "success": True,
                "result": report,
                "data": self.tools["dashboard"].get_stats()
            }
        return None

    def _cmd_sales_chart(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["chart penjualan", "grafik penjualan", "chart pendapatan"]):
            if not self.tools["dashboard"].sales_data:
                self.tools["dashboard"].add_sample_sales()

            filepath = self.tools["dashboard"].chart_daily_revenue()
            if filepath:
                return {
                    "action": "sales_chart",
                    "success": True,
                    "result": f"📈 Chart pendapatan harian tersimpan di:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "sales_chart", "success": False,
                        "result": "❌ Gagal generate chart. Pastikan matplotlib terinstall.", "data": {}}
        return None

    def _cmd_sales_top(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["produk terlaris", "top produk", "best seller", "paling laku"]):
            if not self.tools["dashboard"].sales_data:
                self.tools["dashboard"].add_sample_sales()

            filepath = self.tools["dashboard"].chart_top_products()
            if filepath:
                return {
                    "action": "sales_top",
                    "success": True,
                    "result": f"🏆 Chart produk terlaris tersimpan di:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "sales_top", "success": False,
                        "result": "❌ Gagal generate chart.", "data": {}}
        return None

    # ─── SOCIAL MEDIA ──────────────────────────────────────────────────
    def _cmd_social_caption(self, cmd: str) -> Optional[dict]:
        match = re.search(r'buat\s+caption\s+(.+)|generate\s+caption\s+(.+)', cmd)
        if match:
            topic = match.group(1) or match.group(2)
            topic = topic.strip()

            # Determine template
            template_map = {
                "promo": "promo_harga", "diskon": "promo_harga",
                "tips": "tips_ban", "tips ban": "tips_ban",
                "testimoni": "testimoni", "produk": "produk_unggulan",
                "new": "new_stock", "baru": "new_stock",
            }

            template_key = "promo_harga"
            for k, v in template_map.items():
                if k in topic.lower():
                    template_key = v
                    break

            caption = self.tools["social"].generate_caption(
                template_key,
                product="Ban Michelin Energy XM2",
                price=750000,
                size="185/65R14",
                tipe="Energy XM2+",
                car_type="Sedan/MPV"
            )

            return {
                "action": "social_caption",
                "success": True,
                "result": f"✍️ *Caption {template_key} siap!*\n\n{caption}\n\n📋 Copy dan paste ke Instagram/WhatsApp!",
                "data": {"template": template_key, "caption": caption}
            }
        return None

    def _cmd_social_plan(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["rencana konten", "content plan", "jadwal posting", "konten minggu"]):
            plan = self.tools["social"].generate_content_plan(7)
            lines = ["📅 *Rencana Konten 7 Hari:*\n"]
            for p in plan:
                lines.append(f"• {p['day']} ({p['date']}): {p['template']}")
            return {
                "action": "social_plan",
                "success": True,
                "result": "\n".join(lines),
                "data": {"plan": plan}
            }
        return None

    def _cmd_social_tip(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["tips ban", "tips", "tips perawatan"]):
            tip = self.tools["social"].get_random_tip()
            return {
                "action": "social_tip",
                "success": True,
                "result": f"💡 *Tips Perawatan Ban:*\n\n{tip}",
                "data": {"tip": tip}
            }
        return None

    # ─── COMPETITOR ───────────────────────────────────────────────────
    def _cmd_competitor_check(self, cmd: str) -> Optional[dict]:
        match = re.search(r'cek\s+kompetitor\s+(.+)|cek\s+harga\s+(.+)|kompetitor\s+(.+)', cmd)
        if match:
            query = match.group(1) or match.group(2) or match.group(3)
            query = query.strip()

            results = self.tools["competitor"].check_price_changes(query)

            lines = [f"🔍 *Harga Kompetitor untuk '{query}':*\n"]
            for r in results:
                change = ""
                if r.get("price_change"):
                    arrow = "🔺" if r.get("price_change", 0) > 0 else "🔻"
                    change = f" {arrow} {abs(r.get('price_change', 0)):,}"
                lines.append(f"• {r.get('source', '-')}: Rp {r.get('price', 0):,}{change}")

            return {
                "action": "competitor_check",
                "success": True,
                "result": "\n".join(lines),
                "data": {"results": results}
            }
        return None

    # ─── ORDERS ───────────────────────────────────────────────────────
    def _cmd_orders_summary(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["cek pesanan", "lihat pesanan", "daftar pesanan", "semua pesanan"]):
            orders = self.tools["orders"].orders
            if not orders:
                return {"action": "orders_summary", "success": True,
                        "result": "📋 Belum ada pesanan. Ketik 'tambah sample pesanan' untuk contoh.", "data": {}}

            lines = ["📋 *DAFTAR PESANAN:*\n"]
            for o in orders[:10]:
                lines.append(f"• {o.get('ID', '-')}: {o.get('Pelanggan', '-')} - Rp {o.get('Total', 0):,} [{o.get('Status', '-')}]")

            if len(orders) > 10:
                lines.append(f"\n...dan {len(orders) - 10} pesanan lainnya")

            return {
                "action": "orders_summary",
                "success": True,
                "result": "\n".join(lines),
                "data": {"orders": orders[:10]}
            }
        return None

    def _cmd_orders_pending(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["pesanan pending", "pending", "pesanan aktif", "belum selesai"]):
            pending = self.tools["orders"].get_pending_orders()
            if not pending:
                return {"action": "orders_pending", "success": True,
                        "result": "✅ Tidak ada pesanan pending! Semua selesai.", "data": {}}

            lines = ["⏳ *PESANAN PENDING:*\n"]
            for p in pending:
                lines.append(f"• {p.get('ID', '-')}: {p.get('Pelanggan', '-')} - {p.get('Status', '-')}")

            return {
                "action": "orders_pending",
                "success": True,
                "result": "\n".join(lines),
                "data": {"pending": pending}
            }
        return None

    def _cmd_orders_sample(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["tambah sample pesanan", "sample pesanan", "contoh pesanan"]):
            self.tools["orders"].add_sample_orders()
            return {
                "action": "orders_sample",
                "success": True,
                "result": "✅ 15 sample pesanan berhasil ditambahkan!",
                "data": {}
            }
        return None

    # ─── LOYALTY ──────────────────────────────────────────────────────
    def _cmd_loyalty_customers(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["daftar pelanggan", "lihat pelanggan", "customer", "pelanggan"]):
            customers = self.tools["loyalty"].customers
            if not customers:
                self.tools["loyalty"].add_sample_customers()
                customers = self.tools["loyalty"].customers

            lines = ["⭐ *DAFTAR PELANGGAN:*\n"]
            for c in customers:
                tier_icon = {"Reguler": "🟢", "Silver": "⚪", "Gold": "🟡", "Platinum": "💎"}
                icon = tier_icon.get(c.get("Tier", "Reguler"), "🟢")
                lines.append(f"{icon} {c.get('Nama', '-')}: {c.get('Total Poin', 0)} poin ({c.get('Tier', 'Reguler')})")

            return {
                "action": "loyalty_customers",
                "success": True,
                "result": "\n".join(lines),
                "data": {"customers": customers}
            }
        return None

    def _cmd_loyalty_tiers(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["level membership", "tier", "member", "tingkat member"]):
            tiers = self.tools["loyalty"].get_all_tiers()
            lines = ["👑 *LEVEL MEMBERSHIP:*\n"]
            for t in tiers:
                lines.append(f"• {t['name']} (Min {t['min_points']} poin)")
                for b in t['benefits'][:2]:
                    lines.append(f"  ✓ {b}")
            return {
                "action": "loyalty_tiers",
                "success": True,
                "result": "\n".join(lines),
                "data": {"tiers": tiers}
            }
        return None

    # ─── REPORTS ──────────────────────────────────────────────────────
    def _cmd_report_excel(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["buat laporan excel", "laporan excel", "generate excel", "report excel"]):
            sales_data = self.tools["dashboard"].sales_data
            if not sales_data:
                self.tools["dashboard"].add_sample_sales()
                sales_data = self.tools["dashboard"].sales_data

            filepath = self.tools["sheets"].create_sales_report(sales_data)
            if filepath:
                return {
                    "action": "report_excel",
                    "success": True,
                    "result": f"📊 Laporan Excel tersimpan di:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "report_excel", "success": False,
                        "result": "❌ Gagal generate. Install: pip install openpyxl pandas", "data": {}}
        return None

    def _cmd_report_daily(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["ringkasan harian", "laporan harian", "daily report", "hari ini"]):
            inv = self.tools["inventory"].get_summary()
            orders = self.tools["orders"].get_summary()

            text = self.tools["sheets"].daily_summary_text(
                self.tools["dashboard"].sales_data,
                inv, orders
            )
            return {
                "action": "report_daily",
                "success": True,
                "result": text,
                "data": {"summary": text}
            }
        return None

    def _cmd_catalog_excel(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["katalog excel", "buat katalog excel", "catalog excel"]):
            products = self.tools["inventory"].products
            if not products:
                self.tools["inventory"].add_sample_data()
                products = self.tools["inventory"].products

            filepath = self.tools["sheets"].create_catalog_excel(products)
            if filepath:
                return {
                    "action": "catalog_excel",
                    "success": True,
                    "result": f"📗 Katalog Excel tersimpan di:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "catalog_excel", "success": False,
                        "result": "❌ Gagal generate.", "data": {}}
        return None

    # ─── QR ───────────────────────────────────────────────────────────
    def _cmd_qr_catalog(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["buat katalog html", "katalog html", "katalog online"]):
            products = self.tools["inventory"].products
            if not products:
                self.tools["inventory"].add_sample_data()
                products = self.tools["inventory"].products

            filepath = self.tools["qr_catalog"].save_catalog(products)
            if filepath:
                return {
                    "action": "qr_catalog_html",
                    "success": True,
                    "result": f"📱 Katalog HTML tersimpan! Buka di browser:\n{filepath}",
                    "data": {"filepath": filepath}
                }
            else:
                return {"action": "qr_catalog_html", "success": False,
                        "result": "❌ Gagal generate katalog.", "data": {}}
        return None

    def _cmd_qr_generate(self, cmd: str) -> Optional[dict]:
        if any(k in cmd for k in ["buat katalog qr", "generate qr", "qr code katalog", "buat qr"]):
            products = self.tools["inventory"].products
            if not products:
                self.tools["inventory"].add_sample_data()
                products = self.tools["inventory"].products

            html_path = self.tools["qr_catalog"].save_catalog(products)
            if html_path:
                qr_path = self.tools["qr_catalog"].generate_qr(
                    f"file://{html_path}",
                    label="Toko Ban Murah Anugerah"
                )
                if qr_path:
                    return {
                        "action": "qr_generate",
                        "success": True,
                        "result": f"📱 QR Code katalog tersimpan! Cetak dan tempel di toko:\n{qr_path}",
                        "data": {"qr_path": qr_path, "html_path": html_path}
                    }

            return {"action": "qr_generate", "success": False,
                    "result": "❌ Gagal generate QR code.", "data": {}}
        return None

    # ═══════════════════════════════════════════════════════════════════
    # GROWTH PARTNER — Executive Growth Partner Agent
    # 3 Jobs: Competitive Intel, Pricing Strategy, Content Creation
    # ═══════════════════════════════════════════════════════════════════

    # ─── COMPETITIVE INTEL ───────────────────────────────────────────
    def _cmd_growth_competitive_intel(self, cmd: str) -> Optional[dict]:
        """
        Job 1: Competitive Intelligence
        - Analyze competitor data, flag undercutting, suggest counter-moves
        """
        # Match: analisis kompetitor [nama], counter [kompetitor], dll
        match = re.search(r'(?:analisis|analisa|cek|pantau|lihat|bandingkan)\s+(?:kompetitor|pesaing|saingan)?\s*(.+)|counter\s+(.+)|(?:ssm|omah ban|hsr wheel)', cmd, re.IGNORECASE)
        
        competitor_query = None
        if match:
            competitor_query = match.group(1) or match.group(2) or match.group(3)
        
        # Check for specific competitor names in command
        competitor_found = None
        comp_names = {"ssm": "SSM Ban", "omah": "Omah Ban", "hsr": "HSR Wheel"}
        for key, name in comp_names.items():
            if key in cmd.lower():
                competitor_found = name
                break
        
        if competitor_found:
            return self._generate_competitive_analysis(competitor_found)
        
        if any(k in cmd for k in ["analisis kompetitor", "analisa kompetitor", "cek kompetitor", 
                                   "counter", "undercut", "strategi kompetitor"]):
            return self._generate_competitive_analysis(competitor_query or "kompetitor umum")
        
        return None

    def _generate_competitive_analysis(self, competitor: str) -> dict:
        """Generate competitive intel analysis and counter-move recommendations."""
        
        # Check inventory for comparison pricing
        products = self.tools["inventory"].products
        
        analysis = f"""\
📈 *GROWTH PARTNER — Competitive Intelligence*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Target:** {competitor}

"""

        # If we have inventory data, compare
        if products:
            premium_brands = ["Michelin", "Bridgestone", "Yokohama", "Goodyear", "Dunlop"]
            value_brands = ["Accelera", "GT Radial", "Delium", "Sailun"]
            
            # Get price ranges for comparison
            our_prices = {}
            for p in products[:5]:
                merek = p.get("Merek", "")
                harga = p.get("Harga Jual", 0)
                if merek and harga:
                    our_prices[merek] = harga
            
            if our_prices:
                analysis += "**🏷️ Rentang Harga Kami:**\n"
                for merek, harga in list(our_prices.items())[:5]:
                    analysis += f"• {merek}: Rp {harga:,}\n"
                analysis += "\n"

        analysis += """\
**🔍 Analisis Kompetitif:**
• Kompetitor seperti SSM, Omah Ban, dan HSR Wheel fokus pada ban pasar menengah
• Mereka sering pakai strategi harga miring di ukuran populer (185/65R14, 195/65R15)
• Kelemahan: layanan purna jual dan garansi terbatas

**⚡ Counter-Move Rekomendasi:**
• Jangan perang harga — unggulkan *value* (gratis balancing + spooring)
• Pakai Accelera/Sailun sebagai *loss leader* ukuran 185/65R14 (harga dekat modal)
• Upsell Michelin/Bridgestone dengan narasi "Garansi Resmi + Pasang Gratis"
• Promosi bundling: "Beli 4 Ban, Gratis Spooring + Balancing"
• Manfaatkan 2 lokasi (Banyumanik & Ungaran) untuk jangkauan lebih luas

**📱 CTA:**
Kirim promo WhatsApp ke pelanggan setia dengan mention harga termurah!"""

        return {
            "action": "growth_competitive_intel",
            "success": True,
            "result": analysis.strip(),
            "data": {
                "competitor": competitor,
                "analysis_type": "competitive_intel"
            }
        }

    # ─── PRICING STRATEGY ────────────────────────────────────────────
    def _cmd_growth_pricing_strategy(self, cmd: str) -> Optional[dict]:
        """
        Job 2: Pricing Strategy
        - Loss leader packages using value brands
        - High-margin recommendations
        - Price points for common tire sizes
        """
        if not any(k in cmd for k in ["strategi harga", "loss leader", "paket ban", "harga ban",
                                       "pricing", "high margin", "paket promo", "bundling",
                                       "upsell", "diskon ban"]):
            return None

        # Extract target size from command
        size_match = re.search(r'(\d{3}/\d{2}R\d{2})', cmd)
        target_size = size_match.group(1) if size_match else "185/65R14"
        
        # Extract brand preference
        brand = "value"  # default
        if any(k in cmd for k in ["premium", "michelin", "bridgestone", "yokohama"]):
            brand = "premium"
        elif any(k in cmd for k in ["accelera", "sailun", "murah"]):
            brand = "value"

        # Get inventory data
        products = self.tools["inventory"].products

        strategy = f"""\
📈 *GROWTH PARTNER — Pricing Strategy*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Target Ukuran:** {target_size}
**Fokus:** {'Value Brand (Loss Leader)' if brand == 'value' else 'Premium Brand (High Margin)'}

"""

        # Loss Leader Strategy (default)
        if brand == "value":
            strategy += """\
**🎯 LOSS LEADER PACKAGE — Accelera / Sailun**

Tujuan: Isi service bay, lalu upsell balancing & spooring!

**Paket 1 — Ekonomis**
• 4x Accelera/Sailun {target_size} — Rp 1.200.000 (harga modal)
• + Gratis Balancing (nilai Rp 100rb)
• + Upsell Spooring Rp 150rb
• **Margin potensial: Rp 150rb dari spooring + balancing**

**Paket 2 — Keluarga**
• 4x GT Radial {target_size} — Rp 1.600.000
• + Gratis Balancing + Spooring
• + 1x Free Rotasi Ban di bulan ke-3
• **Margin: Rp 300rb**

**💡 Rekomendasi:**
• Pasang display banner "Ban Mulai Rp 300rb!" di Banyumanik & Ungaran
• Staff 4 (Banyumanik) / 3 (Ungaran) cukup untuk handle 2-3 mobil/ hari
• Waktu pengerjaan ~45 menit per mobil"."""
        else:
            strategy += """\
**🎯 HIGH-MARGIN PREMIUM PACKAGE — Michelin / Bridgestone**

Tujuan: Jual value & keamanan, bukan harga!

**Paket Premium — Safety First**
• 4x Michelin Energy XM2+ {target_size} — Rp 3.200.000
• + Gratis Balancing + Spooring (senilai Rp 250rb)
• + Garansi Resmi 1 Tahun + Road Hazard
• + Free Rotasi & Tekanan Angin 6 Bulan
• **Margin: Rp 800rb - 1jt per set**

**💡 Rekomendasi:**
• Narasi jualan: "Investasi Keselamatan Keluarga"
• Tampilkan perbedaan kualitas (video side-by-side)
• Target: pemilik mobil baru, keluarga dengan anak
• Follow-up WA 3 hari setelah pasang untuk testimoni"""

        strategy += f"""

---
**💰 RINGKASAN KEUANGAN:**
• Modal loss leader: ~Rp 300rb per ban Accelera
• Harga jual paket: Rp 1.200.000 (4 ban + balancing)
• Upsell spooring: Rp 150rb (95% margin)
• **Total per transaksi: Rp 1.350.000 | Keuntungan bersih: Rp 150rb-300rb**
• Target 3 transaksi/hari = Rp 450rb-900rb/hari
"""

        return {
            "action": "growth_pricing_strategy",
            "success": True,
            "result": strategy.strip(),
            "data": {
                "target_size": target_size,
                "brand_focus": brand,
                "strategy_type": "loss_leader" if brand == "value" else "high_margin"
            }
        }

    # ─── CONTENT CREATION ────────────────────────────────────────────
    def _cmd_growth_content_creation(self, cmd: str) -> Optional[dict]:
        """
        Job 3: Content Creation
        - Uses the specific template from the Growth Partner config
        - Title, Store, Tone, Hook, Visual, Audio, Caption
        """
        if not any(k in cmd for k in ["buat konten", "konten instagram", "konten promo",
                                       "caption growth", "posting growth", "konten marketing",
                                       "iklan sosmed", "konten ban"]):
            return None

        # Determine topic
        topic = "promo"
        if any(k in cmd for k in ["tips", "tips ban", "tips perawatan"]):
            topic = "tips"
        elif any(k in cmd for k in ["testimoni", "review", "pelanggan"]):
            topic = "testimoni"
        elif any(k in cmd for k in ["produk", "produk baru", "new stock", "barang baru"]):
            topic = "produk"

        # Determine store
        store = "Banyumanik"
        if "ungaran" in cmd.lower():
            store = "Ungaran"

        # Determine tone
        tone = "Trustable"
        if any(k in cmd for k in ["fast", "cepat", "sat-set"]):
            tone = "Fast"
        elif any(k in cmd for k in ["premium", "mewah", "exclusive"]):
            tone = "Premium"
        elif any(k in cmd for k in ["murah", "hemat", "ekonomis", "affordable"]):
            tone = "Affordable"

        # Staff count based on store
        staff_count = "4" if store == "Banyumanik" else "3"

        # Generate content using the template
        content = self._generate_social_content(topic, store, tone, staff_count)

        return {
            "action": "growth_content_creation",
            "success": True,
            "result": content,
            "data": {
                "topic": topic,
                "store": store,
                "tone": tone
            }
        }

    def _generate_social_content(self, topic: str, store: str, tone: str, staff_count: str) -> str:
        """Generate social media content using the Growth Partner template."""
        
        whatsapp = "081280595845"
        
        content_templates = {
            "promo": {
                "title": "🔥 PROMO BAN MURAH — SAT-SET GAK PAKE LAMA! 🔥" if tone == "Fast" else \
                         "💎 PREMIUM TIRE DEALS — Kualitas Juara, Harga Bersahabat 💎" if tone == "Premium" else \
                         "🛞 BAN MURAH BERKUALITAS? ADA DISINI! 🛞",
                "hook": "Mau ganti ban tapi budget mepet? Tenang, Paling Murah Se-Anugerah!" if tone == "Affordable" else \
                        "Sat-set gak pake lama — ganti ban selesai dalam 45 menit!" if tone == "Fast" else \
                        "Keamanan keluarga dengan ban premium, tanpa bikin kantong bolong.",
                "body": f"""
📍 **{store} — Toko Ban Murah Anugerah**

Kami punya 15 merek ban siap pasang:
✅ Premium: Michelin, Bridgestone, Yokohama, Goodyear
✅ Value: Accelera, GT Radial, Sailun, Delium
✅ Semua ukuran mobil & SUV
✅ Garansi Resmi + Free Balancing

💥 **Harga Mulai Rp 300rb/ban!** 💥
+ Gratis Balancing untuk pembelian 4 ban
+ Free Tekanan Angin seumur hidup""",
            },
            "tips": {
                "title": "💡 TIPS BAN BIKIN AWET — BANYUMANIK & UNGARAN 💡",
                "hook": "Ban mobil itu investasi — rawat biar gak cepet gompel!",
                "body": f"""
📍 **{store} — Toko Ban Murah Anugerah**

**{staff_count} Tips Rawat Ban biar Awet:**

1️⃣ Cek tekanan angin 2 minggu sekali (30-33 PSI standar)
2️⃣ Rotasi ban setiap 8.000-10.000 km
3️⃣ Spooring & balancing tiap ganti ban atau setir bergetar
4️⃣ Jangan tunggu gundul — ganti di kedalaman 1.6mm

🔧 Butuh service ban? Langsung chat aja!""",
            },
            "testimoni": {
                "title": "⭐ TESTIMONI PELANGGAN PUAS — BANYUMANIK & UNGARAN ⭐",
                "hook": "Pelanggan puas, senyum lebar! Pelayanan Premium bikin betah.",
                "body": f"""
📍 **{store} — Toko Ban Murah Anugerah**

"Pasang ban di Toko Ban Murah Anugerah, pelayanannya ramah,
harganya miring, plus gratis balancing. Rekomended banget!"
— Bapak Andi, Pelanggan Setia

Kami selalu kasih:
✅ Harga Paling Murah
✅ Pelayanan Sat-Set (45 menit beres)
✅ Staff ramah & berpengalaman ({staff_count} staff siap bantu)

Gaskan mampir atau chat WhatsApp aja!""",
            },
            "produk": {
                "title": "🆕 NEW ARRIVAL — BAN TERBARU SUDAH DATANG! 🆕" if tone == "Fast" else \
                         "✨ KOLEKSI BAN TERBARU — KUALITAS NO.1 ✨",
                "hook": "Stok baru dateng! Ban premium & value semua ukuran ready!",
                "body": f"""
📍 **{store} — Toko Ban Murah Anugerah**

Yang baru datang:
🚗 Michelin Energy XM2+ — segala cuaca, irit BBM
🚙 Bridgestone Ecopia — nyaman di jalan
🏎️ Yokohama Geolandar — untuk SUV kesayangan
💰 Accelera & Sailun — ekonomis, kualitas oke

Semua ready stok! Langsung mampir atau chat WA buat tanya harga.""",
            }
        }

        tmpl = content_templates.get(topic, content_templates["promo"])
        
        audio_narasi = "🎵 Trending automotive beat" if tone == "Fast" else \
                       "🎵 Clean, professional narration" if tone == "Premium" else \
                       "🎵 Warm background music + narration"

        visuaL_setup = "📹 Simple setup — max 4 staff, clean workspace, ban display" if store == "Banyumanik" else \
                       "📹 Simple setup — max 3 staff, clean workspace, ban display"

        return f"""\
📈 *GROWTH PARTNER — Content Creation*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Title:** {tmpl['title']}
**Store:** {store} ({staff_count} staff)
**Tone:** {tone}
**Hook:** {tmpl['hook']}
**Visual:** {visuaL_setup}
**Audio:** {audio_narasi}

---
**📝 CAPTION:**{tmpl['body']}

---
**📱 CALL TO ACTION:**
👇👇👇
MASIH RAGU? CHAT LANGSUNG!
📍 **{store}** | {'Jl. Perintis Kemerdekaan No.10A, Banyumanik (08:00-17:30)' if store == 'Banyumanik' else 'Jl. Diponegoro No.79, Ungaran (08:00-18:00)'}
📲 **WhatsApp: {whatsapp}**
🌟 Toko Ban Murah Anugerah — Paling Murah, Pelayanan Premium!

#TokoBanMurah #BanMobil #PromoBan #Banyumanik #Ungaran #BanMurahAnugerah"""

    # ═══════════════════════════════════════════════════════════════════
    # COMPANY RESEARCH — Serper + Gemini
    # ═══════════════════════════════════════════════════════════════════

    def _cmd_company_research(self, cmd: str) -> Optional[dict]:
        """
        Research any company via web search (Serper) + Gemini synthesis.
        Trigger: "research [company name]" or "cari perusahaan [name]"
        """
        patterns = [
            r'(?:research|riset|teliti|cari)\s+(?:perusahaan|company)?\s*(.+)',
            r'(?:profil|profile|about|tentang)\s+(?:perusahaan|company)?\s*(.+)',
            r'info\s+(?:perusahaan|company)?\s*(.+)',
        ]
        company = None
        for p in patterns:
            m = re.search(p, cmd, re.IGNORECASE)
            if m:
                company = m.group(1).strip()
                break

        if not company:
            return None

        # Use configured Groq client from AI Command Center
        if not self.groq_configured:
            return {
                "action": "company_research",
                "success": False,
                "result": "❌ Groq AI belum dikonfigurasi.\n"
                          "Buka Pengaturan (gear icon) → masukkan Groq API Key → Simpan.",
                "data": {},
            }

        serper_key = os.environ.get("SERPER_API_KEY", "")
        if not serper_key:
            return {
                "action": "company_research",
                "success": False,
                "result": "❌ SERPER_API_KEY tidak ditemukan di .env",
                "data": {},
            }

        if not _has_company_research:
            return {
                "action": "company_research",
                "success": False,
                "result": "❌ Modul company_research tidak ditemukan.",
                "data": {},
            }

        result = research_company(company, serper_key, self.groq_client)
        return result

    # ═══════════════════════════════════════════════════════════════════
    # NEW AUTOMATION FEATURES
    # ═══════════════════════════════════════════════════════════════════

    # ─── RANDOM PROMO ────────────────────────────────────────────────
    def _cmd_random_promo(self, cmd: str) -> Optional[dict]:
        """Send promo to N random customers."""
        # Format: "promo random 5" atau "5 random" atau "kirim ke 10 orang"
        match = re.search(r'(\d+)\s*(orang|pelanggan|customer|random|acak)', cmd)
        match2 = re.search(r'(random|acak)\s*(\d+)', cmd)
        count = 10  # default
        if match:
            count = int(match.group(1))
        elif match2:
            count = int(match2.group(2))

        customers = self.tools["loyalty"].customers
        if not customers:
            self.tools["loyalty"].add_sample_customers()
            customers = self.tools["loyalty"].customers

        if not customers:
            return {"action": "random_promo", "success": False,
                    "result": "❌ Belum ada pelanggan terdaftar.", "data": {}}

        # Pick random customers
        selected = random.sample(customers, min(count, len(customers)))
        contacts = [{"name": c.get("Nama", ""), "phone": c.get("Telepon", "")}
                   for c in selected if c.get("Telepon", "")]

        if not contacts:
            return {"action": "random_promo", "success": False,
                    "result": "❌ Tidak ada pelanggan dengan nomor telepon.", "data": {}}

        from tools.whatsapp_bot import TIRE_TEMPLATES
        message = TIRE_TEMPLATES["promo"]

        def send_thread():
            for c in contacts:
                personalized = message.replace("{name}", c["name"])
                try:
                    self.tools["whatsapp"].send_whatsapp(c["phone"], personalized)
                    time.sleep(5)  # Delay between sends
                except:
                    pass

        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()

        names = "\n".join([f"• {c['name']} ({c['phone']})" for c in contacts])
        return {
            "action": "random_promo",
            "success": True,
            "result": f"📨 Promo dikirim ke {len(contacts)} pelanggan secara acak!\n\n{names}\n\nWhatsApp akan terbuka satu per satu.",
            "data": {"total": len(contacts), "contacts": contacts}
        }

    # ─── TIER PROMO ───────────────────────────────────────────────────
    def _cmd_tier_promo(self, cmd: str) -> Optional[dict]:
        """Send promo to customers of a specific tier."""
        # Determine which tier
        tier_map = {
            "reguler": "Reguler", "silver": "Silver", "gold": "Gold", "platinum": "Platinum",
            "semua": "all", "all": "all",
        }
        target_tier = "all"
        for keyword, tier in tier_map.items():
            if re.search(rf'\b{keyword}\b', cmd):
                target_tier = tier
                break

        customers = self.tools["loyalty"].customers
        if not customers:
            self.tools["loyalty"].add_sample_customers()
            customers = self.tools["loyalty"].customers

        # Filter by tier
        if target_tier == "all":
            selected = customers
        else:
            selected = [c for c in customers if c.get("Tier", "Reguler").lower() == target_tier.lower()]

        if not selected:
            return {"action": "tier_promo", "success": True,
                    "result": f"📭 Tidak ada pelanggan tier '{target_tier}'.", "data": {}}

        contacts = [{"name": c.get("Nama", ""), "phone": c.get("Telepon", "")}
                   for c in selected if c.get("Telepon", "")]

        if not contacts:
            return {"action": "tier_promo", "success": False,
                    "result": "❌ Tidak ada nomor telepon ditemukan.", "data": {}}

        from tools.whatsapp_bot import TIRE_TEMPLATES
        message = TIRE_TEMPLATES["promo"]

        # Add tier-specific perks
        tier_perks = {
            "Gold": "\n\n💎 Sebagai member Gold, Anda mendapat diskon EXTRA 5%!",
            "Platinum": "\n\n👑 Member Platinum! Anda mendapat diskon EXTRA 10% + gratis balancing!",
            "Silver": "\n\n⚪ Member Silver, dapatkan poin DOUBLE untuk pembelian hari ini!",
        }
        extra = tier_perks.get(target_tier, "")
        if extra:
            message += extra

        def send_thread():
            for c in contacts:
                personalized = message.replace("{name}", c["name"])
                try:
                    self.tools["whatsapp"].send_whatsapp(c["phone"], personalized)
                    time.sleep(5)
                except:
                    pass

        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()

        return {
            "action": "tier_promo",
            "success": True,
            "result": f"📨 Promo dikirim ke {len(contacts)} pelanggan tier '{target_tier}'!\n\nWhatsApp akan terbuka satu per satu.",
            "data": {"tier": target_tier, "total": len(contacts)}
        }

    # ─── AI AUTO-REPLY ───────────────────────────────────────────────
    def _cmd_ai_auto_reply(self, cmd: str) -> Optional[dict]:
        """Generate a smart AI auto-reply using Gemini."""
        # Extract the incoming message
        match = re.search(r'balas\s+(.+)|replies\s+(.+)|jawab\s+(.+)', cmd)
        incoming_message = None
        if match:
            incoming_message = match.group(1) or match.group(2) or match.group(3)

        if not incoming_message:
            # Maybe user is asking to enable auto-reply
            if any(k in cmd for k in ["aktifkan", "nyalakan", "enable", "on"]):
                return {
                    "action": "ai_auto_reply",
                    "success": True,
                    "result": "✅ Auto-reply cerdas siap!\n\n"
                              "Saat pelanggan chat WhatsApp Anda, gunakan AI Command Center "
                              "dan ketik 'balas [pesan pelanggan]' untuk dapatkan balasan pintar "
                              "yang cocok untuk toko ban Anda.",
                    "data": {}
                }
            return None

        # Use Groq to generate a smart reply
        reply = None
        if self.groq_configured:
            try:
                resp = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": "Anda adalah asisten toko ban Toko Ban Murah Anugerah. Balas pesan pelanggan dengan ramah, profesional, Bahasa Indonesia natural, maksimal 3 kalimat."},
                        {"role": "user", "content": f"Pesan pelanggan: {incoming_message}"},
                    ],
                    temperature=0.7,
                    max_tokens=200,
                )
                reply = resp.choices[0].message.content.strip()
            except Exception as e:
                print(f"[AI] Groq reply error: {e}")

        if not reply:
            # Fallback to template matching
            from tools.whatsapp_bot import TIRE_TEMPLATES
            reply = self.tools["whatsapp"].match_template(incoming_message)
            if not reply:
                reply = TIRE_TEMPLATES["halo"]

        return {
            "action": "ai_auto_reply",
            "success": True,
            "result": f"💬 *Balasan AI untuk:* \"{incoming_message}\"\n\n{reply}\n\n📋 Copy balasan di atas dan kirim ke pelanggan!",
            "data": {"incoming": incoming_message, "reply": reply}
        }

    # ─── SCHEDULER ────────────────────────────────────────────────────
    def _cmd_schedule_auto(self, cmd: str) -> Optional[dict]:
        """Schedule automatic promo sending."""
        if not _has_schedule:
            return {"action": "schedule", "success": False,
                    "result": "❌ Library 'schedule' belum terinstall.\nInstall: pip install schedule", "data": {}}

        # Parse time and interval
        time_match = re.search(r'(\d{1,2}):(\d{2})', cmd)
        interval = "daily"
        if "setiap" in cmd or "daily" in cmd or "harian" in cmd or "tiap" in cmd:
            interval = "daily"
        elif "minggu" in cmd or "weekly" in cmd:
            interval = "weekly"
        elif "jam" in cmd or "hour" in cmd:
            # Parse hours interval
            hour_match = re.search(r'(\d+)\s*jam', cmd)
            if hour_match:
                interval = f"every_{hour_match.group(1)}_hours"

        if not time_match:
            return {
                "action": "schedule",
                "success": False,
                "result": "❌ Format: 'jadwal promo setiap jam 10:00' atau 'jadwal promo tiap 3 jam'",
                "data": {}
            }

        hour = int(time_match.group(1))
        minute = int(time_match.group(2))

        # Check for duplicate
        for existing in self.scheduler_jobs:
            if existing["time"] == f"{hour:02d}:{minute:02d}" and existing["interval"] == interval:
                return {
                    "action": "schedule",
                    "success": True,
                    "result": f"⏰ Jadwal promo jam {hour:02d}:{minute:02d} ({interval_text}) sudah ada!",
                    "data": {"existing": True}
                }

        # Create schedule job
        job_id = f"promo_{hour:02d}{minute:02d}_{int(time.time())}"

        def promo_job():
            """The actual promo sending job."""
            customers = self.tools["loyalty"].customers
            if not customers:
                self.tools["loyalty"].add_sample_customers()
                customers = self.tools["loyalty"].customers

            contacts = [{"name": c.get("Nama", ""), "phone": c.get("Telepon", "")}
                       for c in customers if c.get("Telepon", "")]

            if contacts:
                from tools.whatsapp_bot import TIRE_TEMPLATES
                message = TIRE_TEMPLATES["promo"] + "\n\n📨 *Pesan otomatis dari Toko Ban Murah Anugerah*"
                self.tools["whatsapp"].bulk_send(contacts, message)

        # Schedule based on interval
        if interval == "daily":
            sched.every().day.at(f"{hour:02d}:{minute:02d}").do(promo_job)
        elif interval == "weekly":
            sched.every().monday.at(f"{hour:02d}:{minute:02d}").do(promo_job)
        elif interval.startswith("every_"):
            hours = int(interval.split("_")[1])
            sched.every(hours).hours.do(promo_job)

        self.scheduler_jobs.append({
            "id": job_id,
            "time": f"{hour:02d}:{minute:02d}",
            "interval": interval,
            "active": True
        })

        # Start scheduler if not running
        if not self.scheduler_running:
            self._start_scheduler()

        interval_text = {
            "daily": "setiap hari",
            "weekly": "setiap hari Senin",
        }.get(interval, interval)

        return {
            "action": "schedule",
            "success": True,
            "result": f"⏰ Promo otomatis DIJADWALKAN!\n\n"
                      f"• Waktu: {hour:02d}:{minute:02d}\n"
                      f"• Interval: {interval_text}\n"
                      f"• Akan dikirim ke semua pelanggan\n\n"
                      f"✅ Scheduler aktif! App harus tetap berjalan.",
            "data": {"job_id": job_id, "time": f"{hour:02d}:{minute:02d}", "interval": interval}
        }

    def _start_scheduler(self):
        """Start the background scheduler thread."""
        if not _has_schedule:
            return

        def run_scheduler():
            self.scheduler_running = True
            while self.scheduler_running:
                sched.run_pending()
                time.sleep(30)  # Check every 30 seconds

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """Stop the background scheduler."""
        self.scheduler_running = False

    def get_scheduler_status(self) -> dict:
        """Get scheduler status."""
        return {
            "running": self.scheduler_running,
            "jobs": self.scheduler_jobs,
            "total_jobs": len(self.scheduler_jobs)
        }

    # ─── SCHEDULE STATUS ────────────────────────────────────────────
    def _cmd_schedule_status(self, cmd: str) -> Optional[dict]:
        """Check active schedule status."""
        if any(k in cmd for k in ["cek jadwal", "lihat jadwal", "schedule status", "jadwal aktif", "daftar jadwal"]):
            status = self.get_scheduler_status()
            if not status["jobs"]:
                return {
                    "action": "schedule_status",
                    "success": True,
                    "result": "📅 Tidak ada jadwal promo otomatis yang aktif.\n\n"
                              "Ketik 'jadwal promo jam 10:00' untuk membuat jadwal baru!",
                    "data": status
                }

            lines = ["📅 *JADWAL PROMO AKTIF:*\n"]
            for job in status["jobs"]:
                if job["active"]:
                    interval_text = {
                        "daily": "setiap hari",
                        "weekly": "setiap Senin",
                    }.get(job["interval"], job["interval"])
                    lines.append(f"⏰ {job['time']} ({interval_text})")

            lines.append(f"\n✅ Scheduler: {'AKTIF' if status['running'] else 'MATI'}")
            return {
                "action": "schedule_status",
                "success": True,
                "result": "\n".join(lines),
                "data": status
            }
        return None

    # ─── CONVERSATION ─────────────────────────────────────────────────
    def get_conversation_log(self, limit: int = 10) -> list:
        """Get recent conversation history."""
        return self.conversation_log[-limit:]

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_log = []
        self.command_history = []
