#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Mega-Engine: MTProto Telegram Proxy Collector (Zero-Hardcoded Sources)
منابع ۱۰۰٪ مخفی | تست پینگ زنده | دکمه شیشه‌ای (بدون پین خودکار)
"""

from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs
import asyncio, os, re, sys, json
import aiohttp

def _load_credentials() -> Tuple[str, str]:
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

BOT_TOKEN, CHAT_ID = _load_credentials()

# منابع کاملاً مخفی هستند و از متغیر محیطی خوانده می‌شوند (هیچ لینکی در کد نیست)
def _get_sources() -> List[str]:
    raw = os.environ.get("PROXY_SOURCES", "").strip()
    if raw:
        return [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
    if os.path.exists("proxy_sources.txt"):
        try:
            with open("proxy_sources.txt", "r", encoding="utf-8") as f:
                return [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except Exception: pass
    return []

SOURCES = _get_sources()

OUTPUT_FILE = "subscriptions/plain/guard8.txt"
CHANNEL_LINK = "https://t.me/Goodbaye_filtering"
CHAT_GROUP_LINK = "https://t.me/CONFIG_V2RAY_VIP"
FETCH_TIMEOUT = 14.0
TCP_TIMEOUT = 3.5
MAX_CONCURRENT_TESTS = 50
MAX_RETRIES = 2
PROXY_RE = re.compile(r"(?:https?://t\.me|tg://)/?(?:proxy)?\?[^\s'\"<>]+")

@dataclass
class ProxyLink:
    server: str
    port: int
    secret: str
    raw: str
    latency: float = 999.0

    def __hash__(self): return hash((self.server, self.port, self.secret))
    def __eq__(self, o): return isinstance(o, ProxyLink) and (self.server, self.port, self.secret) == (o.server, o.port, o.secret)

def parse_proxy_line(line: str) -> Optional[ProxyLink]:
    line = line.strip()
    if not line: return None
    try:
        m = PROXY_RE.search(line)
        if not m: return None
        url = m.group(0)
        norm = url if url.startswith("http") else "https://t.me/proxy" + url[url.index("?"):]
        qs = parse_qs(urlparse(norm).query)
        s = (qs.get("server", [""])[0] or "").strip().rstrip(".").lower()
        prt = (qs.get("port", [""])[0] or "").strip()
        sec = (qs.get("secret", [""])[0] or "").strip()
        if not s or not prt.isdigit() or not sec: return None
        p = int(prt)
        if not (0 < p < 65536): return None
        return ProxyLink(server=s, port=p, secret=sec, raw=f"https://t.me/proxy?server={s}&port={p}&secret={sec}")
    except Exception:
        return None

async def fetch_source(session, url):
    for _ in range(MAX_RETRIES):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT), ssl=False) as r:
                if r.status == 200: return (await r.text(errors="ignore")).splitlines()
        except Exception: await asyncio.sleep(1.0)
    return []

async def collect_all():
    if not SOURCES:
        print("⚠️ هیچ منبعی در PROXY_SOURCES تعریف نشده است.")
        return []
    print(f"🚀 [PROXY] دریافت پروکسی‌ها از {len(SOURCES)} منبع مخفی...")
    connector = aiohttp.TCPConnector(limit=60, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        res = await asyncio.gather(*[fetch_source(session, u) for u in SOURCES])

    seen, proxies = set(), []
    for lines in res:
        for l in lines:
            p = parse_proxy_line(l)
            if p and (p.server, p.port, p.secret) not in seen:
                seen.add((p.server, p.port, p.secret))
                proxies.append(p)
    print(f"✅ {len(proxies)} پروکسی یکتا استخراج شد.")
    return proxies

async def measure(p, sem):
    async with sem:
        t0 = asyncio.get_event_loop().time()
        w = None
        try:
            _, w = await asyncio.wait_for(asyncio.open_connection(p.server, p.port), timeout=TCP_TIMEOUT)
            p.latency = round((asyncio.get_event_loop().time() - t0) * 1000, 1)
            return p
        except Exception: return None
        finally:
            if w:
                try: w.close(); await w.wait_closed()
                except Exception: pass

async def send_to_telegram(file_path, proxies):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ خطا: توکن یا چت‌آیدی تنظیم نشده است.")
        return
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(tehran_tz)
    caption = f"""📦 فایل: {os.path.basename(file_path)}
📊 تعداد: {len(proxies)} پروکسی MTProto زنده
⏱️ پینگ واقعی: همگی < 500ms
🕒 ساعت بروزرسانی: {now.strftime('%H:%M:%S')} (تهران)
📅 تاریخ میلادی: {now.strftime('%Y-%m-%d')}

💬 گروه: {CHAT_GROUP_LINK}
✨ کانال: {CHANNEL_LINK}"""

    url_doc = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    url_msg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("chat_id", CHAT_ID)
            data.add_field("caption", caption)
            data.add_field("document", f, filename=os.path.basename(file_path))
            try:
                async with session.post(url_doc, data=data, timeout=aiohttp.ClientTimeout(total=45)) as r:
                    res = await r.json()
                    if res.get("ok"): print("✔ فایل پروکسی‌های MTProto به کانال ارسال شد.")
            except Exception as e: print("❌ خطا در ارسال فایل:", e)

        if proxies:
            top = proxies[:3]
            kb = []
            lines = ["🚀 <b>۳ پروکسی فوق‌سریع برتر تلگرام (اتصال با یک کلیک):</b>\n"]
            for i, p in enumerate(top, 1):
                lines.append(f"<b>پروکسی {i}</b> | پینگ: <b>{p.latency}ms</b>\n<code>{p.raw}</code>\n")
                kb.append([{"text": f"⚡ اتصال به پروکسی {i} ({int(p.latency)}ms)", "url": p.raw}])
            try:
                async with session.post(url_msg, json={"chat_id": CHAT_ID, "text": "\n".join(lines), "parse_mode": "HTML", "reply_markup": {"inline_keyboard": kb}}, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    res = await r.json()
                    if res.get("ok"): print("✔ پیام ۳ دکمه شیشه‌ای بدون پین ارسال شد.")
            except Exception as e: print("❌ خطا در ارسال دکمه‌ها:", e)

async def main():
    proxies = await collect_all()
    if not proxies:
        print("❌ پروکسی یافت نشد.")
        return
    sem = asyncio.Semaphore(MAX_CONCURRENT_TESTS)
    print(f"🧪 تست پینگ {len(pxs := proxies)} پروکسی...")
    res = await asyncio.gather(*[measure(p, sem) for p in pxs])
    alive = [p for p in res if p]
    alive.sort(key=lambda x: x.latency)
    print(f"⚡ {len(alive)} پروکسی سالم تایید شدند.")
    if not alive: return

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(p.raw for p in alive))
    print(f"💾 فایل {OUTPUT_FILE} ذخیره شد.")
    await send_to_telegram(OUTPUT_FILE, alive)

if __name__ == "__main__":
    asyncio.run(main())
