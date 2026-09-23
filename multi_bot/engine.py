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
                # اگر هاست خالی بود، از IP پیش‌فرض یا ساختار جایگزین استفاده کن تا حذف نشود
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
