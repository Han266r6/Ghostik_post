#!/usr/bin/env python3
"""
🛡️ Ghost Protocol - 24/7 Telegram MTProxy Channel Poster Bot (Çudo Edition)
Framework: pyTelegramBotAPI (telebot) + Flask (Keep-Alive Server)
Host Target: Render.com / GitHub / VPS
Exclusively authorized for Admin ID: 6640701495
"""

import os
import re
import json
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
# Environment Variables & Base Paths
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8643237203:AAF5V_shvCNWoAyKBZkhnE8aOgQVTD8TVV0").strip()
DEFAULT_CHANNEL = "@ghost_protocolI"
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6640701495").strip() or "6640701495")
PORT = int(os.environ.get("PORT", 5000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").strip()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "post_config.json")
CUSTOM_BANNER_PATH = os.path.join(BASE_DIR, "custom_banner.jpg")
WIDE_BANNER_PATH = os.path.join(BASE_DIR, "ghost_banner_wide.jpg")
LOGO_PATH = os.path.join(BASE_DIR, "ghost_profile_logo.jpg")

start_time = time.time()
ping_counter = 0

# ---------------------------------------------------------
# Default Post Configuration & Ornament Styles
# ---------------------------------------------------------
DEFAULT_POST_CONFIG = {
    "post_text": "Используйте Telegram без VPN, нажмите кнопку (connect)",
    "channel_mention": DEFAULT_CHANNEL,
    "slogan": "Самый быстрый канал прокси в Туркменистане",
    "ornament_style": "default",
    "hashtags": "#ghostprotocol #proxy #freeproxy\n#mtproxy #socks5 #vpn #turkmenistan",
    "use_custom_banner": False
}

ORNAMENT_STYLES = {
    "default": "════════ ◖⚚◗ ════════",
    "diamond": "─── ❖ ─── ❖ ───",
    "fleur": "⚜️ ──────── ⚜️",
    "cyber": "━━━━━━━━━━━━━━",
    "glow": "✧･ﾟ: *✧･ﾟ:* *:･ﾟ✧*:･ﾟ✧",
    "none": ""
}

ORNAMENT_NAMES = {
    "default": "◖⚚◗ Altyn Gerb (2-nji surat)",
    "diamond": "❖ Almaz / Diamond",
    "fleur": "⚜️ Patyşalyk / Royal",
    "cyber": "━ Kiber Çyzyk / Cyber",
    "glow": "✧ Ýyldyz Şuglasy / Glow",
    "none": "🚫 Arakesmesiz (Ýönekeý)"
}

def load_post_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg = DEFAULT_POST_CONFIG.copy()
                cfg.update(saved)
                return cfg
        except Exception as e:
            logger.error(f"Sazlama faýly okalmady: {e}")
    return DEFAULT_POST_CONFIG.copy()

def save_post_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Sazlama faýly ýazylyp bolmady: {e}")

post_config = load_post_config()
current_channel = post_config.get("channel_mention", DEFAULT_CHANNEL)
pending_posts = {}
user_states = {}

def normalize_channel(raw_input: str) -> str:
    if not raw_input:
        return DEFAULT_CHANNEL
    s = raw_input.strip()
    if "t.me/" in s:
        s = s.split("t.me/")[-1].split("/")[0].split("?")[0]
    s = s.strip()
    if s.startswith("-100") or (s.startswith("-") and s[1:].isdigit()):
        return s
    s = s.lstrip("@").strip()
    return f"@{s}"

def generate_channel_caption(channel: str = None) -> str:
    cfg = load_post_config()
    target_channel = channel or cfg.get("channel_mention", DEFAULT_CHANNEL)
    ornament_key = cfg.get("ornament_style", "default")
    ornament = ORNAMENT_STYLES.get(ornament_key, ORNAMENT_STYLES["default"])

    text = cfg.get("post_text", DEFAULT_POST_CONFIG["post_text"])
    slogan = cfg.get("slogan", DEFAULT_POST_CONFIG["slogan"])
    tags = cfg.get("hashtags", DEFAULT_POST_CONFIG["hashtags"])

    if ornament:
        caption = (
            f"<b>{text}</b>\n"
            f"{ornament}\n"
            f"💎 <b>{target_channel}</b>\n"
            f"{ornament}\n"
            f"🥇 <i>{slogan}</i>\n\n"
            f"{tags}"
        )
    else:
        caption = (
            f"<b>{text}</b>\n\n"
            f"💎 <b>{target_channel}</b>\n\n"
            f"🥇 <i>{slogan}</i>\n\n"
            f"{tags}"
        )
    return caption

def get_active_banner_path():
    cfg = load_post_config()
    if cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH):
        return CUSTOM_BANNER_PATH
    if os.path.exists(WIDE_BANNER_PATH):
        return WIDE_BANNER_PATH
    if os.path.exists(LOGO_PATH):
        return LOGO_PATH
    return None

# ---------------------------------------------------------
# Flask Keep-Alive Web Server
# ---------------------------------------------------------
app = Flask(__name__)

@app.route("/")
def index():
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    cfg = load_post_config()
    has_custom = cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH)
    return f"""
    <html><body style="background:#080c14;color:#10b981;font-family:sans-serif;text-align:center;padding:50px;">
        <div style="background:#0f172a;border:1px solid #10b981;border-radius:16px;padding:30px;display:inline-block;max-width:550px;box-shadow:0 0 30px rgba(16,185,129,0.2);">
            <h1 style="color:#34d399;">🛡️ Ghost Protocol Çudo Bot</h1>
            <p style="color:#10b981;font-weight:bold;">🟢 24/7 OÝA WE IŞLEÝÄR (SUPER EDITION)</p>
            <p style="color:#94a3b8;">Admin ID: <b>{ADMIN_ID} (Doly Goralan)</b></p>
            <p style="color:#94a3b8;">Kanal: <b>{cfg.get('channel_mention')}</b></p>
            <p style="color:#94a3b8;">Post Suraty: <b>{'🖼 Galereýa Suraty' if has_custom else '🖼 16:9 Standart Banner'}</b></p>
            <p style="color:#94a3b8;">Uptime: <b>{hours}h {minutes}m {seconds}s</b></p>
            <p style="color:#94a3b8;">Auto-Ping: <b>{ping_counter} gezek oýaryldy</b></p>
        </div>
    </body></html>
    """, 200

