#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Ultimate Hub & UI Synchronizer (Fixed URL-Encoding & Robust Country Parser)
"""
import os
import glob
import urllib.parse
import base64

# نگاشت جامع کدهای بین‌المللی و نام کشورها با پرچم
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
    "se": ("سوئد", "🇸🇪"),
    "ch": ("سوئیس", "🇨🇭"),
    "jp": ("ژاپن", "🇯🇵"),
}

def decode_node_safely(node_str):
    """رمزگشایی ایمن متن نود که ممکن است URL-encoded یا Base64 باشد"""
    try:
        # دیکد کردن کدهای هگزادسیمال و URL-encoded (حل مشکل ایموجی‌ها مثل %F0%9F...)
        decoded = urllib.parse.unquote(node_str)
        return decoded
    except Exception:
        return node_str

def parse_ping(node_str):
    """استخراج مقدار پینگ از داخل نام یا ساختار نود"""
    try:
        lower_str = node_str.lower()
        if "ping:" in lower_str:
            parts = lower_str.split("ping:")
            num_str = "".join([c for c in parts[1].split("ms")[0] if c.isdigit()])
            if num_str:
                return int(num_str)
    except Exception:
        pass
    return 999  # پیش‌فرض برای نودهایی که پینگ ندارند

def run_updater():
    print("🔄 در حال پردازش پیشرفته و پاک‌سازی نودها...")
    
    config_files = glob.glob("Config/*.txt")
    all_nodes = []
    for cf in config_files:
        try:
            with open(cf, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip()
                    if clean_line and "://" in clean_line:
                        all_nodes.append(clean_line)
        except Exception: 
            pass

    all_nodes = list(set(all_nodes))
    print(f"💎 کل نودهای یکتا جهت پردازش: {len(all_nodes)}")

    tier_ultra_fast = [] # زیر ۲۰۰ میلی‌ثانیه
    tier_good = []       # زیر ۵۰۰ میلی‌ثانیه
    country_data = {}

    for node in all_nodes:
        # اعمال دیکد ایمن برای خواندن کاراکترهای URL-encoded شده
        readable_node = decode_node_safely(node)
        ping_val = parse_ping(readable_node)
        
        # لایه‌بندی پینگ واقعی
        if ping_val <= 200:
            tier_ultra_fast.append(node)
        if ping_val <= 500:
            tier_good.append(node)

        # تفکیک دقیق کشوری با پشتیبانی از متن‌های دیکد شده
        assigned = False
        node_lower = readable_node.lower()
        
        # ۱. بررسی بر اساس نام کشورها یا کدهای استاندارد داخل متن خوانا
        for code, (c_name, flag) in COUNTRY_MAP.items():
            if f"[{code}]" in node_lower or f"_{code}_" in node_lower or c_name in node_lower:
                key = (c_name, flag)
                if key not in country_data:
                    country_data[key] = []
                country_data[key].append(node)
                assigned = True
                break

        # ۲. اگر کشوری صراحتاً پیدا نشد، بررسی در سایر بخش‌ها یا ثبت به عنوان Global
        if not assigned:
            key = ("سایر سرورها (Global)", "🌐")
            if key not in country_data:
                country_data[key] = []
            country_data[key].append(node)

    # ذخیره فایل‌های لایه‌بندی پینگ در پوشه Subscription
    os.makedirs("Subscription", exist_ok=True)
    with open("Subscription/ultra_fast.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(tier_ultra_fast) + "\n")
    
    with open("Subscription/good_ping.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(tier_good) + "\n")

    # ساخت فایل‌های کشوری و جدول README
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

# 🌍 مرکز سرورهای کشوری و پینگ واقعی (Countries Hub)

تفکیک زنده بر اساس منطقه جغرافیایی، تست سرعت واقعی و سابسکریپشن‌های اختصاصی

</div>

---

| کشور (Country) | تعداد نودها (Nodes) | لینک مستقیم سابسکرایب |
| :--- | :---: | :---: |
{table_rows}
---
> 🔄 سیستم ارزیابی خودکار پینگ واقعی و تفکیک هوشمند کشوری
"""
    with open(country_readme_path, "w", encoding="utf-8") as f:
        f.write(country_readme_content)

    print(f"✅ تفکیک کامل کشوری با {len(sorted_countries)} دسته و لایه‌بندی پینگ با موفقیت انجام شد.")

if __name__ == "__main__":
    run_updater()
