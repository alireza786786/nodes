#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Master Multi-Bot Orchestrator & Hub Splitter (Zero-Hardcoded Sources)
منابع ۱۰۰٪ مخفی و خوانده‌شده از سکرت SOURCES_DATA
بدون وجود حتی یک لینک در متن کدها
"""

import os
import sys
import json
import re
import base64
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("multi_bot"))
sys.path.append(os.path.abspath("Proxy_collector"))

import engine as core_engine

CHANNEL_LINK = "https://t.me/Goodbaye_filtering"
CHAT_GROUP_LINK = "https://t.me/CONFIG_V2RAY_VIP"

def load_sources_from_vault():
    """خواندن ۱۰۰٪ مخفی منابع از گاوصندوق سکرت گیت‌هاب"""
    data_str = os.environ.get("SOURCES_DATA", "").strip()
    if data_str:
        try:
            return json.loads(data_str)
        except Exception as e:
            print(f"❌ خطای دیکود منابع: {e}")
    # پشتیبان لوکال برای ترموکس
    cfg_p = os.path.expanduser("~/.sources.json")
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: pass
    return {}

def get_tehran_time():
    tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

def extract_country(line: str) -> str:
    m = re.search(r'®️([^©️#\n\r]+)©️', line)
    if m:
        c = m.group(1).strip()
        if c and c.lower() != "unknown":
            clean = re.sub(r'[^\w\s-]', '', c).strip().replace(" ", "_")
            return clean if clean else "Other"
    return "Other"

def extract_protocol(line: str) -> str:
    scheme = line.split("://")[0].lower().strip()
    if scheme in ["hysteria2", "hy2"]: return "hysteria2"
    if scheme in ["socks", "socks5"]: return "socks"
    if scheme in ["vless", "vmess", "trojan", "ss"]: return scheme
    return "other"

def extract_transport(line: str) -> str:
    lower = line.lower()
    if "type=xhttp" in lower or "xhttp-elite" in lower: return "xhttp"
    if "type=grpc" in lower or "servicename=" in lower or "reality-grpc" in lower: return "grpc"
    if "type=ws" in lower or "ws-tls" in lower or "cf-worker" in lower: return "ws"
    if "type=tcp" in lower or "reality-vision" in lower: return "tcp"
    return "other"

def build_header(cat_title: str, count: int, date_str: str, time_str: str) -> str:
    return (
        f"# ═══════════════════════════════════════════════════════\n"
        f"# ✨ Goodbaye Filtering Hub — {cat_title.upper()}\n"
        f"# 📊 تعداد کانفیگ‌های تست‌شده: {count}\n"
        f"# 📅 تاریخ میلادی: {date_str} | 🕒 ساعت: {time_str} (تهران)\n"
        f"# 📢 کانال: {CHANNEL_LINK}\n"
        f"# 💬 گروه: {CHAT_GROUP_LINK}\n"
        f"# ═══════════════════════════════════════════════════════\n"
    )

def main():
    print("🚀 [ORCHESTRATOR] شروع پردازش ایمن با منابع مخفی...")
    date_str, time_str = get_tehran_time()

    sources_data = load_sources_from_vault()
    if not sources_data:
        print("❌ خطا: هیچ منبعی در سکرت SOURCES_DATA پیدا نشد.")
        return

    os.makedirs("Subscription/plain", exist_ok=True)
    os.makedirs("Subscription/base64", exist_ok=True)
    os.makedirs("Config", exist_ok=True)
    os.makedirs("Country", exist_ok=True)
    os.makedirs("transports", exist_ok=True)

    all_plain_configs = []
    seen_bases = set()

    for i in range(1, 8):
        key = f"guard{i}"
        srcs = sources_data.get(key, [])
        if not srcs: continue
        out_plain = f"Subscription/plain/{key}.txt"
        out_b64 = f"Subscription/base64/{key}.txt"

        print(f"\n⚡ پردازش بسته {key}...")
        valid_nodes = core_engine.run_engine_core(key, tuple(srcs), out_plain)

        if valid_nodes:
            b64_str = base64.b64encode("\n".join(valid_nodes).encode("utf-8")).decode("utf-8")
            with open(out_b64, "w", encoding="utf-8") as bf:
                bf.write(b64_str)

            for line in valid_nodes:
                base = line.split("#")[0]
                if base not in seen_bases:
                    seen_bases.add(base)
                    all_plain_configs.append(line)

    try:
        print("\n⚡ پردازش بسته guard8 (پروکسی تلگرام)...")
        os.environ["PROXY_SOURCES"] = "\n".join(sources_data.get("guard8", []))
        import collector as proxy_module
        import asyncio
        asyncio.run(proxy_module.main())
    except Exception as e:
        print(f"⚠️ اجرا بسته ۸: {e}")

    total_unique = len(all_plain_configs)
    print(f"\n🎯 مجموع کل کانفیگ‌های یکتای استخراج‌شده: {total_unique}")
    if not all_plain_configs:
        return

    by_proto, by_trans, by_country = {}, {}, {}
    for node in all_plain_configs:
        p = extract_protocol(node)
        by_proto.setdefault(p, []).append(node)

        t = extract_transport(node)
        if t != "other": by_trans.setdefault(t, []).append(node)

        c = extract_country(node)
        by_country.setdefault(c, []).append(node)

    for proto, nodes in by_proto.items():
        fname = f"Config/{proto}.txt"
        header = build_header(f"Protocol: {proto}", len(nodes), date_str, time_str)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(nodes) + "\n")

    for trans, nodes in by_trans.items():
        fname = f"transports/{trans}.txt"
        header = build_header(f"Transport: {trans}", len(nodes), date_str, time_str)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(nodes) + "\n")

    for country, nodes in by_country.items():
        if country == "Other": continue
        fname = f"Country/{country}.txt"
        header = build_header(f"Country: {country}", len(nodes), date_str, time_str)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(nodes) + "\n")

    header_all = build_header("All Confirmed Nodes", total_unique, date_str, time_str)
    with open("all.txt", "w", encoding="utf-8") as f:
        f.write(header_all + "\n".join(all_plain_configs) + "\n")

    b64_all = base64.b64encode("\n".join(all_plain_configs).encode("utf-8")).decode("utf-8")
    with open("all_b64.txt", "w", encoding="utf-8") as f:
        f.write(b64_all)

    print("✅ تمام پوشه‌ها (Config, Country, transports, Subscription) با موفقیت پر شدند.")

if __name__ == "__main__":
    main()