@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "healthy",
        "service": "Ghost Protocol MTProxy Bot",
        "admin_id": ADMIN_ID,
        "uptime": int(time.time() - start_time),
        "channel": current_channel,
        "self_pings": ping_counter
    }), 200

def start_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

def auto_keep_alive_pinger():
    global ping_counter
    time.sleep(15)
    while True:
        try:
            urls = []
            if RENDER_EXTERNAL_URL:
                urls.append(f"{RENDER_EXTERNAL_URL.rstrip('/')}/healthz")
            urls.append(f"http://127.0.0.1:{PORT}/healthz")
            for u in urls:
                try:
                    res = requests.get(u, timeout=10)
                    if res.status_code == 200:
                        ping_counter += 1
                        break
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Oýaryjy säwligi: {e}")
        time.sleep(240)

# ---------------------------------------------------------
# Universal MTProxy Parser & Keyboard Builder
# ---------------------------------------------------------
def parse_mtproxy_links(text: str) -> list[str]:
    valid_links = []
    url_pattern = re.compile(r'(?:https?://t\.me/proxy\?[^\s\<\>"\']+|tg://proxy\?[^\s\<\>"\']+)', re.IGNORECASE)
    for url in url_pattern.findall(text):
        clean_url = url.replace("tg://proxy?", "https://t.me/proxy?")
        parsed = urlparse(clean_url)
        params = parse_qs(parsed.query)
        s, p, sec = params.get("server", [""])[0], params.get("port", [""])[0], params.get("secret", [""])[0]
        if s and p and sec:
            norm = f"https://t.me/proxy?server={s}&port={p}&secret={sec}"
            if norm not in valid_links:
                valid_links.append(norm)

    raw_pattern = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b):(\d{2,5}):([a-fA-F0-9]{32,64}|ee[a-fA-F0-9]+|dd[a-fA-F0-9]+)', re.IGNORECASE)
    for s, p, sec in raw_pattern.findall(text):
        norm = f"https://t.me/proxy?server={s}&port={p}&secret={sec}"
        if norm not in valid_links:
            valid_links.append(norm)

    return valid_links

