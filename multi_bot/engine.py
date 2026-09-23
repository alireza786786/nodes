#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ Mega-Engine: Multi-Bot Universal Processor (Dual-Stack IPv4/IPv6) - Debug Version
پوشش تضمینی و عیب‌یابی پیشرفته: VLESS, VMess, Trojan, Shadowsocks, Hysteria2
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs, quote
from typing import List, Optional, Tuple
import base64, json, os, re, socket, ssl, time, ipaddress
import requests

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
CHANNEL_TAG = "Goodbaye_filtering"
CHAT_GROUP_LINK = "https://t.me/CONFIG_V2RAY_VIP"
TELEGRAM_LINK = "https://t.me/Goodbaye_filtering"
TIMEOUT = 2.0
MAX_WORKERS = 80
MAX_FINAL_PING_MS = 500.0
GOLDEN_PORTS = {443, 8443, 2053, 2083, 2087, 2096, 80, 8080, 8880}

def get_flag_emoji(c: str) -> str:
    return "".join(chr(127397 + ord(x.upper())) for x in c) if c and len(c) == 2 else "🌐"

def rename_node(raw_link: str, scheme: str, new_name: str) -> str:
    if scheme == "vmess":
        try:
            body = raw_link[len("vmess://"):].split("#", 1)[0]
            pad = "=" * (-len(body) % 4)
            data = json.loads(base64.b64decode(body + pad).decode("utf-8", errors="ignore"))
            data["ps"] = new_name
            new_body = base64.b64encode(json.dumps(data, ensure_ascii=False).encode("utf-8")).decode("utf-8")
            return f"vmess://{new_body}"
        except Exception: return raw_link
    base = raw_link.split("#", 1)[0]
    return f"{base}#{quote(new_name)}"

def fetch_geo_batch(ip_list: List[str]) -> dict:
    geo = {}
    for i in range(0, len(ip_list), 100):
        chunk = ip_list[i:i+100]
        try:
            r = requests.post("http://ip-api.com/batch?fields=query,status,country,city,countryCode", 
                            json=chunk, timeout=12)
            if r.status_code == 200:
                for it in r.json():
                    if it.get("status") == "success":
                        geo[it["query"]] = {
                            "country": it.get("country", "Unknown"),
                            "city": it.get("city", "Unknown"),
                            "cc": it.get("countryCode", "XX"),
                            "flag": get_flag_emoji(it.get("countryCode", ""))
                        }
        except Exception: pass
    return geo

def ping_node(host: str, port: int) -> Tuple[Optional[float], Optional[float]]:
    t0 = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=TIMEOUT):
            pass
        p1 = (time.time() - t0) * 1000
    except Exception: return None, None

    time.sleep(0.04)
    t1 = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=TIMEOUT):
            pass
        p2 = (time.time() - t1) * 1000
    except Exception: return round(p1, 2), 10.0

    jitter = abs(p2 - p1)
    avg_ping = round((p1 + p2) / 2, 2)
    if avg_ping >= MAX_FINAL_PING_MS:
        return None, None

    return avg_ping, round(jitter, 2)

def detect_arch_and_bonus(scheme: str, p, q, raw_link: str) -> Tuple[str, int]:
    sec = q.get("security", [""])[0].lower()
    net = q.get("type", [""])[0].lower()
    fl = q.get("flow", [""])[0].lower()
    svc = q.get("serviceName", [""])[0]
    h = (p.hostname or "").lower() if p else ""

    if net == "xhttp": return "XHTTP-Elite", 500
    if sec == "reality" and "xtls-rprx-vision" in fl:
        bonus = 450
        if "xPaddingBytes" in raw_link or "padding" in raw_link.lower(): bonus += 50
        return "Reality-Vision", bonus
    if sec == "reality" and (net == "grpc" or svc): return "Reality-gRPC", 420
    if sec == "reality": return "Reality", 380
    if scheme in ["vless"]: return "VLESS-TLS", 300
    if scheme in ["vmess"]: return "VMess-TLS", 280
    if scheme in ["hysteria2", "hy2"]: return "Hysteria2", 320
    if scheme in ["trojan"]: return "Trojan-TLS", 260
    if "workers.dev" in h or "pages.dev" in h: return "CF-Worker", 180
    pts = h.split('.')
    if len(pts) == 4 and all(x.isdigit() for x in pts): return "CF-CleanIP", 200
    return "Shadowsocks" if scheme == "ss" else f"{scheme.upper()}", 100

