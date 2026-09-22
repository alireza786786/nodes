#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Master Multi-Bot Orchestrator & Dynamic README Generator
ساخت خودکار تمام پوشه‌ها، پر کردن VLESS/VMess و تولید زنده جدول کشورها و QR کدها
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

REPO_RAW_BASE = "https://raw.githubusercontent.com/alireza786786/nodes/main"
CHANNEL_LINK = "https://t.me/Goodbaye_filtering"
CHAT_GROUP_LINK = "https://t.me/CONFIG_V2RAY_VIP"

def get_tehran_time():
    tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

def extract_country_info(line: str):
    m = re.search(r'📡(.*?)®️([^©️#\n\r]+)©️', line)
    if m:
        flag = m.group(1).strip()
        country = m.group(2).strip()
        if country and country.lower() != "unknown":
            clean_c = re.sub(r'[^\w\s-]', '', country).strip().replace(" ", "_")
            return flag, country, clean_c
    return "🌐", "Global", "Global"

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

def generate_dynamic_readme(by_country, by_proto, total_nodes, date_str, time_str):
    """تولید کاملاً خودکار جدول صفحه اول دقیقاً مطابق عکس ارسالی شما با بارکدها و تعداد زنده"""
    
    # مرتب‌سازی کشورها بر اساس بیشترین تعداد سرور
    sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]["nodes"]), reverse=True)
    
    country_rows = []
    for clean_name, data in sorted_countries:
        count = len(data["nodes"])
        flag = data["flag"]
        raw_name = data["name"]
        file_url = f"{REPO_RAW_BASE}/Country/{clean_name}.txt"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={file_url}"
        
        row = f"""| {flag} {raw_name} | **{count}** | [📄 دانلود کانفیگ‌ها]({file_url}) | <img src="{qr_url}" width="65"/> |"""
        country_rows.append(row)

    country_table_md = "\n".join(country_rows)

    # جدول پروتکل‌ها
    proto_rows = []
    for proto, nodes in by_proto.items():
        count = len(nodes)
        file_url = f"{REPO_RAW_BASE}/Config/{proto}.txt"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={file_url}"
        proto_rows.append(f"| **{proto.upper()}** | **{count}** | [📄 دانلود سابسکریپشن]({file_url}) | <img src=\"{qr_url}\" width=\"60\"/> |")
    proto_table_md = "\n".join(proto_rows)

    all_txt_url = f"{REPO_RAW_BASE}/all.txt"
    all_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={all_txt_url}"

    readme_content = f"""<div align="center">

# 🛡️ NODES HYPER-HUB (V2Ray / Xray Master Hub)
### مرجع رسمی توزیع، پالایش و سابسکریپشن ضد فیلترینگ

![Nodes](https://img.shields.io/badge/Active%20Nodes-{total_nodes}%20Online-success?style=for-the-badge&logo=speedtest&logoColor=white)
![Updated](https://img.shields.io/badge/Updated-{time_str}%20Tehran-blue?style=for-the-badge&logo=clock&logoColor=white)

---

### 📱 کانال رسمی و اتصال مستقیم تلگرام

<table>
  <tr>
    <td align="center" width="50%">
      <b>📢 کانال رسمی تلگرام</b><br>
      <a href="{CHANNEL_LINK}">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={CHANNEL_LINK}" width="130"/>
      </a><br>
      <a href="{CHANNEL_LINK}">👉 @Goodbaye_filtering</a>
    </td>
    <td align="center" width="50%">
      <b>💬 گروه گفتگو و تبادل</b><br>
      <a href="{CHAT_GROUP_LINK}">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={CHAT_GROUP_LINK}" width="130"/>
      </a><br>
      <a href="{CHAT_GROUP_LINK}">👉 @CONFIG_V2RAY_VIP</a>
    </td>
  </tr>
</table>

</div>

---

## 🌐 تفکیک بر اساس کشورها (By Country)
> در این جدول، سرورها بر اساس کشور مرتب شده‌اند و هر ردیف دارای **تعداد نودهای زنده**، **لینک مستقیم** و **کد QR اختصاصی** است:

| کشور (Country) | تعداد نودها (Nodes) | لینک مستقیم سابسکریپشن | اسکن بارکد (QR Code) |
| :--- | :---: | :---: | :---: |
{country_table_md}

---

## ⚡ تفکیک بر اساس پروتکل‌ها (By Protocol)

| پروتکل (Protocol) | تعداد نودها (Nodes) | لینک مستقیم سابسکریپشن | اسکن بارکد (QR Code) |
| :--- | :---: | :---: | :---: |
{proto_table_md}

---

## 📦 آرشیو جامع تمام {total_nodes} سرور یکجا
* 📄 **[دانلود مستقیم تمام کانفیگ‌ها (all.txt)]({all_txt_url})**
* 📱 **کد QR برای اسکن کل آرشیو یکجا:**
<br>
<img src="{all_qr_url}" width="120"/>

---

<div align="center">
  <sub>🕒 آخرین بروزرسانی: {date_str} ساعت {time_str} به وقت تهران</sub><br>
  <sub>کانال رسمی: <b>@Goodbaye_filtering</b> | گروه تبادل: <b>@CONFIG_V2RAY_VIP</b></sub>
</div>
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("🌟 فایل README.md با جدول‌های پویا و بارکدهای QR با موفقیت بازنویسی شد!")

def main():
    print("🚀 [ORCHESTRATOR] شروع پردازش نهایی و تولید هاب زنده...")
    date_str, time_str = get_tehran_time()

    with open("sources.json", "r", encoding="utf-8") as f:
        sources_data = json.load(f)

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
    print(f"\n🎯 مجموع کل کانفیگ‌های تاییدشده: {total_unique}")
    if not all_plain_configs: return

    by_proto = {}
    by_trans = {}
    by_country = {}

    for node in all_plain_configs:
        p = extract_protocol(node)
        by_proto.setdefault(p, []).append(node)

        t = extract_transport(node)
        if t != "other": by_trans.setdefault(t, []).append(node)

        flag, raw_country, clean_c = extract_country_info(node)
        if clean_c != "Global" and clean_c != "Other":
            by_country.setdefault(clean_c, {"flag": flag, "name": raw_country, "nodes": []})["nodes"].append(node)

    # نوشتن فایل‌های Config/ (شامل vless و vmess و بقیه)
    for proto, nodes in by_proto.items():
        fname = f"Config/{proto}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")
        print(f"📁 فایل Config/{proto}.txt با {len(nodes)} نود ایجاد شد.")

    # نوشتن فایل‌های transports/
    for trans, nodes in by_trans.items():
        fname = f"transports/{trans}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")

    # نوشتن فایل‌های Country/
    for clean_c, data in by_country.items():
        fname = f"Country/{clean_c}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(data["nodes"]) + "\n")

    # ذخیره فایل آرشیو کل
    with open("all.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_plain_configs) + "\n")

    b64_all = base64.b64encode("\n".join(all_plain_configs).encode("utf-8")).decode("utf-8")
    with open("all_b64.txt", "w", encoding="utf-8") as f:
        f.write(b64_all)

    # تولید جادویی صفحه README.md زنده
    generate_dynamic_readme(by_country, by_proto, total_unique, date_str, time_str)
    print("✅ تمام پوشه‌ها پر شدند و صفحه اصلی با بارکدها و جدول‌های زنده ساخته شد.")

if __name__ == "__main__":
    main()
