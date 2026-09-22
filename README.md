<div align="center">

# 🌐 NODES HYPER-HUB
### پایگاه جامع و خودکار توزیع، پالایش و سابسکریپشن کانفیگ‌های نسل جدید

![Status](https://img.shields.io/badge/Status-Active%20%26%20Clean-success?style=for-the-badge&logo=githubactions&logoColor=white)
![Python](https://img.shields.io/badge/Engine-Multi--Bot%203.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Speed](https://img.shields.io/badge/Latency-Ping%20%3C%20500ms-orange?style=for-the-badge&logo=speedtest&logoColor=white)

---

### 📱 اسکن سریع با بارکد (QR Codes)

<table>
  <tr>
    <td align="center" width="50%">
      <b>📢 کانال رسمی تلگرام</b><br>
      <a href="https://t.me/Goodbaye_filtering">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://t.me/Goodbaye_filtering" alt="QR Channel" width="130"/>
      </a><br>
      <a href="https://t.me/Goodbaye_filtering">👉 @Goodbaye_filtering</a>
    </td>
    <td align="center" width="50%">
      <b>💬 گروه گفتگو و تبادل</b><br>
      <a href="https://t.me/CONFIG_V2RAY_VIP">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://t.me/CONFIG_V2RAY_VIP" alt="QR Group" width="130"/>
      </a><br>
      <a href="https://t.me/CONFIG_V2RAY_VIP">👉 @CONFIG_V2RAY_VIP</a>
    </td>
  </tr>
</table>

</div>

---

## 📂 مراکز تخصصی دسته‌بندی (Hub Directories)

برای دسترسی سریع به هر بخش، روی پوشه مورد نظر کلیک کنید:

* 📁 **[مرکز بسته‌های اشتراک (Subscription)](./Subscription):** شامل دو شاخه متنی `plain` (کپی دستی) و `base64` (کلاینت‌ها)
* 📁 **[مرکز پروتکل‌ها (Config)](./Config):** تفکیک بر اساس ۸ پروتکل (`VLESS`, `VMess`, `Trojan`, `Shadowsocks`, `Hysteria2`, `SOCKS5`, ...)
* 📁 **[مرکز شبکه‌ها و بسترهای انتقال (Transports)](./transports):** بسترهای اختصاصی `gRPC`، `XHTTP`، `WebSocket` و `TCP`
* 📁 **[مرکز سرورهای کشوری (Country)](./Country):** تفکیک جغرافیایی سرورها (آلمان، هلند، فنلاند، آمریکا، روسیه و...)
* ✈️ **[پروکسی‌های تلگرام (Proxy_collector)](./Proxy_collector):** استخراج روزانه پروکسی‌های زنده MTProto تلگرام

---

## 💎 استانداردهای طلایی پایش و انتخاب کانفیگ

1. **پینگ واقعی زیر ۵۰۰ میلی‌ثانیه:** فیلتر قطعی تمام سرورهای مرده، کند یا دارای قطعی مداوم.
2. **سنجش پایداری و نوسان (Jitter):** حذف سرورهایی با نوسان پینگ شدید برای تضمین استریم روان ویدیو و وبگردی.
3. **آزمون شبیه‌سازی عبور از DPI:** تست دست‌دهی عمیق لایه TLS برای جلوگیری از مسدودسازی و حملات قطع اتصال (RST).
4. **صفر تکراری در ویتوری (Zero-Duplicate):** ترجمه دامنه‌ها به آی‌پی فیزیکی و حذف کامل سرورهای مشابه.
5. **بازنویسی تخصصی VMess:** رمزگشایی کدهای Base64 و ویرایش فیلد `"ps"` برای نمایش رسمی نام کانال در تمام کلاینت‌ها.
6. **برندینگ یکپارچه روی هر کانفیگ:**
   ```text
   👉🆔@Goodbaye_filtering📡[پرچم]®️[نام کشور]©️[نام شهر]🅿️ping:[پینگ]ms⚡️[معماری]
