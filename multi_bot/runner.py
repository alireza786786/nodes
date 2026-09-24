#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Master Multi-Bot Orchestrator & Ultimate Dynamic Hub + Telegram Sender
تولید خودکار جداول، فایل‌های سابسکریپشن و ارسال مستقیم بسته‌ها به کانال تلگرام با پنل گرافیکی
"""

import os
import sys
import json
import re
import base64
import requests
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

def load_sources_safely():
    src_data = os.environ.get("SOURCES_DATA", "").strip()
    if src_data:
        try: return json.loads(src_data)
        except Exception: pass
    for pf in ["sources.json", "multi_bot/sources.json"]:
        if os.path.exists(pf):
            try:
                with open(pf, "r", encoding="utf-8") as f: return json.load(f)
            except Exception: pass
    return {}

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

def send_to_telegram(file_path: str, caption: str):
    token = os.environ.get("BOT_TOKEN", "").strip()
    chat_id = os.environ.get("CHAT_ID", "").strip()
    if not token or not chat_id:
        print("⚠️ توکن بات یا چت آیدی تلگرام در Secrets گیت‌هاب تنظیم نشده است!")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
            r = requests.post(url, data=data, files=files, timeout=30)
            if r.status_code == 200:
                print(f"✅ فایل {file_path} با موفقیت به کانال تلگرام ارسال شد.")
            else:
                print(f"❌ خطا در ارسال به تلگرام: {r.text}")
    except Exception as e:
        print(f"❌ خطا در ارسال فایل به تلگرام: {e}")

def generate_hub_readmes(by_country, by_proto, total_nodes, date_str, time_str):
    sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]["nodes"]), reverse=True)
    country_rows = []
    for clean_name, data in sorted_countries:
        count = len(data["nodes"])
        flag = data["flag"]
        raw_name = data["name"]
        file_url = f"{REPO_RAW_BASE}/Country/{clean_name}.txt"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={file_url}"
        row = f"| {flag} {raw_name} | **{count}** | [📄 دریافت سابسکریپشن]({file_url}) | <img src=\"{qr_url}\" width=\"65\"/> |"
        country_rows.append(row)

    country_table_md = "\n".join(country_rows) if country_rows else "| 🌐 Global | **0** | - | - |"

    proto_rows = []
    for proto, nodes in by_proto.items():
        count = len(nodes)
        file_url = f"{REPO_RAW_BASE}/Config/{proto}.txt"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={file_url}"
        proto_rows.append(f"| **{proto.upper()}** | **{count}** | [📄 دریافت سابسکریپشن]({file_url}) | <img src=\"{qr_url}\" width=\"60\"/> |")
        
    proto_table_md = "\n".join(proto_rows) if proto_rows else "| - | **0** | - | - |"

    all_txt_url = f"{REPO_RAW_BASE}/all.txt"
    all_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={all_txt_url}"

    country_readme_content = f"""# 🌍 مرکز سرورهای کشوری (Countries Hub)
### تفکیک زنده بر اساس کشور، تعداد نودهای فعال و کدهای QR

| کشور (Country) | تعداد نودها (Nodes) | لینک مستقیم سابسکریپشن | اسکن بارکد (QR Code) |
| :--- | :---: | :---: | :---: |
{country_table_md}

---
> 🕒 آخرین بروزرسانی: {date_str} ساعت {time_str} به وقت تهران  
> 📢 کانال رسمی: [@Goodbaye_filtering]({CHANNEL_LINK}) | 💬 گروه: [@CONFIG_V2RAY_VIP]({CHAT_GROUP_LINK})
"""
    with open("Country/README.md", "w", encoding="utf-8") as f:
        f.write(country_readme_content)

    config_readme_content = f"""# 📁 مرکز پروتکل‌های اختصاصی (Protocols Hub)
### تفکیک زنده بر اساس نوع پروتکل، تعداد نودها و کدهای QR

| پروتکل (Protocol) | تعداد نودها (Nodes) | لینک مستقیم سابسکریپشن | اسکن بارکد (QR Code) |
| :--- | :---: | :---: | :---: |
{proto_table_md}

---
> 🕒 آخرین بروزرسانی: {date_str} ساعت {time_str} به وقت تهران  
> 📢 کانال رسمی: [@Goodbaye_filtering]({CHANNEL_LINK}) | 💬 گروه: [@CONFIG_V2RAY_VIP]({CHAT_GROUP_LINK})
"""
    with open("Config/README.md", "w", encoding="utf-8") as f:
        f.write(config_readme_content)

    root_readme_content = f"""<div align="center">

