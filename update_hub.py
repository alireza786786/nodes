#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 اسکریپت خودکار به‌روزرسانی جدول‌ها و دسته‌بندی کشوری
"""
import os, glob

def update_readme_and_countries():
    print("🔄 در حال به‌روزرسانی رابط کاربری و جدول‌های README...")
    
    # 1. خواندن و تفکیک نودها بر اساس کشور از فایل‌های Config
    config_files = glob.glob("Config/*.txt")
    all_nodes = []
    for cf in config_files:
        try:
            with open(cf, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and "://" in line]
                all_nodes.extend(lines)
        except Exception: pass

    country_data = {}
    for node in all_nodes:
        # استخراج پرچم یا نام کشور از نام نود (بر اساس ساختار برندینگ شما)
        if "®️" in node and "©️" in node:
            try:
                parts = node.split("®️")[1].split("©️")
                country_name = parts[0].strip()
                # پیدا کردن پرچم قبل از نام کشور
                flag_part = node.split("📡")[1].split("®️")[0] if "📡" in node else "🌐"
                cc = country_name[:2].lower() # پیش‌فرض کوتاه
                
                key = (country_name, flag_part)
                if key not in country_data:
                    country_data[key] = []
                country_data[key].append(node)
            except Exception: pass

    # 2. ذخیره فایل‌های کشوری در پوشه Country
    country_dir = "Country"
    os.makedirs(country_dir, exist_ok=True)
    
    table_rows = ""
    for (c_name, flag), nodes in country_data.items():
        count = len(nodes)
        cc_code = c_name.lower().replace(" ", "_")
        file_name = f"{cc_code}.txt"
        file_path = os.path.join(country_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")
            
        sub_link = f"./Country/{file_name}"
        table_rows += f"| {flag} {c_name} | {count} | [سابسکرایب]({sub_link}) |\n"

    if not table_rows:
        table_rows = "| 🌐 Global | 0 | - |\n"

    # 3. به‌روزرسانی فایل README.md در پوشه Country
    country_readme_path = os.path.join(country_dir, "README.md")
    readme_content = f"""<div align="center">

# 🌍 مرکز سرورهای کشوری (Countries Hub)

تفکیک زنده بر اساس کشور، تعداد نودهای فعال و کدهای QR

</div>

---

| کشور (Country) | تعداد نودها (Nodes) | لینک مستقیم سابسکرایب |
| :--- | :---: | :---: |
{table_rows}
---
> آخرین بروزرسانی خودکار با سیستم هوشمند
"""
    with open(country_readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ جدول‌ها و فایل‌های کشوری با موفقیت به‌روزرسانی شدند.")

if __name__ == "__main__":
    update_readme_and_countries()