def build_channel_keyboard(links: list[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    count = len(links)
    row_size = 3 if count >= 3 else (2 if count == 2 else 1)
    buttons = [types.InlineKeyboardButton(text="Connect ↗", url=l) for l in links]
    for i in range(0, count, row_size):
        markup.row(*buttons[i:i + row_size])
    return markup

def get_main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("📢 Kanala Post Ibermek"), types.KeyboardButton("🎨 Post Redaktory"))
    markup.add(types.KeyboardButton("⚡ Tizlik (Ping)"), types.KeyboardButton("⚙️ Kanaly Sazlamak"))
    markup.add(types.KeyboardButton("📊 24/7 Status"), types.KeyboardButton("ℹ️ Gollanma"))
    return markup

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def check_admin(message_or_query) -> bool:
    user_id = message_or_query.from_user.id
    if user_id != ADMIN_ID:
        if isinstance(message_or_query, types.CallbackQuery):
            bot.answer_callback_query(message_or_query.id, "⛔ Giriş gadagan!", show_alert=True)
        else:
            bot.reply_to(message_or_query, "⛔ <b>Giriş gadagan edildi!</b> Bu bot diňe administratoryň özi üçin goralandyr.")
        return False
    return True

try:
    bot.set_my_commands([
        types.BotCommand("start", "Baş menýuny we düwmeleri açmak"),
        types.BotCommand("post", "Kanala MTProxy postuny ugratmak"),
        types.BotCommand("editor", "Post redaktory (surat, tekst, hesteg üýtgetmek)"),
        types.BotCommand("setchannel", "Post iberiljek kanaly sazlamak"),
        types.BotCommand("status", "24/7 iş wagty we serwer ýagdaýy"),
        types.BotCommand("ping", "Botuň jogap tizligini barlamak"),
    ])
except Exception:
    pass

def build_editor_markup():
    cfg = load_post_config()
    has_custom = cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🖼 Galereýadan Täze Surat Ýüklemek", callback_data="ed_upload_photo"))
    markup.row(
        types.InlineKeyboardButton("✏️ Esasy Tekst", callback_data="ed_edit_text"),
        types.InlineKeyboardButton("💎 Kanal Linki", callback_data="ed_edit_channel")
    )
    markup.row(
        types.InlineKeyboardButton("🥇 Aşaky Şygar", callback_data="ed_edit_slogan"),
        types.InlineKeyboardButton("🏷 Heştegler", callback_data="ed_edit_hashtags")
    )
    markup.row(types.InlineKeyboardButton("💠 Bezeg Çyzygy (Ornaments)", callback_data="ed_choose_ornament"))
    markup.row(
        types.InlineKeyboardButton("👁 Posty Syn Etmek (Preview)", callback_data="ed_preview_post"),
        types.InlineKeyboardButton("🔄 Standarta Gaýtar", callback_data="ed_reset_defaults")
    )
    if has_custom:
        markup.row(types.InlineKeyboardButton("🗑 Ýüklenen Suraty Aýyr (Standarta Gaýt)", callback_data="ed_remove_custom_photo"))
    return markup

def send_editor_panel(chat_id, message_id=None):
    cfg = load_post_config()
    ornament_key = cfg.get("ornament_style", "default")
    ornament_preview = ORNAMENT_STYLES.get(ornament_key, "════════ ◖⚚◗ ════════") or "(Arakesmesiz / Ýönekeý)"
    has_custom = cfg.get("use_custom_banner") and os.path.exists(CUSTOM_BANNER_PATH)
    photo_status = "🟢 Galereýaňyzdan Ýüklenen Surat" if has_custom else "🔵 16:9 Standart Kiber Banner"

    text = (
        "🎨 <b>Ghost Protocol Post Redaktory (Çudo Panel)</b>\n\n"
        "Şu wagtky bellenen post sazlamalary:\n"
        f"• <b>Surat:</b> {photo_status}\n"
        f"• <b>Esasy Tekst:</b> <i>{cfg.get('post_text')}</i>\n"
        f"• <b>Kanal Salgysy:</b> <code>{cfg.get('channel_mention')}</code>\n"
        f"• <b>Aşaky Şygar:</b> <i>{cfg.get('slogan')}</i>\n"
        f"• <b>Bezeg Çyzygy:</b> <code>{ornament_preview}</code>\n"
        f"• <b>Heştegler:</b> <code>{len(cfg.get('hashtags', '').split())} sany heşteg</code>\n\n"
        "👇 <i>Üýtgetmek isleýän zadyňyzyň düwmesine basyň:</i>"
    )

    markup = build_editor_markup()
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="HTML")
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=["start", "menu"])
def cmd_start(message: types.Message):
    if not check_admin(message):
        return
    cfg = load_post_config()
    welcome_text = (
        "🛡️ <b>Ghost Protocol Dolandyryş Paneli (Çudo Edition)</b>\n\n"
        "✨ <b>Täze:</b> <i>Post Redaktory arkaly suraty, teksti, heştegleri we nagşlary göni botuň içinden üýtgedip bilersiňiz!</i>\n\n"
        f"📢 <b>Häzirki Kanal:</b> <code>{cfg.get('channel_mention')}</code> (Taýýar)\n"
        f"👤 <b>Admin ID:</b> <code>{ADMIN_ID}</code> (Doly Goralan)\n"
        "⚡ <b>Ýagdaýy:</b> 7/48 Oýa, düwmä basan badyňyza jogap bermäge taýýar!"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text in ["🎨 Post Redaktory", "/editor"])
