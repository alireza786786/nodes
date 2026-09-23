#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Master Hub & UI Auto-Updater (Countries & README Sync)
"""
import os
import glob

def run_updater():
    print("🔄 در حال پردازش و به‌روزرسانی رابط کاربری مخزن...")
    
    # 1. خواندن تمام نودهای موجود از پوشه Config
    config_files = glob.glob("Config/*.txt")
    all_nodes = []
    for cf in config_files:
        try:
            with open(cf, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and "://" in line]
                all_nodes.extend(lines)
        except Exception: 
            pass

    # حذف تکراری‌ها
    all_nodes = list(set(all_nodes))
    print(f"💎 کل نودهای یکتا برای دسته‌بندی کشوری: {len(all_nodes)}")

    # 2. دسته‌بندی نودها بر اساس کشور
    country_data = {}
    global_nodes = []

    for node in all_nodes:
        global_nodes.append(node)
        if "®️" in node and "©️" in node:
            try:
                parts = node.split("®️")[1].split("©️")
                country_name = parts[0].strip()
                flag_part = node.split("📡")[1].split("®️")[0] if "📡" in node else "🌐"
                
                key = (country_name, flag_part)
                if key not in country_data:
                    country_data[key] = []
                country_data[key].append(node)
            except Exception:
                pass

    # 3. ایجاد پوشه Country و فایل‌های متنی هر کشور
    country_dir = "Country"
    os.makedirs(country_dir, exist_ok=True)
    
    table_rows = ""
    # مرتب‌سازی بر اساس بیشترین تعداد نود
    sorted_countries = sorted(country_data.items(), key=lambda x: len(x[1]), reverse=True)

    for (c_name, flag), nodes in sorted_countries:
        count = len(nodes)
        cc_code = "".join([c for c in c_name if c.isalnum()]).lower() or "xx"
        file_name = f"{cc_code}.txt"
        file_path = os.path.join(country_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(nodes) + "\n")
            
        sub_link = f"./{file_name}"
        table_rows += f"| {flag} {c_name} | {count} | [سابسکرایب]({sub_link}) |\n"

    if not table_rows:
        table_rows = "| 🌐 Global | 0 | - |\n"

    # 4. آپدیت خودکار فایل README.md داخل پوشه Country
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

    print(f"✅ تفکیک کشوری انجام شد. تعداد {len(sorted_countries)} کشور شناسایی و ذخیره شد.")

if __name__ == "__main__":
    run_updater()
