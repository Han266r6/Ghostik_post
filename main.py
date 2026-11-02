#!/usr/bin/env python3
"""
Ghost Protocol - 24/7 Telegram MTProxy Channel Poster Bot
Framework: pyTelegramBotAPI (telebot) + Flask (Keep-Alive Server)
Host Target: Render.com / GitHub / VPS
Exclusively authorized for Admin ID: 6640701495
"""

import os
import re
import time
import logging
import threading
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify
import requests

import telebot
from telebot import types

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("GhostProtocol")

# ---------------------------------------------------------
# Environment Variables & Strict Admin Security
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8643237203:AAF5V_shvCNWoAyKBZkhnE8aOgQVTD8TVV0").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()
# Strict Admin Security: Diňe sizde (6640701495) işlemeli
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6640701495").strip() or "6640701495")
PORT = int(os.environ.get("PORT", 5000))

# Render.com automatic external URL or fallback
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
SELF_PING_URL = os.environ.get("SELF_PING_URL", "").strip()

# Post content
POST_TITLE = "Ghost Protocol MTProxy"
POST_TEXT = "Используйте Telegram без VPN, нажмите кнопку (Connect)"

# Track stats & states
start_time = time.time()
ping_counter = 0
current_channel = CHANNEL_ID
admin_states = {}

# ---------------------------------------------------------
# Flask Keep-Alive Web Server (Render.com 24/7 Uptime)
# ---------------------------------------------------------
app = Flask(__name__)