def handle_editor_command(message: types.Message):
    if not check_admin(message):
        return
    send_editor_panel(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "⚡ Tizlik (Ping)" or msg.text == "/ping")
def handle_ping(message: types.Message):
    if not check_admin(message):
        return
    t0 = time.time()
    msg = bot.reply_to(message, "⚡ <i>Barlanýar...</i>")
    dt = round((time.time() - t0) * 1000, 1)
    bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚡ <b>Bot Oýa we Tiz Jogap Berýär!</b>\n\n• Jogap tizligi: <b>{dt} ms</b>\n• Ýagdaýy: 🟢 7/48 Durman Işleýär!", parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "📊 24/7 Status" or msg.text == "/status")
def handle_status(message: types.Message):
    if not check_admin(message):
        return
    uptime = int(time.time() - start_time)
    h, rem = divmod(uptime, 3600)
    m, s = divmod(rem, 60)
    cfg = load_post_config()
    bot.reply_to(message, f"🟢 <b>Ghost Protocol 24/7 Status</b>\n\n• <b>Admin:</b> <code>{ADMIN_ID}</code>\n• <b>Iş wagty:</b> {h} sagat, {m} minut, {s} sekunt\n• <b>Awtomatiki Oýaryjy:</b> {ping_counter} gezek oýaryldy\n• <b>Birikdirilen Kanal:</b> <code>{cfg.get('channel_mention')}</code>", reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "⚙️ Kanaly Sazlamak")
def handle_channel_menu(message: types.Message):
    if not check_admin(message):
        return
    cfg = load_post_config()
    bot.reply_to(message, f"📢 <b>Kanal Sazlamalary</b>\n\nHäzirki bellenen kanal: <code>{cfg.get('channel_mention')}</code>\n\nKanaly üýtgetmegiň 2 sany aňsat ýoly bar:\n1. Kanalyňyzdan islendik bir posty göni şu bota <b>Forward (Переслать)</b> ediň.\n2. Ýa-da buýruk ýazyň: <code>/setchannel @ghost_protocolI</code>", reply_markup=get_main_menu_keyboard())

@bot.message_handler(commands=["setchannel"])
def cmd_set_channel(message: types.Message):
    global current_channel
    if not check_admin(message):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Mysal: <code>/setchannel @ghost_protocolI</code>")
        return
    current_channel = normalize_channel(parts[1].strip())
    cfg = load_post_config()
    cfg["channel_mention"] = current_channel
    save_post_config(cfg)
    bot.reply_to(message, f"✅ <b>Kanal üstünlikli bellenildi:</b> <code>{current_channel}</code>", reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.forward_from_chat is not None)
