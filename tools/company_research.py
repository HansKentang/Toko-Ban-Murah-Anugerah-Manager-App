"""
Company Research Agent - Toko Ban Murah Anugerah
================================================
Uses Serper API for web search + Gemini for synthesis
to produce comprehensive company research reports.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional

try:
    from groq import Groq
    _has_groq = True
except ImportError:
    _has_groq = False


SERPER_URL = "https://google.serper.dev/search"


def _serper_search(query: str, api_key: str) -> Optional[dict]:
    """Search the web via Serper API."""
    if not api_key:
        return None
    payload = json.dumps({"q": query, "num": 8}).encode("utf-8")
    req = urllib.request.Request(
        SERPER_URL,
        data=payload,
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[CompanyResearch] Serper error: {e}")
        return None


def _extract_text_from_results(data: dict) -> str:
    """Extract readable text from Serper results."""
    parts = []
    if data.get("knowledgeGraph"):
        kg = data["knowledgeGraph"]
        title = kg.get("title", "")
        desc = kg.get("description", "")
        if title:
            parts.append(f"=== Knowledge Graph ===\nTitle: {title}")
        if desc:
            parts.append(f"Description: {desc}")
        if kg.get("attributes"):
            for k, v in kg["attributes"].items():
                parts.append(f"{k}: {v}")

    if data.get("organic"):
        parts.append("\n=== Search Results ===")
        for i, r in enumerate(data["organic"][:6], 1):
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            parts.append(f"{i}. {title}\n   {snippet}\n   {link}")

    if data.get("topStories"):
        parts.append("\n=== Top Stories ===")
        for s in data["topStories"][:3]:
            parts.append(f"- {s.get('title', '')} ({s.get('source', '')})")

    return "\n\n".join(parts)


def _synthesize_report(company: str, search_text: str, client, model: str) -> str:
    """Use Groq to turn raw search text into a structured report."""
    prompt = f"""You are a professional business researcher. Based on the web search data below about "{company}", generate a comprehensive company research report in Bahasa Indonesia.

Research Report Structure:
1. **Overview** — What the company does, its market position, headquarters
2. **Business Performance** — Key metrics, revenue indicators, growth signals
3. **Ideal Customer Profile (ICP)** — Who their target customers are
4. **Market Trends** — Industry trends affecting this company
5. **Challenges** — Key challenges the company faces
6. **Actionable Strategies** — Recommendations for competing or partnering

Web Search Data:
{search_text}

Return ONLY the report in clean markdown format.
"""
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[CompanyResearch] Groq synthesis error: {e}")
        return None


def research_company(
    company: str,
    serper_api_key: str,
    groq_api_key: str,
) -> dict:
    """
    Research a company by name/domain.
    Returns: { "success": bool, "result": str, "data": {...} }
    """
    # 1. Search the web
    search_data = _serper_search(f"{company} company profile overview", serper_api_key)
    if not search_data:
        return {
            "success": False,
            "result": "Gagal mencari data perusahaan. Periksa SERPER_API_KEY.",
            "data": {},
        }

    search_text = _extract_text_from_results(search_data)

    # 2. Also search for news
    news_data = _serper_search(f"{company} latest news 2026", serper_api_key)
    if news_data:
        news_text = _extract_text_from_results(news_data)
        search_text += f"\n\n=== News ===\n{news_text}"

    # 3. Synthesize with Groq
    report = None
    if _has_groq and groq_api_key:
        try:
            client = Groq(api_key=groq_api_key)
            report = _synthesize_report(company, search_text, client, "llama-3.3-70b-versatile")
            if not report:
                report = _synthesize_report(company, search_text, client, "llama-3.3-70b-versatile")
        except Exception as e:
            print(f"[CompanyResearch] Groq init error: {e}")

    if not report:
        # Fallback: return raw search data formatted
        report = f"🔍 *Hasil Pencarian untuk: {company}*\n\n{search_text[:2000]}"

    return {
        "success": True,
        "result": f"🔬 *Company Research: {company}*\n\n{report}",
        "data": {
            "company": company,
            "raw_search": search_text[:500],
            "report_length": len(report),
        },
    }
