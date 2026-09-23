#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Robust Country & Hub Synchronizer
"""
import os
import glob
import re

# نگاشت ساده کدهای دو حرفی به نام کامل و پرچم کشورها
COUNTRY_MAP = {
    "de": ("آلمان", "🇩🇪"),
    "nl": ("هلند", "🇳🇱"),
    "us": ("آمریكا", "🇺🇸"),
    "tr": ("ترکیه", "🇹🇷"),
    "gb": ("انگلستان", "🇬🇧"),
    "fr": ("فرانسه", "🇫🇷"),
    "ca": ("کانادا", "🇨🇦"),
    "ir": ("ایران", "🇮🇷"),
    "fi": ("فنلاند", "🇫🇮"),
    "ru": ("روسیه", "🇷🇺"),
    "ae": ("امارات", "🇦🇪"),
    "sg": ("سنگاپور", "🇸🇬"),
}

def run_updater():
    print("🔄 در حال پردازش پیشرفته نودها و تفکیک کشوری...")
    
    config_files = glob.glob("Config/*.txt")
    all_nodes = []
    for cf in config_files:
        try:
            with open(cf, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and "://" in line]
                all_nodes.extend(lines)
        except Exception: 
            pass

    all_nodes = list(set(all_nodes))
    print(f"💎 تعداد کل نودهای یکتا: {len(all_nodes)}")

    country_data = {}
    
    # تفکیک نودها بر اساس شناسایی نام یا کد کشور
    for node in all_nodes:
        assigned = False
        node_lower = node.lower()
        
        # روش اول: جستجوی نام یا کد کشور در متن نود
        for code, (c_name, flag) in COUNTRY_MAP.items():
            # بررسی کدهای استاندارد یا نام کشور در متن
            if f"[{code}]" in node_lower or f"_{code}_" in node_lower or c_name in node:
                key = (c_name, flag)
                if key not in country_data:
                    country_data[key] = []
                country_data[key].append(node)
                assigned = True
                break
        
        # اگر کشوری پیدا نشد، به عنوان Global (سایر سرورها) در نظر گرفته شود
        if not assigned:
            key = ("سایر سرورها (Global)", "🌐")
            if key not in country_data:
                country_data[key] = []
            country_data[key].append(node)

    country_dir = "Country"
    os.makedirs(country_dir, exist_ok=True)
    
    table_rows = ""
    sorted_countries = sorted(country_data.items(), key=lambda x: len(x[1]), reverse=True)

    for (c_name, flag), nodes in sorted_countries:
        count = len(nodes)
        cc_code = "".join([c for c in c_name if c.isalnum()]).lower() or "global"
        file_name = f"{cc_code}.txt"
        file_path = os.path.join(country_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")
            
        sub_link = f"./{file_name}"
        table_rows += f"| {flag} {c_name} | {count} | [سابسکرایب]({sub_link}) |\n"

    # آپدیت فایل README.md در پوشه Country
    country_readme_path = os.path.join(country_dir, "README.md")
    country_readme_content = f"""<div align="center">

# 🌍 مرکز سرورهای کشوری (Countries Hub)

تفکیک زنده بر اساس کشور، تعداد نودهای فعال و سابسکریپشن‌های اختصاصی

</div>

---

| کشور (Country) | تعداد نودها (Nodes) | لینک مستقیم سابسکرایب |
| :--- | :---: | :---: |
{table_rows}
---
> 🔄 آخرین بروزرسانی خودکار هوشمند گیت‌هاب اکشن
"""
    with open(country_readme_path, "w", encoding="utf-8") as f:
        f.write(country_readme_content)

    print(f"✅ تفکیک کشوری با موفقیت انجام شد. تعداد {len(sorted_countries)} دسته ثبت شد.")

if __name__ == "__main__":
    run_updater()