def handle_forwarded_post(message: types.Message):
    global current_channel
    if not check_admin(message):
        return
    chat = message.forward_from_chat
    current_channel = f"@{chat.username}" if chat.username else str(chat.id)
    cfg = load_post_config()
    cfg["channel_mention"] = current_channel
    save_post_config(cfg)
    bot.reply_to(message, f"🎉 <b>Kanal derrew tanaldy we bellenildi!</b>\n\n• Ady: <b>{chat.title}</b>\n• Salgysy: <code>{current_channel}</code>\n\nIndi ugradýan MTProxy postlaryňyz göni şu kanala iberiler!", reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Gollanma")
def handle_help(message: types.Message):
    if not check_admin(message):
        return
    bot.reply_to(message, "ℹ️ <b>Ghost Protocol Çudo Bot Gollanmasy</b>\n\n1. <b>Surat ýüklemek:</b> Galereýaňyzdan islendik suraty göni şu söhbete ugradyň, bot ony derrew täze post suraty edip beller!\n2. <b>Post Redaktory:</b> '🎨 Post Redaktory' düwmesine basyp, teksti, heştegleri we nagşlary aňsatlyk bilen sazlaň.\n3. <b>Kanala Post Ibermek:</b> MTProxy linkleriňizi şu ýere ugradyň, bot aşagynda '🚀 Kanala Göni Ugrat' düwmesini berer.\n4. Basan badyňyza owadan banner, heştegler we 3 sütünli Connect düwmeleri bilen kanala ugradylar!", reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "📢 Kanala Post Ibermek" or msg.text == "/post")
def handle_post_prompt(message: types.Message):
    if not check_admin(message):
        return
    bot.reply_to(message, "📥 <b>MTProxy linkleriňizi şu ýere ugradyň:</b>\n(Islendik format: https://t.me/proxy, tg://, ýa-da IP:PORT:SECRET)", reply_markup=get_main_menu_keyboard())

@bot.message_handler(content_types=["photo"])
def handle_photo_upload(message: types.Message):
    if not check_admin(message):
        return
    try:
        photo_info = message.photo[-1]
        file_info = bot.get_file(photo_info.file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)
        with open(CUSTOM_BANNER_PATH, "wb") as f:
            f.write(downloaded_bytes)

        cfg = load_post_config()
        cfg["use_custom_banner"] = True
        save_post_config(cfg)
        user_states.pop(message.from_user.id, None)

        preview_markup = types.InlineKeyboardMarkup()
        preview_markup.row(
            types.InlineKeyboardButton("👁 Posty Syn Etmek (Preview)", callback_data="ed_preview_post"),
            types.InlineKeyboardButton("🎨 Post Redaktoryna Gaýt", callback_data="ed_open_panel")
        )
        bot.reply_to(message, "🎉 <b>Ajaýyp! Täze surat galereýadan üstünlikli ýüklenildi!</b>\n\nIndi kanala ugradyljak ähli MTProxy postlaryňyzda şu surat peýdalanylar.\nGörünüşini barlamak üçin aşakdaky düwmä basyň:", reply_markup=preview_markup)
    except Exception as e:
        logger.error(f"Surat ýüklemekde säwlik: {e}")
        bot.reply_to(message, f"❌ <b>Suraty ýükläp bolmady:</b> <code>{e}</code>")

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_any_text(message: types.Message):
    if not check_admin(message):
        return
    user_id = message.from_user.id
    current_state = user_states.get(user_id)
    text = message.text.strip()

    if current_state:
        cfg = load_post_config()
        if current_state == "waiting_for_text":
            cfg["post_text"] = text
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, f"✅ <b>Esasy tekst üstünlikli üýtgedildi!</b>\n\nTäze tekst: <i>{text}</i>")
            send_editor_panel(message.chat.id)
            return
        elif current_state == "waiting_for_channel":
            normalized = normalize_channel(text)
            cfg["channel_mention"] = normalized
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, f"✅ <b>Kanal salgysy üstünlikli üýtgedildi:</b> <code>{normalized}</code>")
            send_editor_panel(message.chat.id)
            return
        elif current_state == "waiting_for_slogan":
            cfg["slogan"] = text
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, f"✅ <b>Aşaky şygar üstünlikli üýtgedildi!</b>\n\nTäze şygar: <i>{text}</i>")
            send_editor_panel(message.chat.id)
            return
        elif current_state == "waiting_for_hashtags":
            cfg["hashtags"] = text
            save_post_config(cfg)
            user_states.pop(user_id, None)
            bot.reply_to(message, "✅ <b>Heştegler üstünlikli üýtgedildi!</b>")
            send_editor_panel(message.chat.id)
            return
        elif current_state == "waiting_for_photo":
            bot.reply_to(message, "⚠️ <b>Siz tekst däl-de, SURAT ibermeli!</b>\nGalereýaňyzdan suraty saýlap iberiň ýa-da ýatyrmak üçin aşakdaky düwmä basyň.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel")))
            return

    links = parse_mtproxy_links(text)
    if not links:
        bot.reply_to(message, "⚠️ <b>Hiç hili MTProxy tapylmady!</b>\nLinkiňizde <code>server</code>, <code>port</code> we <code>secret</code> barlygyny barlaň ýa-da aşakdaky menýudan peýdalanyň.", reply_markup=get_main_menu_keyboard())
        return

    pending_posts[user_id] = links
    cfg = load_post_config()
    target_channel = cfg.get("channel_mention", DEFAULT_CHANNEL)
    confirm_markup = types.InlineKeyboardMarkup()
    confirm_markup.row(types.InlineKeyboardButton("🚀 Kanala Göni Ugrat", callback_data="do_post_channel"), types.InlineKeyboardButton("❌ Ýatyr", callback_data="do_cancel_post"))
    confirm_markup.row(types.InlineKeyboardButton("🎨 Post Dizaýnyny Redaktirle", callback_data="ed_open_panel"))
    bot.reply_to(message, f"✅ <b>{len(links)} sany MTProxy üstünlikli tapyldy!</b>\n\n📢 <b>Ugradyljak Kanal:</b> <code>{target_channel}</code>\n Düwmeler: <b>Connect ↗ ({len(links)} sany, 3 sütünli)</b>\n\nPosty kanala paýlaşmak üçin aşakdaky düwmä basyň:", reply_markup=confirm_markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: types.CallbackQuery):
    if not check_admin(call):
        return
    user_id = call.from_user.id
    data = call.data

    if data == "do_cancel_post":
        pending_posts.pop(user_id, None)
        bot.edit_message_text("❌ <b>Post ugratmak ýatyryldy.</b>", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, "Ýatyryldy")
        return
    if data == "ed_open_panel":
        send_editor_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    if data == "ed_cancel":
        user_states.pop(user_id, None)
        send_editor_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Ýatyryldy")
        return
    if data == "ed_upload_photo":
        user_states[user_id] = "waiting_for_photo"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text("📸 <b>Galereýaňyzdan täze suraty saýlap şu söhbete ugradyň!</b>\n\nBot ony derrew kabul edip, indiki postlaryňyz üçin esasy banner edip beller.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=cancel_markup)
        bot.answer_callback_query(call.id)
        return
    if data == "ed_remove_custom_photo":
        cfg = load_post_config()
        cfg["use_custom_banner"] = False
        save_post_config(cfg)
        bot.answer_callback_query(call.id, "Standart bannere geçildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return
    if data == "ed_edit_text":
        user_states[user_id] = "waiting_for_text"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text("✏️ <b>Postuň esasy tekstini täze görnüşde ýazyp ugradyň:</b>\n\n<i>Häzirki mysal: Используйте Telegram без VPN, нажмите кнопку (connect)</i>", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=cancel_markup)
        bot.answer_callback_query(call.id)
        return
    if data == "ed_edit_channel":
        user_states[user_id] = "waiting_for_channel"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text("💎 <b>Postda görünjek kanal adyny ýazyň:</b>\n\n<i>Mysal: @ghost_protocolI ýa-da https://t.me/ghost_protocolI</i>", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=cancel_markup)
        bot.answer_callback_query(call.id)
        return
    if data == "ed_edit_slogan":
        user_states[user_id] = "waiting_for_slogan"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text("🥇 <b>Aşaky şygary ýazyp ugradyň:</b>\n\n<i>Häzirki mysal: Самый быстрый канал прокси в Туркменистане</i>", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=cancel_markup)
        bot.answer_callback_query(call.id)
        return
    if data == "ed_edit_hashtags":
        user_states[user_id] = "waiting_for_hashtags"
        cancel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ Ýatyr", callback_data="ed_cancel"))
        bot.edit_message_text("🏷 <b>Postuň aşagyndaky heştegleri ugradyň:</b>\n\n<i>Mysal: #ghostprotocol #proxy #freeproxy #mtproxy #socks5 #vpn #turkmenistan</i>", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=cancel_markup)
        bot.answer_callback_query(call.id)
        return
    if data == "ed_choose_ornament":
        ornament_markup = types.InlineKeyboardMarkup()
        for key, name in ORNAMENT_NAMES.items():
            ornament_markup.row(types.InlineKeyboardButton(name, callback_data=f"set_orn_{key}"))
        ornament_markup.row(types.InlineKeyboardButton("⬅️ Yza (Redaktora)", callback_data="ed_open_panel"))
        bot.edit_message_text("💠 <b>Postdaky bezeg çyzygynyň (Ornament) stilini saýlaň:</b>\n\nBu çyzyk kanalyň adynyň ýokarsynda we aşagynda owadan bolup görünýär.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ornament_markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("set_orn_"):
        orn_key = data.replace("set_orn_", "")
        cfg = load_post_config()
        cfg["ornament_style"] = orn_key
        save_post_config(cfg)
        bot.answer_callback_query(call.id, "Bezeg stili bellenildi!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return
    if data == "ed_reset_defaults":
        save_post_config(DEFAULT_POST_CONFIG.copy())
        bot.answer_callback_query(call.id, "Standart dizaýna gaýtaryldy!")
        send_editor_panel(call.message.chat.id, call.message.message_id)
        return
    if data == "ed_preview_post":
        caption = generate_channel_caption()
        banner_path = get_active_banner_path()
        dummy_markup = types.InlineKeyboardMarkup()
        dummy_markup.row(
            types.InlineKeyboardButton("Connect 1 ↗", url="https://t.me/proxy?server=127.0.0.1&port=443&secret=ee00"),
            types.InlineKeyboardButton("Connect 2 ↗", url="https://t.me/proxy?server=127.0.0.1&port=443&secret=ee00"),
            types.InlineKeyboardButton("Connect 3 ↗", url="https://t.me/proxy?server=127.0.0.1&port=443&secret=ee00")
        )
        try:
            if banner_path and os.path.exists(banner_path):
                with open(banner_path, "rb") as photo:
                    bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption=f"👁 <b>[DESLAPKY SYN / PREVIEW]</b>\n\n{caption}", reply_markup=dummy_markup, parse_mode="HTML")
            else:
                bot.send_message(chat_id=call.message.chat.id, text=f"👁 <b>[DESLAPKY SYN / PREVIEW]</b>\n\n{caption}", reply_markup=dummy_markup, parse_mode="HTML")
            bot.answer_callback_query(call.id, "Syn ugradyldy!")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Syn säwligi: {e}", show_alert=True)
        return
    if data == "do_post_channel":
        links = pending_posts.get(user_id, [])
        if not links:
            bot.answer_callback_query(call.id, "⚠️ Linkler tapylmady!", show_alert=True)
            return
        cfg = load_post_config()
        target = normalize_channel(cfg.get("channel_mention", DEFAULT_CHANNEL))
        keyboard = build_channel_keyboard(links)
        caption = generate_channel_caption(target)
        banner_path = get_active_banner_path()

        try:
            if banner_path and os.path.exists(banner_path):
                with open(banner_path, "rb") as photo:
                    bot.send_photo(chat_id=target, photo=photo, caption=caption, reply_markup=keyboard, parse_mode="HTML")
            else:
                bot.send_message(chat_id=target, text=caption, reply_markup=keyboard, parse_mode="HTML")

            bot.edit_message_text(f"🚀 <b>Post üstünlikli kanala ugradyldy!</b>\n\n• Kanal: <code>{target}</code>\n• Goşulan Connect düwmeleri: <b>{len(links)} sany (3 sütün)</b>\n• Ulanylan surat: <b>{'Ýüklenen Surat' if cfg.get('use_custom_banner') else '16:9 Kiber Banner'}</b>", chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.answer_callback_query(call.id, "🚀 Ugradyldy!")
            del pending_posts[user_id]
        except Exception as e:
            bot.answer_callback_query(call.id, f"Säwlik: {e}", show_alert=True)
            bot.send_message(call.message.chat.id, f"❌ <b>Post ugradyp bolmady:</b> <code>{e}</code>\n\n<i>Bellik: Botuň <code>{target}</code> kanalyňyzda Administrator bolmagy hökmanydyr!</i>")

def main():
    logger.info("Ghost Protocol Çudo Bot işe girizilýär...")
    threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=auto_keep_alive_pinger, daemon=True).start()
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=10, skip_pending=True)
        except Exception as exc:
            logger.error(f"Polling säwligi: {exc}")
            time.sleep(5)

if __name__ == "__main__":
    main()
