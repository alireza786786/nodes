#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Master Multi-Bot Orchestrator & Hub Splitter
اجرای خودکار بسته‌های guard1 تا guard8 بر اساس sources.json
پر کردن پوشه‌های Subscription, Config, Country, transports و فایل all.txt
"""

import os
import sys
import json
import re
import base64
from datetime import datetime, timezone, timedelta

# اضافه کردن مسیر پوشه‌ها به سیستم
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("multi_bot"))
sys.path.append(os.path.abspath("Proxy_collector"))

import engine as core_engine

SOURCES_FILE = "sources.json"
CHANNEL_LINK = "https://t.me/Goodbaye_filtering"
CHAT_GROUP_LINK = "https://t.me/CONFIG_V2RAY_VIP"

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
    print("🚀 [ORCHESTRATOR] شروع پردازش سراسری بسته‌های guard...")
    date_str, time_str = get_tehran_time()

    if not os.path.exists(SOURCES_FILE):
        print(f"❌ فایل منابع {SOURCES_FILE} یافت نشد.")
        return

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        sources_data = json.load(f)

    # ساخت زیرساخت پوشه‌ها
    os.makedirs("Subscription/plain", exist_ok=True)
    os.makedirs("Subscription/base64", exist_ok=True)
    os.makedirs("Config", exist_ok=True)
    os.makedirs("Country", exist_ok=True)
    os.makedirs("transports", exist_ok=True)

    all_plain_configs = []
    seen_bases = set()

    # اجرای بسته‌های ۱ تا ۷
    for i in range(1, 8):
        key = f"guard{i}"
        srcs = sources_data.get(key, [])
        if not srcs:
            continue
        out_plain = f"Subscription/plain/{key}.txt"
        out_b64 = f"Subscription/base64/{key}.txt"

        print(f"\n⚡ پردازش بسته {key}...")
        valid_nodes = core_engine.run_engine_core(key, tuple(srcs), out_plain)

        # ساخت فایل Base64 همان بسته
        if valid_nodes:
            b64_str = base64.b64encode("\n".join(valid_nodes).encode("utf-8")).decode("utf-8")
            with open(out_b64, "w", encoding="utf-8") as bf:
                bf.write(b64_str)

            for line in valid_nodes:
                base = line.split("#")[0]
                if base not in seen_bases:
                    seen_bases.add(base)
                    all_plain_configs.append(line)

    # اجرای بسته ۸ (پروکسی‌های تلگرام)
    try:
        print("\n⚡ پردازش بسته guard8 (پروکسی تلگرام)...")
        import collector as proxy_module
        import asyncio
        asyncio.run(proxy_module.main())
    except Exception as e:
        print(f"⚠️ خطا در اجرای بسته ۸: {e}")

    total_unique = len(all_plain_configs)
    print(f"\n🎯 مجموع کل کانفیگ‌های یکتای استخراج‌شده: {total_unique}")
    if not all_plain_configs:
        return

    # دسته‌بندی در پوشه Config (پروتکل‌ها)
    by_proto = {}
    by_trans = {}
    by_country = {}

    for node in all_plain_configs:
        p = extract_protocol(node)
        by_proto.setdefault(p, []).append(node)

        t = extract_transport(node)
        if t != "other":
            by_trans.setdefault(t, []).append(node)

        c = extract_country(node)
        by_country.setdefault(c, []).append(node)

    # نگارش فایل‌های Config/
    for proto, nodes in by_proto.items():
        fname = f"Config/{proto}.txt"
        header = build_header(f"Protocol: {proto}", len(nodes), date_str, time_str)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(nodes) + "\n")

    # نگارش فایل‌های transports/
    for trans, nodes in by_trans.items():
        fname = f"transports/{trans}.txt"
        header = build_header(f"Transport: {trans}", len(nodes), date_str, time_str)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(nodes) + "\n")

    # نگارش فایل‌های Country/
    for country, nodes in by_country.items():
        if country == "Other": continue
        fname = f"Country/{country}.txt"
        header = build_header(f"Country: {country}", len(nodes), date_str, time_str)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(nodes) + "\n")

    # نگارش فایل آرشیو جامع ریشه all.txt
    header_all = build_header("All Confirmed Nodes", total_unique, date_str, time_str)
    with open("all.txt", "w", encoding="utf-8") as f:
        f.write(header_all + "\n".join(all_plain_configs) + "\n")

    # نسخه Base64 جامع
    b64_all = base64.b64encode("\n".join(all_plain_configs).encode("utf-8")).decode("utf-8")
    with open("all_b64.txt", "w", encoding="utf-8") as f:
        f.write(b64_all)

    print("✅ تمام پوشه‌های Config، Country، transports و Subscription با موفقیت پر شدند.")

if __name__ == "__main__":
    main()