@app.route("/")
def index():
    """Web browser we barlag üçin status sahypasy."""
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ghost Protocol Bot - 24/7 Online</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #080c14; color: #10b981; padding: 40px; text-align: center; }}
            .card {{ background: #0f172a; border: 1px solid #10b981; border-radius: 16px; padding: 30px; display: inline-block; max-width: 520px; box-shadow: 0 0 30px rgba(16,185,129,0.2); }}
            h1 {{ margin: 0 0 15px 0; color: #34d399; font-size: 24px; }}
            p {{ color: #94a3b8; font-size: 14px; margin: 8px 0; }}
            .status {{ color: #10b981; font-weight: bold; }}
            .badge {{ background: #064e3b; color: #6ee7b7; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛡️ Ghost Protocol Bot</h1>
            <p><span class="badge">🟢 24/7 OÝA WE IŞLEÝÄR</span></p>
            <p>Admin ID: <b>{ADMIN_ID} (Doly Goragly)</b></p>
            <p>Kanal: <b>{current_channel if current_channel else "Sazlanmadyk (Telegramdan /setchannel ýazyň)"}</b></p>
            <p>Iş wagty (Uptime): <b>{uptime_str}</b></p>
            <p>Awtomatiki Oýaryjy Ping sany: <b>{ping_counter}</b></p>
            <p style="margin-top:20px; font-size:12px; color:#64748b;">Keep-Alive Endpoint: <code>/healthz</code></p>
        </div>
    </body>
    </html>
    """, 200

@app.route("/healthz")
def healthz():
    """Lightweight 200 OK endpoint for internal/external keep-alive."""
    return jsonify({
        "status": "healthy",
        "service": "Ghost Protocol MTProxy Bot",
        "admin_id": ADMIN_ID,
        "uptime_seconds": int(time.time() - start_time),
        "channel": current_channel,
        "self_pings": ping_counter
    }), 200

def start_flask():
    """Flask web serverini arka fonda daemons hökmünde işletmek."""
    logger.info(f"Flask Keep-Alive web serveri 0.0.0.0:{PORT} salgysynda işe girizildi.")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

# ---------------------------------------------------------
# Awtomatiki Oýaryjy (Self-Ping / Anti-Sleep Thread)
# Render.com serweriniň 15 minutda uka gitmegini doly aradan aýyrýar!
# ---------------------------------------------------------
def auto_keep_alive_pinger():
    """
    Her 4-5 minutdan Render web serwerine HTTP haýyş ugradyp,
    serweri 24/7 gije-gündüz oýa saklaýar.
    """
    global ping_counter
    time.sleep(20)
    logger.info("Awtomatiki oýaryjy (Self-Pinger) işe başlady.")

    while True:
        try:
            target_urls = []
            
            # 1. Render-iň öz berýän public web salgysy
            if RENDER_EXTERNAL_URL:
                target_urls.append(f"{RENDER_EXTERNAL_URL.rstrip('/')}/healthz")
            if SELF_PING_URL:
                target_urls.append(f"{SELF_PING_URL.rstrip('/')}/healthz")
                
            # 2. Localhost barlagy
            target_urls.append(f"http://127.0.0.1:{PORT}/healthz")

            for url in target_urls:
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        ping_counter += 1
                        logger.info(f"[Keep-Alive] Serwer oýaryldy: {url} -> 200 OK (Jemi: {ping_counter})")
                        break
                except Exception as ping_err:
                    logger.debug(f"Ping haýyşy başa barmady: {url} ({ping_err})")

        except Exception as e:
            logger.error(f"Awtomatiki oýaryjy säwligi: {e}")

        # Her 4 minutdan (240 sekunt) gaýtadan oýarýar
        time.sleep(240)

# ---------------------------------------------------------
# Universal MTProxy Parser (Islendik Formatdaky Linki Tanaýar)
# ---------------------------------------------------------
def parse_mtproxy_links(text: str) -> list[str]:
    """
    Islendik formatdaky MTProxy linklerini derrew saýlap alýar:
      - https://t.me/proxy?server=...&port=...&secret=...
      - tg://proxy?server=...&port=...&secret=...
      - Göni IP:PORT:SECRET (mysal: 185.123.45.67:443:ee0000...)
    """
    valid_links = []
    
    # 1. URL formatlary (https://t.me/proxy ýa-da tg://proxy)
    url_pattern = re.compile(r'(?:https?://t.me/proxy?[^\s\<\>"\']+|tg://proxy?[^\s\<\>"\']+)', re.IGNORECASE)
    found_urls = url_pattern.findall(text)
    
    for url in found_urls:
        clean_url = url.replace("tg://proxy?", "https://t.me/proxy?")
        parsed = urlparse(clean_url)
        params = parse_qs(parsed.query)
        
        server = params.get("server", [""])[0]
        port = params.get("port", [""])[0]
        secret = params.get("secret", [""])[0]
        
        if server and port and secret:
            normalized = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
            if normalized not in valid_links:
                valid_links.append(normalized)

    # 2. Göni IP:PORT:SECRET formaty
    raw_pattern = re.compile(
        r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b):(\d{2,5}):([a-fA-F0-9]{32,64}|ee[a-fA-F0-9]+|dd[a-fA-F0-9]+)',
        re.IGNORECASE
    )
    found_raw = raw_pattern.findall(text)
    for server, port, secret in found_raw:
        normalized = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
        if normalized not in valid_links:
            valid_links.append(normalized)

    return valid_links

def build_inline_keyboard(links: list[str]) -> types.InlineKeyboardMarkup:
    """
    Siz näçe link ugratsaňyz (1, 2, 3, 4, 6 ýa-da islendik mukdarda),
    şonça 'Connect ↗' düwmelerini owadan 2 sütünli tertipde döredýär.
    """
    markup = types.InlineKeyboardMarkup()
    count = len(links)
    
    buttons = []
    for i, link in enumerate(links, start=1):
        btn_text = f"Connect {i} ↗" if count > 1 else "Connect ↗"
        btn = types.InlineKeyboardButton(text=btn_text, url=link)
        buttons.append(btn)
    
    # 2 sütünli tertip
    if count == 1:
        markup.add(buttons[0])
    elif count % 2 == 0:
        for i in range(0, count, 2):
            markup.row(buttons[i], buttons[i + 1])
    else:
        for i in range(0, count - 1, 2):
            markup.row(buttons[i], buttons[i + 1])
        markup.add(buttons[-1])
        
    return markup

# ---------------------------------------------------------
# Telebot Setup & Strict Admin Authorization
# ---------------------------------------------------------
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def check_admin(message: types.Message) -> bool:
    """
    HOWPSUZLYK TALABY:
    Bot diňe we diňe siziň Telegram ID-iňizde (6640701495) işlemeli.
    Başga hiç kim bota girip ýa-da buýruk berip bilmeýär!
    """
    if message.from_user.id != ADMIN_ID:
        logger.warning(f"Röwhusyz giriş synanyşygy: User ID={message.from_user.id}")
        bot.reply_to(
            message,
            "⛔ <b>Giriş gadagan edildi!</b>\nBu bot hususy we diňe bellenen administratoryň özi üçin goralandyr."
        )
        return False
    return True

# ---------------------------------------------------------
# Bot Handlerleri
# ---------------------------------------------------------
@bot.message_handler(commands=["start", "help"])
def send_welcome(message: types.Message):
    if not check_admin(message):
        return

    welcome_text = (
        "🛡️ <b>Salam, Ghost Protocol Hoş Geldiňiz!</b>\n\n"
        "Bot doly goralan we diňe siziň Telegram ID-iňizde (<code>6640701495</code>) işleýär.\n"
        "Render.com-da 24/7 uka gitmezlik üçin awtomatiki oýaryjy gurlan.\n\n"
        f"📢 <b>Häzirki Kanal:</b> <code>{current_channel or 'Sazlanmadyk'}</code>\n"
        f"⚡ <b>Ýagdaýy:</b> 7/24 Aktiw, duýgur jogap bermäge taýýar!\n\n"
        "<b>Esasy Buýruklar:</b>\n"
        "• <code>/post</code> - Täze MTProxy postyny taýýarlamak\n"
        "• <code>/setchannel @kanal</code> - Post iberiljek kanaly sazlamak\n"
        "• <code>/status</code> - 24/7 iş wagty we awtomatiki oýaryjyny görmek\n"
        "• <code>/ping</code> - Botuň tizligini we oýalygyny barlamak\n"
        "• <code>/cancel</code> - Häzirki amaly ýatyrmak\n\n"
        "💡 <b>Tiz usul:</b> Islendik formatdaky MTProxy linkleriňizi göni şu bota ugratsaňyz, "
        "bot olary derrew tanaýar we Connect düwmeleri bilen kanala paýlaşmaga taýýarlaýar!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=["ping"])
def ping_cmd(message: types.Message):
    if not check_admin(message):
        return
    t0 = time.time()
    msg = bot.reply_to(message, "⚡ <i>Barlanýar...</i>")
    dt = round((time.time() - t0) * 1000, 1)
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.message_id,
        text=f"⚡ <b>Bot Oýa we Tiz Jogap Berýär!</b>\n\n• Jogap tizligi: <b>{dt} ms</b>\n• Status: 🟢 7/24 Durman Işleýär!",
        parse_mode="HTML"
    )

@bot.message_handler(commands=["status"])
def check_status(message: types.Message):
    if not check_admin(message):
        return
    
    uptime = int(time.time() - start_time)
    h, rem = divmod(uptime, 3600)
    m, s = divmod(rem, 60)
    
    bot.reply_to(
        message,
        f"🟢 <b>Ghost Protocol 24/7 Status</b>\n\n"
        f"• <b>Admin:</b> <code>{ADMIN_ID}</code> (Diňe sizde işleýär)\n"
        f"• <b>Iş wagty:</b> {h} sagat, {m} minut, {s} sekunt\n"
        f"• <b>Awtomatiki Oýaryjy:</b> {ping_counter} gezek Render oýaryldy\n"
        f"• <b>Web Server:</b> 0.0.0.0:{PORT} (/healthz)\n"
        f"• <b>Birikdirilen Kanal:</b> <code>{current_channel or 'Sazlanmadyk (/setchannel @kanal)'}</code>"
    )

@bot.message_handler(commands=["setchannel"])
def set_channel(message: types.Message):
    global current_channel
    if not check_admin(message):
        return

    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(
            message,
            "⚠️ <b>Kanal salgysyny görkeziň!</b>\n\n"
            "Mysal üçin:\n<code>/setchannel @sizin_kanalyňyz</code>\n"
            "ýa-da ýapyk kanal üçin ID: <code>/setchannel -1001234567890</code>"
        )
        return

    new_ch = parts[1].strip()
    current_channel = new_ch
    bot.reply_to(
        message,
        f"✅ <b>Kanal üstünlikli bellenildi:</b> <code>{current_channel}</code>\n\n"
        "<i>Bellik: Botuň bu kanalda Administrator bolandygyny we 'Post Messages' ygtyýarlylygynyň barlygyny barlaň!</i>"
    )

@bot.message_handler(commands=["cancel"])
def cancel_process(message: types.Message):
    if not check_admin(message):
        return
    if message.from_user.id in admin_states:
        del admin_states[message.from_user.id]
    bot.reply_to(message, "✅ Amal ýatyryldy.")

@bot.message_handler(commands=["post"])
def initiate_post(message: types.Message):
    if not check_admin(message):
        return

    admin_states[message.from_user.id] = {"action": "waiting_proxies"}
    bot.reply_to(
        message,
        "📥 <b>MTProxy linkleriňizi ugradyň:</b>\n\n"
        "Siz linkleri islendik formatda ugradyp bilersiňiz:\n"
        "• <code>https://t.me/proxy?server=...&port=...&secret=...</code>\n"
        "• <code>tg://proxy?server=...&port=...&secret=...</code>\n"
        "• Göni <code>IP:PORT:SECRET</code>\n"
        "• Ýa-da birnäçe linki bulaşyk tekst bilen bilelikde.\n\n"
        "<i>(Ýatyrmak üçin /cancel ýazyň)</i>"
    )

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_text_proxies(message: types.Message):
    if not check_admin(message):
        return

    text = message.text.strip()
    links = parse_mtproxy_links(text)

    if not links:
        if admin_states.get(message.from_user.id, {}).get("action") == "waiting_proxies":
            bot.reply_to(
                message,
                "⚠️ <b>Hiç hili dogry MTProxy tapylmady!</b>\n"
                "Haýyş edýäris, linkiňizde <code>server</code>, <code>port</code> we <code>secret</code> barlygyny barlaň."
            )
        return

    keyboard = build_inline_keyboard(links)
    caption = f"<b>{POST_TITLE}</b>\n\n{POST_TEXT}"

    target = current_channel or CHANNEL_ID
    if not target:
        bot.reply_to(
            message,
            f"✅ <b>{len(links)} sany MTProxy tapyldy!</b>\n\n"
            "⚠️ Emma post iberiljek kanal entek sazlanmandyr.\n"
            "Kanal bellemek üçin şu buýrugy ýazyň: <code>/setchannel @sizin_kanalyňyz</code>\n\n"
            "Aşakda postuňyz üçin Connect düwmeleriniň syny (Preview):",
            reply_markup=keyboard
        )
        return

    # Posty kanala ugratmak
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "ghost_profile_logo.jpg")
        
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as photo:
                bot.send_photo(
                    chat_id=target,
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        else:
            bot.send_message(
                chat_id=target,
                text=caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        bot.reply_to(
            message,
            f"🚀 <b>Post üstünlikli kanala ugradyldy!</b>\n\n"
            f"• Kanal: <code>{target}</code>\n"
            f"• Goşulan Connect düwmeleri: <b>{len(links)} sany</b>",
            reply_markup=keyboard
        )
        if message.from_user.id in admin_states:
            del admin_states[message.from_user.id]

    except Exception as e:
        logger.error(f"Kanala post ibermekde säwlik: {e}")
        bot.reply_to(
            message,
            f"❌ <b>Post ugradyp bolmady!</b>\n\n"
            f"Säwlik jikme-jigi: <code>{e}</code>\n\n"
            "<b>Näme etmeli?</b>\n"
            "1. Botuňyz hökman kanalda <b>Administrator</b> bolmaly.\n"
            "2. Botuň 'Post Messages' (Habar paýlaşmak) ygtyýarlylygynyň barlygyny barlaň.\n"
            f"3. Eger kanal ady ýalňyş bolsa, <code>/setchannel @taze_kanal</code> ýazyň."
        )

# ---------------------------------------------------------
# Esasy Programmanyň Başlangyjy
# ---------------------------------------------------------
def main():
    logger.info(f"Ghost Protocol Bot taýýarlanýar... Admin ID: {ADMIN_ID}")

    # 1. Flask Keep-Alive Web Serverini background thread-de başlatmak
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # 2. Render 24/7 Awtomatiki Oýaryjyny (Self-Ping) background thread-de başlatmak
    pinger_thread = threading.Thread(target=auto_keep_alive_pinger, daemon=True)
    pinger_thread.start()

    # 3. Telegram Bot Polling-iň çalt we duýgur tertipde işlemesi
    logger.info("Telegram Bot Polling (infinity_polling) işe girizilýär...")
    while True:
        try:
            bot.infinity_polling(
                timeout=10,
                long_polling_timeout=10,
                skip_pending=True,
                allowed_updates=["message", "callback_query"]
            )
        except Exception as exc:
            logger.error(f"Polling säwligi: {exc}. 5 sekuntdan gaýtadan barlanýar...")
            time.sleep(5)

if __name__ == "__main__":
    main()