# 🛡️ NODES MASTER REPOSITORY
### مرجع جامع و خودکار توزیع سابسکریپشن‌های ضد فیلترینگ

![Nodes](https://img.shields.io/badge/Active%20Nodes-{total_nodes}%20Online-success?style=for-the-badge&logo=speedtest&logoColor=white)
![Updated](https://img.shields.io/badge/Updated-{time_str}%20Tehran-blue?style=for-the-badge&logo=clock&logoColor=white)

---

### 📱 کانال رسمی و پشتیبانی تلگرام

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

| کشور (Country) | تعداد نودها (Nodes) | لینک سابسکریپشن | اسکن بارکد (QR Code) |
| :--- | :---: | :---: | :---: |
{country_table_md}

---

## ⚡ تفکیک بر اساس پروتکل‌ها (By Protocol)

| پروتکل (Protocol) | تعداد نودها (Nodes) | لینک سابسکریپشن | اسکن بارکد (QR Code) |
| :--- | :---: | :---: | :---: |
{proto_table_md}

---

## 📦 آرشیو جامع تمام {total_nodes} سرور یکجا
* 📄 **[دانلود مستقیم تمام کانفیگ‌ها (all.txt)]({all_txt_url})**
* 📱 **اسکن کل آرشیو یکجا با بارکد QR:**
<br>
<img src="{all_qr_url}" width="120"/>

---

<div align="center">
  <sub>🕒 آخرین به‌روزرسانی: {date_str} ساعت {time_str} به وقت تهران</sub>
</div>
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(root_readme_content)
    print("🌟 تمام جداول پویا با تعداد دقیق نودها و کدهای QR بازنویسی شدند.")

def main():
    print("🚀 [RUNNER] شروع پردازش سراسری بر اساس سورس‌های معتبر...")
    date_str, time_str = get_tehran_time()

    sources_data = load_sources_safely()
    if not sources_data:
        print("❌ هیچ منبعی در دسترس نیست.")
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

            # 📮 متن گرافیکی و شیک برای ارسال به کانال تلگرام
            sub_url = f"{REPO_RAW_BASE}/Subscription/plain/{key}.txt"
            caption = (
                f"╔═══════════════════════╗\n"
                f"  🛡️ <b>بسته سابسکریپشن اختصاصی #{key.upper()}</b>\n"
                f"╚═══════════════════════╝\n\n"
                f"⚡ <b>وضعیت اتصال:</b> تست شده و فوق‌العاده پرسرعت\n"
                f"📡 <b>تعداد نودهای زنده:</b> <code>{len(valid_nodes)}</code> سرور\n\n"
                f"🔗 <b>لینک مستقیم فایل سابسکریپشن:</b>\n"
                f"👉 <a href='{sub_url}'>کلیک برای دریافت فایل خام</a>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📢 <b>کانال رسمی:</b> <a href='{CHANNEL_LINK}'>@Goodbaye_filtering</a>\n"
                f"💬 <b>گروه تبادل:</b> <a href='{CHAT_GROUP_LINK}'>@CONFIG_V2RAY_VIP</a>"
            )
            send_to_telegram(out_plain, caption)

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

    by_proto = {}
    by_trans = {}
    by_country = {}

    for node in all_plain_configs:
        p = extract_protocol(node)
        by_proto.setdefault(p, []).append(node)

        t = extract_transport(node)
        if t != "other": by_trans.setdefault(t, []).append(node)

        flag, raw_country, clean_c = extract_country_info(node)
        if clean_c not in ["Global", "Other", "Unknown"]:
            by_country.setdefault(clean_c, {"flag": flag, "name": raw_country, "nodes": []})["nodes"].append(node)

    for proto, nodes in by_proto.items():
        fname = f"Config/{proto}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")
        print(f"📁 فایل Config/{proto}.txt ذخیره شد ({len(nodes)} نود).")

    for trans, nodes in by_trans.items():
        fname = f"transports/{trans}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")

    for clean_c, data in by_country.items():
        fname = f"Country/{clean_c}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(data["nodes"]) + "\n")
        print(f"📁 فایل Country/{clean_c}.txt ذخیره شد ({len(data['nodes'])} نود).")

    with open("all.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_plain_configs) + "\n")

    b64_all = base64.b64encode("\n".join(all_plain_configs).encode("utf-8")).decode("utf-8")
    with open("all_b64.txt", "w", encoding="utf-8") as f:
        f.write(b64_all)

    generate_hub_readmes(by_country, by_proto, total_unique, date_str, time_str)
    print("✅ تمام جداول زنده با نودها و کدهای QR در README اصلی و پوشه‌ها ساخته شدند.")

if __name__ == "__main__":
    main()