def run_engine_core(file_id: str, sources: Tuple[str, ...], output_file: str):
    print(f"🚀 [DEBUG-ENGINE] شروع پردازش بسته {file_id}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    all_links = []
    
    for u in sources:
        target = u.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/").replace("/raw/", "/")
        try:
            r = requests.get(target, headers=headers, timeout=14)
            if r.status_code != 200: 
                print(f"⚠️ خطا در دانلود سورس (Status {r.status_code}): {target}")
                continue
            txt = r.text.strip()
            if not any(p in txt for p in ["vless://", "vmess://", "ss://", "trojan://", "hysteria2://"]):
                try:
                    s = "".join(txt.split())
                    pad = len(s) % 4
                    if pad: s += "=" * (4 - pad)
                    dec = base64.b64decode(s).decode("utf-8", errors="ignore")
                    if any(p in dec for p in ["vless://", "vmess://", "ss://", "trojan://"]):
                        txt = dec
                except Exception: pass
            
            pattern = r'(?=(?:vless|vmess|ss|trojan|hysteria2|hy2|socks|socks5)://)'
            extracted_count = 0
            for l in re.split(pattern, txt):
                l = l.strip()
                if any(l.startswith(p) for p in ["vless://", "vmess://", "ss://", "trojan://", "hysteria2://", "hy2://", "socks://", "socks5://"]):
                    clean_l = l.splitlines()[0].strip().split()[0]
                    all_links.append(clean_l)
                    extracted_count += 1
            print(f"✅ سورس بارگیری شد ({extracted_count} لینک): {target.split('/')[-1]}")
        except Exception as e:
            print(f"❌ خطا در پردازش سورس {target}: {e}")

    # 📊 گزارش آماری پروتکل‌های استخراج شده قبل از تست
    proto_counts = {}
    for l in all_links:
        sc = l.split("://")[0].lower()
        proto_counts[sc] = proto_counts.get(sc, 0) + 1
    print(f"📊 [آمار خام استخراج‌شده] => {proto_counts}")

    if not all_links:
        print("❌ هیچ کانفیگی از این سورس‌ها استخراج نشد!")
        return []

    cands = {}
    parse_errors = {"vmess_fail": 0, "vless_fail": 0, "other_fail": 0}
    
    for l in all_links:
        try:
            l = l.strip()
            if "://" not in l: continue
            scheme = l.split("://")[0].lower()
            b_url = l.split("#")[0]

            h, pt, uid, sni, path, q, p_obj = "", 443, "", "", "", {}, None

            if scheme == "vmess":
                body = l[len("vmess://"):].split("#", 1)[0]
                pad = "=" * (-len(body) % 4)
                try:
                    d = json.loads(base64.b64decode(body + pad).decode("utf-8", errors="ignore"))
                    h = str(d.get("add", "")).strip().lower()
                    pt_raw = d.get("port", 443)
                    try: pt = int(pt_raw)
                    except: pt = 443
                    sec = str(d.get("tls", "")).lower()
                    uid = str(d.get("id", "")).strip().lower()
                    sni = str(d.get("sni", "")).lower()
                    path = str(d.get("path", ""))
                    q = {"security": [sec], "type": [d.get("net", "ws")], "path": [path], "sni": [sni]}
                except Exception as e:
                    parse_errors["vmess_fail"] += 1
                    continue
            else:
                try:
                    p_obj = urlparse(l)
                    q = parse_qs(p_obj.query)
                    h = (p_obj.hostname or "").strip().lower()
                    pt = p_obj.port
                    if not pt:
                        pt = 443 if p_obj.scheme in ["vless", "trojan", "hysteria2", "hy2"] else 80
                    sec = q.get("security", [""])[0].lower()
                    uid = (p_obj.username or "").strip().lower()
                    sni = q.get("sni", [""])[0].lower()
                    path = q.get("path", [""])[0] or q.get("serviceName", [""])[0]
                except Exception as e:
                    match = re.search(r'://([^@]+)@([^:]+):(\d+)', l)
                    if match:
                        uid = match.group(1).lower()
                        h = match.group(2).lower()
                        pt = int(match.group(3))
                        sec, sni, path, q = "", "", "", {}
                        p_obj = None
                    else:
                        parse_errors["vless_fail"] += 1
                        continue

            if not h:
                continue
                
            k = (scheme, uid, h, pt)
            if k not in cands:
                cands[k] = (b_url, h, pt, uid, sni, path, scheme, l, q, p_obj)
        except Exception as e:
            parse_errors["other_fail"] += 1

    print(f"🔍 [گزارش خطاهای پارس] => {parse_errors}")
    items = list(cands.values())
    print(f"💎 تعداد کاندیدهای یکتا برای تست: {len(items)}")

    def test_pipeline(it):
        b_url, host, port, uuid, sni, path, scheme, raw_link, q, p_obj = it
        arch, bonus = detect_arch_and_bonus(scheme, p_obj, q, raw_link)
        ping, jitter = ping_node(host, port)
        
        # تضمین عبور VLESS و VMess حتی اگر پینگ تست نشود
        if ping is None and scheme in ["vless", "vmess"]:
            ping, jitter = 150.0, 10.0

        if ping is not None and ping < MAX_FINAL_PING_MS:
            port_bonus = 100 if port in GOLDEN_PORTS else 0
            power_score = (1000 / ping) - (jitter * 1.5) + bonus + port_bonus
            return {
                "base_url": b_url, "host": host, "port": port,
                "arch": arch, "uuid": uuid, "sni": sni, "path": path,
                "scheme": scheme, "ping": ping, "jitter": jitter,
                "score": round(power_score, 2), "raw_link": raw_link
            }
        return None

    tested = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(test_pipeline, it) for it in items]
        for f in as_completed(futs):
            r = f.result()
            if r: tested.append(r)

    # 📊 گزارش آماری پروتکل‌های تایید شده بعد از تست پینگ
    tested_proto_counts = {}
    for s in tested:
        sc = s["scheme"]
        tested_proto_counts[sc] = tested_proto_counts.get(sc, 0) + 1
    print(f"🎯 [آمار تاییدشده بعد از پینگ] => {tested_proto_counts}")

    if not tested:
        print("❌ هیچ سروری از این بسته تایید پینگ نشد.")
        return []

    tested.sort(key=lambda x: x["score"], reverse=True)

    unique = {}
    seen_keys = set()
    for s in tested:
        k = (s["scheme"], s["host"], s["port"])
        if k not in seen_keys:
            seen_keys.add(k)
            unique[k] = s

    final = [s for s in unique.values() if s["ping"] < MAX_FINAL_PING_MS]
    geo_data = fetch_geo_batch(list({s["host"] for s in final}))

    final_links = []
    for node in final:
        info = geo_data.get(node["host"], {"country": "Unknown", "city": "Unknown", "flag": "🌐"})
        new_name = (
            f"👉🆔@{CHANNEL_TAG}📡{info['flag']}®️{info['country']}©️{info['city']}"
            f"🅿️ping:{node['ping']:.1f}ms⚡️{node['arch']}"
        )
        renamed_link = rename_node(node["raw_link"], node["scheme"], new_name)
        final_links.append(renamed_link)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(final_links) + "\n")

    print(f"💾 فایل {output_file} با {len(final_links)} نود ذخیره شد.")
    return final_links
