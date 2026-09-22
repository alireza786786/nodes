#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 حذف خودکار تمام پین‌ها از سقف کانال
"""
import os, json, requests

def _load_credentials():
    t = os.environ.get("BOT_TOKEN", "").strip()
    c = os.environ.get("CHAT_ID", "").strip()
    if not t or not c:
        p = os.path.expanduser("~/.tg_secrets.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    t = t or d.get("bot_token", "")
                    c = c or d.get("channel_id", "")
            except Exception: pass
    return t, c

def main():
    token, chat_id = _load_credentials()
    if not token or not chat_id:
        print("❌ خطا: توکن یا چت‌آیدی تنظیم نشده است.")
        return
    url = f"https://api.telegram.org/bot{token}/unpinAllChatMessages"
    try:
        r = requests.post(url, json={"chat_id": chat_id}, timeout=20)
        if r.json().get("ok"):
            print("✔ موفقیت: تمام پیام‌های پین‌شده از بالای کانال برداشته شدند.")
        else:
            print("⚠️ تلگرام:", r.json().get("description"))
    except Exception as e:
        print("❌ خطا:", e)

if __name__ == "__main__":
    main()
